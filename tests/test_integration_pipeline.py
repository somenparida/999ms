"""Integration tests for Warehouse Sentinel: Member 1 (YOLO & ByteTrack) + Member 2 (Behavior Intelligence).

Tests:
1. SentinelPipeline initialization and component binding
2. Single-frame processing contract (annotated frame, records with behavior dict, events)
3. Data contract verification between PersonTracker and BehaviorEngine
4. End-to-end video pipeline processing, video I/O, and telemetry JSON schema validation
5. PersonTracker native execution with behavior_engine integration
6. Streaming video generator interface
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import cv2
import numpy as np
import pytest

# Ensure autonomous-vision is on path
_ROOT = Path(__file__).resolve().parent.parent
_VISION = _ROOT / "autonomous-vision"
for _p in [str(_ROOT), str(_VISION)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from detection.tracker import PersonTracker, dispatch_to_behavior_engine, to_behavior_engine_kwargs
from behavior.behavior_engine import BehaviorEngine
from behavior.schemas import BehaviorResult, BehaviorStatus, ActivityType
from pipeline.sentinel_pipeline import SentinelPipeline


@pytest.fixture(scope="module")
def shared_pipeline():
    """Instantiate a shared SentinelPipeline instance for fast testing."""
    return SentinelPipeline(
        model_path="autonomous-vision/models/yolo11n.pt",
        behavior_config="configs/behavior.yaml",
        conf_threshold=0.25,
    )


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test artifacts and clean up afterwards."""
    td = Path(tempfile.mkdtemp(prefix="test_sentinel_pipeline_"))
    yield td
    if td.exists():
        shutil.rmtree(td, ignore_errors=True)


def _create_synthetic_video(filepath: Path, num_frames: int = 5, width: int = 320, height: int = 240, fps: float = 10.0) -> Path:
    """Generate a small synthetic video for pipeline tests."""
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(filepath), fourcc, fps, (width, height))
    for i in range(num_frames):
        frame = np.full((height, width, 3), 80, dtype=np.uint8)
        # Draw a moving rectangle
        cv2.rectangle(frame, (40 + i * 4, 30), (100 + i * 4, 150), (60, 160, 240), -1)
        writer.write(frame)
    writer.release()
    return filepath


def test_pipeline_initialization(shared_pipeline):
    """Verify SentinelPipeline initializes both subcomponents correctly."""
    assert shared_pipeline.tracker is not None
    assert isinstance(shared_pipeline.tracker, PersonTracker)
    assert shared_pipeline.behavior_engine is not None
    assert isinstance(shared_pipeline.behavior_engine, BehaviorEngine)
    assert shared_pipeline.visualizer is not None


def test_data_contract_tracker_to_behavior_engine():
    """Verify raw tracking records map perfectly into BehaviorEngine.update."""
    engine = BehaviorEngine("configs/behavior.yaml")

    dummy_record: Dict[str, Any] = {
        "track_id": 101,
        "timestamp": 1.5,
        "bbox": [100.0, 120.0, 180.0, 320.0],
        "keypoints": None,
        "detection_confidence": 0.92,
        "frame_number": 15,
        "center": [140.0, 220.0],
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.92,
    }

    # Verify kwargs adapter
    kwargs = to_behavior_engine_kwargs(dummy_record)
    assert kwargs["track_id"] == 101
    assert kwargs["timestamp"] == 1.5
    assert kwargs["bbox"] == [100.0, 120.0, 180.0, 320.0]
    assert kwargs["keypoints"] is None
    assert kwargs["detection_confidence"] == 0.92

    # Verify dispatch
    res = dispatch_to_behavior_engine(engine, dummy_record)
    assert isinstance(res, BehaviorResult)
    assert res.track_id == 101
    assert res.activity in ActivityType
    assert res.status in BehaviorStatus


def test_pipeline_process_frame(shared_pipeline):
    """Verify single frame processing produces valid annotations, records, and events."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    annotated, records, events = shared_pipeline.process_frame(
        frame=frame,
        frame_number=1,
        timestamp=0.0,
        total_frames=10,
        fps=10.0,
    )

    assert annotated is not None
    assert annotated.shape == (480, 640, 3)
    assert isinstance(records, list)
    assert isinstance(events, list)


def test_pipeline_stream_video(shared_pipeline, temp_dir):
    """Verify streaming generator yields valid per-frame tuples."""
    test_video = temp_dir / "stream_test.mp4"
    _create_synthetic_video(test_video, num_frames=3, width=320, height=240, fps=10.0)

    frames_received = 0
    for frame_idx, ts, annotated, records, events in shared_pipeline.stream_video(test_video):
        frames_received += 1
        assert frame_idx == frames_received
        assert ts >= 0.0
        assert annotated.shape == (240, 320, 3)
        assert isinstance(records, list)
        assert isinstance(events, list)

    assert frames_received == 3


def test_pipeline_end_to_end_video_and_json_schema(shared_pipeline, temp_dir):
    """Verify end-to-end video pipeline creates annotated MP4 and schema-valid JSON telemetry."""
    in_video = temp_dir / "input.mp4"
    out_video = temp_dir / "output.mp4"
    out_json = temp_dir / "telemetry.json"

    num_frames = 6
    _create_synthetic_video(in_video, num_frames=num_frames, width=320, height=240, fps=10.0)

    summary = shared_pipeline.process_video(
        input_path=in_video,
        output_video_path=out_video,
        json_output_path=out_json,
    )

    # 1. Validate summary dict
    assert summary["total_frames_processed"] == num_frames
    assert summary["width"] == 320
    assert summary["height"] == 240
    assert summary["fps"] == 10.0
    assert "activity_distribution" in summary
    assert "status_distribution" in summary

    # 2. Validate output video file
    assert out_video.exists()
    cap = cv2.VideoCapture(str(out_video))
    assert cap.isOpened()
    assert int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) == 320
    assert int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) == 240
    cap.release()

    # 3. Validate JSON structure
    assert out_json.exists()
    with open(out_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "metadata" in data
    assert data["metadata"]["system"] == "Warehouse Sentinel"
    assert "summary" in data
    assert "events" in data
    assert "tracks" in data
    assert data["metadata"]["total_frames"] == num_frames


def test_person_tracker_process_video_with_behavior(temp_dir):
    """Verify Member 1 PersonTracker.process_video works seamlessly with behavior_engine."""
    tracker = PersonTracker(conf_threshold=0.25)
    engine = BehaviorEngine("configs/behavior.yaml")

    in_video = temp_dir / "input_tracker.mp4"
    out_video = temp_dir / "output_tracker.mp4"
    out_json = temp_dir / "tracks_behavior.json"

    _create_synthetic_video(in_video, num_frames=4, width=320, height=240, fps=10.0)

    summary = tracker.process_video(
        input_path=in_video,
        output_video_path=out_video,
        json_output_path=out_json,
        behavior_engine=engine,
    )

    assert summary["total_frames_processed"] == 4
    assert out_video.exists()
    assert out_json.exists()

    with open(out_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["metadata"]["behavior_engine_enabled"] is True
    assert "behavior_events" in data
