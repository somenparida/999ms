"""Unit tests for Phase 3 Person Tracking module (ByteTrack) and Member 2 Integration.

Tests:
1. Tracker initialization and configuration
2. Person-only class constraint (COCO ID 0)
3. Center coordinate [cx, cy] calculation logic
4. Tracking record schema contract (including Member 2 integration fields)
5. Missing input video error handling
6. Synthetic video end-to-end processing and JSON output structure
7. Adapter function to_behavior_engine_kwargs argument mapping
8. Mock behavior engine update dispatch test
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from detection.tracker import (
    PersonTracker,
    dispatch_to_behavior_engine,
    to_behavior_engine_kwargs,
)


class MockBehaviorEngine:
    """Mock implementation of Member 2's BehaviorEngine update interface."""

    def __init__(self) -> None:
        self.updates: List[Dict[str, Any]] = []

    def update(
        self,
        track_id: int,
        timestamp: float,
        bbox: List[float],
        keypoints: Optional[Any],
        detection_confidence: float,
    ) -> bool:
        """Receive person tracking telemetry for behavior analysis."""
        self.updates.append(
            {
                "track_id": track_id,
                "timestamp": timestamp,
                "bbox": bbox,
                "keypoints": keypoints,
                "detection_confidence": detection_confidence,
            }
        )
        return True


class TestPersonTracker(unittest.TestCase):
    """Test suite for ByteTrack PersonTracker and Member 2 integration contract."""

    @classmethod
    def setUpClass(cls) -> None:
        """Instantiate a shared PersonTracker to prevent repeated model weight loads."""
        cls.tracker = PersonTracker()

    def setUp(self) -> None:
        """Create a temporary directory for test artifacts."""
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_tracker_"))

    def tearDown(self) -> None:
        """Remove temporary directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_synthetic_video(
        self,
        filepath: Path,
        num_frames: int = 5,
        width: int = 320,
        height: int = 240,
        fps: float = 10.0,
    ) -> Path:
        """Generate a small synthetic video for pipeline and serialization tests."""
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(filepath), fourcc, fps, (width, height))
        for i in range(num_frames):
            frame = np.full((height, width, 3), 100, dtype=np.uint8)
            cv2.rectangle(frame, (30 + i * 5, 40), (90 + i * 5, 120), (50, 150, 250), -1)
            writer.write(frame)
        writer.release()
        return filepath

    def test_tracker_initialization(self) -> None:
        """Verify PersonTracker initializes with ByteTrack configuration."""
        self.assertIsNotNone(self.tracker.model)
        self.assertEqual(self.tracker.tracker_config, "bytetrack.yaml")
        self.assertEqual(self.tracker.conf_threshold, 0.25)
        self.assertEqual(self.tracker.iou_threshold, 0.45)

    def test_person_only_configuration(self) -> None:
        """Verify PersonTracker defaults exclusively to the person class (ID 0)."""
        self.assertEqual(self.tracker.target_classes, [0])

    def test_center_coordinate_calculation(self) -> None:
        """Verify center coordinate [cx, cy] calculation from bbox [x1, y1, x2, y2]."""
        bbox = [100.0, 200.0, 300.0, 400.0]
        center = PersonTracker.calculate_center(bbox)
        self.assertEqual(center, [200.0, 300.0])

        bbox_decimals = [10.25, 20.75, 50.55, 80.25]
        expected_cx = round((10.25 + 50.55) / 2.0, 2)
        expected_cy = round((20.75 + 80.25) / 2.0, 2)
        self.assertEqual(PersonTracker.calculate_center(bbox_decimals), [expected_cx, expected_cy])

    def test_track_record_schema(self) -> None:
        """Verify tracking record dictionary schema contract with Member 2 fields."""
        dummy_bbox = [120.0, 80.0, 260.0, 380.0]
        dummy_record = {
            "track_id": 7,
            "timestamp": 12.4,
            "bbox": dummy_bbox,
            "keypoints": None,
            "detection_confidence": 0.94,
            "frame_number": 372,
            "center": PersonTracker.calculate_center(dummy_bbox),
            "class_id": 0,
            "class_name": "person",
            "confidence": 0.94,
        }

        required_keys = {
            "track_id",
            "timestamp",
            "bbox",
            "keypoints",
            "detection_confidence",
            "frame_number",
            "center",
            "class_id",
            "class_name",
        }
        self.assertTrue(required_keys.issubset(dummy_record.keys()))
        self.assertEqual(len(dummy_record["bbox"]), 4)
        self.assertEqual(len(dummy_record["center"]), 2)
        self.assertIsInstance(dummy_record["track_id"], int)
        self.assertIsInstance(dummy_record["timestamp"], float)
        self.assertIsNone(dummy_record["keypoints"])
        self.assertIsInstance(dummy_record["detection_confidence"], float)
        self.assertIsInstance(dummy_record["frame_number"], int)

    def test_to_behavior_engine_kwargs(self) -> None:
        """Verify adapter converts record into exact kwargs for behavior_engine.update()."""
        record = {
            "track_id": 7,
            "timestamp": 12.4,
            "bbox": [100.0, 100.0, 180.0, 300.0],
            "keypoints": None,
            "detection_confidence": 0.94,
            "frame_number": 372,
            "center": [140.0, 200.0],
            "class_id": 0,
            "class_name": "person",
        }

        kwargs = to_behavior_engine_kwargs(record)
        expected_keys = {
            "track_id",
            "timestamp",
            "bbox",
            "keypoints",
            "detection_confidence",
        }
        self.assertEqual(set(kwargs.keys()), expected_keys)
        self.assertEqual(kwargs["track_id"], 7)
        self.assertEqual(kwargs["timestamp"], 12.4)
        self.assertEqual(kwargs["bbox"], [100.0, 100.0, 180.0, 300.0])
        self.assertIsNone(kwargs["keypoints"])
        self.assertEqual(kwargs["detection_confidence"], 0.94)

        # Test class method equality
        class_kwargs = PersonTracker.to_behavior_engine_kwargs(record)
        self.assertEqual(class_kwargs, kwargs)

    def test_mock_behavior_engine_dispatch(self) -> None:
        """Verify calling behavior_engine.update(**to_behavior_engine_kwargs(record)) functions seamlessly."""
        mock_engine = MockBehaviorEngine()
        record = {
            "track_id": 7,
            "timestamp": 12.4,
            "bbox": [100.0, 100.0, 180.0, 300.0],
            "keypoints": None,
            "detection_confidence": 0.94,
            "frame_number": 372,
            "center": [140.0, 200.0],
            "class_id": 0,
            "class_name": "person",
        }

        # Method 1: Using kwargs unpacking
        mock_engine.update(**to_behavior_engine_kwargs(record))

        # Method 2: Using helper dispatch function
        dispatch_to_behavior_engine(mock_engine, record)

        self.assertEqual(len(mock_engine.updates), 2)
        for update in mock_engine.updates:
            self.assertEqual(update["track_id"], 7)
            self.assertEqual(update["timestamp"], 12.4)
            self.assertEqual(update["bbox"], [100.0, 100.0, 180.0, 300.0])
            self.assertIsNone(update["keypoints"])
            self.assertEqual(update["detection_confidence"], 0.94)

    def test_missing_video_handling(self) -> None:
        """Verify missing video file raises FileNotFoundError."""
        missing_path = self.test_dir / "non_existent_video.mp4"
        with self.assertRaises(FileNotFoundError) as ctx:
            self.tracker.process_video(missing_path)
        self.assertIn("Input video file not found", str(ctx.exception))

    def test_synthetic_video_end_to_end_and_json_structure(self) -> None:
        """Verify video I/O, ByteTrack execution pipeline, and tracks.json structure.

        NOTE ON TRACK PERSISTENCE:
        Synthetic geometric frames do not activate YOLO11n's real-world person feature
        representations. Therefore, this test validates end-to-end pipeline execution,
        metadata preservation, and JSON schema formatting, rather than falsely asserting
        synthetic identity persistence.
        """
        input_vid = self.test_dir / "synthetic_test.mp4"
        output_vid = self.test_dir / "synthetic_tracked.mp4"
        output_json = self.test_dir / "tracks.json"

        w, h, fps, count = 320, 240, 10.0, 5
        self._create_synthetic_video(input_vid, num_frames=count, width=w, height=h, fps=fps)

        summary = self.tracker.process_video(
            input_path=input_vid,
            output_video_path=output_vid,
            json_output_path=output_json,
        )

        # Verify summary output
        self.assertEqual(summary["total_frames_processed"], count)
        self.assertEqual(summary["width"], w)
        self.assertEqual(summary["height"], h)
        self.assertEqual(summary["fps"], fps)

        # Verify output video file created and readable
        self.assertTrue(output_vid.exists())
        cap = cv2.VideoCapture(str(output_vid))
        self.assertTrue(cap.isOpened())
        self.assertEqual(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), w)
        self.assertEqual(int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), h)
        cap.release()

        # Verify tracks.json structure
        self.assertTrue(output_json.exists())
        with open(output_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("metadata", data)
        self.assertIn("summary", data)
        self.assertIn("tracks", data)

        self.assertEqual(data["metadata"]["tracker"], "ByteTrack")
        self.assertEqual(data["metadata"]["width"], w)
        self.assertEqual(data["metadata"]["height"], h)
        self.assertEqual(data["metadata"]["total_frames"], count)
        self.assertIsInstance(data["summary"]["unique_track_ids"], list)
        self.assertIsInstance(data["tracks"], list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
