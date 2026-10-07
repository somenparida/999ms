"""Warehouse Sentinel - Integrated Video Intelligence Pipeline.

Connects Member 1 (YOLO11n + ByteTrack) with Member 2 (Behavior Intelligence Engine)
into a unified real-time video intelligence pipeline.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

import cv2
import numpy as np

# Ensure project root and autonomous-vision are in sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_VISION_ROOT = _PROJECT_ROOT / "autonomous-vision"

for _p in [str(_PROJECT_ROOT), str(_VISION_ROOT)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from detection.tracker import PersonTracker, dispatch_to_behavior_engine, to_behavior_engine_kwargs
from behavior.behavior_engine import BehaviorEngine
from behavior.visualizer import BehaviorVisualizer
from behavior.schemas import BehaviorResult, BehaviorStatus


class SentinelPipeline:
    """Integrated pipeline bridging Member 1 (Detection & Tracking) and Member 2 (Behavior Intelligence)."""

    def __init__(
        self,
        model_path: Union[str, Path] = "models/yolo11n.pt",
        behavior_config: Optional[Union[str, Path]] = None,
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        tracker_config: str = "bytetrack.yaml",
        device: Optional[str] = None,
    ) -> None:
        """Initialize SentinelPipeline.

        Args:
            model_path: Path to YOLO weights.
            behavior_config: Path to behavior YAML config (default: configs/behavior.yaml).
            conf_threshold: Minimum detection confidence score.
            iou_threshold: NMS IoU threshold.
            tracker_config: Tracker configuration YAML.
            device: Computation device ('cpu', 'cuda', etc.).
        """
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

        # Resolve model path
        self.model_path = Path(model_path)
        if not self.model_path.is_file():
            candidate = _VISION_ROOT / "models" / self.model_path.name
            if candidate.is_file():
                self.model_path = candidate
            else:
                candidate2 = _PROJECT_ROOT / self.model_path.name
                if candidate2.is_file():
                    self.model_path = candidate2

        # Resolve behavior config
        if behavior_config is None:
            default_cfg = _PROJECT_ROOT / "configs" / "behavior.yaml"
            self.behavior_config = str(default_cfg) if default_cfg.is_file() else None
        else:
            self.behavior_config = str(behavior_config)

        # Initialize subcomponents
        self.tracker = PersonTracker(
            model_path=str(self.model_path),
            conf_threshold=self.conf_threshold,
            iou_threshold=self.iou_threshold,
            tracker_config=tracker_config,
            device=device,
        )
        self.behavior_engine = BehaviorEngine(self.behavior_config)
        self.visualizer = BehaviorVisualizer()

    def reset(self) -> None:
        """Reset internal tracker and behavior state."""
        self.behavior_engine.reset()

    def process_frame(
        self,
        frame: np.ndarray,
        frame_number: int = 1,
        timestamp: float = 0.0,
        total_frames: int = 1,
        fps: float = 30.0,
    ) -> Tuple[np.ndarray, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Process a single frame through tracking and behavior analysis.

        Args:
            frame: Raw BGR frame.
            frame_number: Current 1-based frame index.
            timestamp: Elapsed video timestamp in seconds.
            total_frames: Total video frame count.
            fps: Video frames per second.

        Returns:
            Tuple containing:
                - annotated_frame: BGR frame with combined HUD and behavioral diagnostic overlays.
                - enriched_records: List of tracking records enriched with behavior analysis.
                - frame_events: List of safety events triggered in this frame.
        """
        # 1. Member 1: Track persons
        records = self.tracker.track_frame(
            frame=frame,
            frame_number=frame_number,
            timestamp=timestamp,
            persist=True,
        )

        behavior_pairs: List[Tuple[Dict[str, Any], BehaviorResult]] = []
        frame_events: List[Dict[str, Any]] = []

        # 2. Member 2: Ingest into BehaviorEngine
        for rec in records:
            b_result: BehaviorResult = dispatch_to_behavior_engine(self.behavior_engine, rec)
            rec["behavior"] = b_result.to_dict()
            behavior_pairs.append((rec, b_result))

            if b_result.event:
                frame_events.append(b_result.event.to_dict())

        # 3. Render integrated visual overlay
        if behavior_pairs:
            annotated_frame = self.visualizer.draw_integrated_frame(
                frame=frame,
                records_with_results=behavior_pairs,
                frame_number=frame_number,
                total_frames=total_frames,
                fps=fps,
            )
        else:
            annotated_frame = self.visualizer.draw_integrated_frame(
                frame=frame,
                records_with_results=[],
                frame_number=frame_number,
                total_frames=total_frames,
                fps=fps,
            )

        return annotated_frame, records, frame_events

    def stream_video(
        self,
        video_source: Union[str, Path, int],
    ) -> Generator[Tuple[int, float, np.ndarray, List[Dict[str, Any]], List[Dict[str, Any]]], None, None]:
        """Generator yielding per-frame tracking and behavior diagnostics.

        Args:
            video_source: Path to video file or webcam index.

        Yields:
            Tuple of (frame_number, timestamp, annotated_frame, records, events).
        """
        cap = cv2.VideoCapture(video_source if isinstance(video_source, int) else str(video_source))
        if not cap.isOpened():
            raise ValueError(f"Failed to open video source: '{video_source}'.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or np.isnan(fps):
            fps = 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_num = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break
                frame_num += 1
                timestamp = (frame_num - 1) / fps

                annotated, records, events = self.process_frame(
                    frame=frame,
                    frame_number=frame_num,
                    timestamp=timestamp,
                    total_frames=total_frames if total_frames > 0 else frame_num,
                    fps=fps,
                )
                yield (frame_num, timestamp, annotated, records, events)
        finally:
            cap.release()

    def process_video(
        self,
        input_path: Union[str, Path],
        output_video_path: Optional[Union[str, Path]] = None,
        json_output_path: Optional[Union[str, Path]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, Any]:
        """Execute end-to-end video tracking and behavior intelligence pipeline.

        Args:
            input_path: Path to input video file.
            output_video_path: Destination path for annotated MP4 video.
            json_output_path: Destination path for telemetry JSON.
            progress_callback: Optional callback(current_frame, total_frames).

        Returns:
            Dictionary containing processing summary and telemetry.
        """
        src = Path(input_path)
        if not src.exists():
            raise FileNotFoundError(f"Input video file not found: '{input_path}'.")
        if not src.is_file():
            raise ValueError(f"Input path '{input_path}' is not a regular file.")

        cap = cv2.VideoCapture(str(src))
        if not cap.isOpened():
            raise ValueError(f"Failed to open video file: '{input_path}'.")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if width <= 0 or height <= 0:
            cap.release()
            raise ValueError(f"Invalid video dimensions ({width}x{height}) in '{input_path}'.")
        if fps <= 0 or np.isnan(fps):
            fps = 25.0

        # Resolve output destinations
        if output_video_path is None:
            out_dir = _PROJECT_ROOT / "output"
            out_dir.mkdir(parents=True, exist_ok=True)
            dst_video = out_dir / f"{src.stem}_sentinel.mp4"
        else:
            dst_video = Path(output_video_path)
            dst_video.parent.mkdir(parents=True, exist_ok=True)

        if json_output_path is None:
            out_dir = _PROJECT_ROOT / "output"
            out_dir.mkdir(parents=True, exist_ok=True)
            dst_json = out_dir / f"{src.stem}_sentinel.json"
        else:
            dst_json = Path(json_output_path)
            dst_json.parent.mkdir(parents=True, exist_ok=True)

        # Initialize VideoWriter
        writer = self._create_video_writer(dst_video, fps, (width, height))
        if writer is None or not writer.isOpened():
            cap.release()
            raise RuntimeError(f"Failed to open VideoWriter for destination: '{dst_video}'.")

        all_records: List[Dict[str, Any]] = []
        all_events: List[Dict[str, Any]] = []
        unique_track_ids: set[int] = set()
        activity_distribution: Dict[str, int] = {}
        status_distribution: Dict[str, int] = {
            "NORMAL": 0,
            "POTENTIALLY_UNUSUAL": 0,
            "ABNORMAL": 0,
            "UNKNOWN": 0,
        }

        frames_processed = 0
        start_time = time.time()

        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                frames_processed += 1
                timestamp = (frames_processed - 1) / fps

                annotated, frame_records, frame_events = self.process_frame(
                    frame=frame,
                    frame_number=frames_processed,
                    timestamp=timestamp,
                    total_frames=total_frames if total_frames > 0 else frames_processed,
                    fps=fps,
                )

                writer.write(annotated)

                for r in frame_records:
                    unique_track_ids.add(r["track_id"])
                    all_records.append(r)
                    if "behavior" in r:
                        act = r["behavior"].get("activity", "UNKNOWN")
                        stat = r["behavior"].get("status", "UNKNOWN")
                        activity_distribution[act] = activity_distribution.get(act, 0) + 1
                        status_distribution[stat] = status_distribution.get(stat, 0) + 1

                all_events.extend(frame_events)

                if progress_callback:
                    progress_callback(frames_processed, total_frames)

        finally:
            cap.release()
            writer.release()

        elapsed = time.time() - start_time
        avg_fps = frames_processed / elapsed if elapsed > 0 else 0.0

        if frames_processed == 0:
            raise ValueError(f"Video file '{input_path}' contains 0 readable frames.")

        # Build comprehensive JSON payload for Member 3/4
        json_payload = {
            "metadata": {
                "system": "Warehouse Sentinel",
                "subsystems": ["Member 1 (YOLO11 + ByteTrack)", "Member 2 (Behavior Intelligence)"],
                "video_source": str(src.resolve()),
                "tracker": "ByteTrack",
                "model": str(self.model_path.name),
                "width": width,
                "height": height,
                "fps": round(fps, 2),
                "total_frames": frames_processed,
                "elapsed_seconds": round(elapsed, 2),
                "processing_fps": round(avg_fps, 2),
            },
            "summary": {
                "total_records": len(all_records),
                "unique_person_count": len(unique_track_ids),
                "unique_track_ids": sorted(list(unique_track_ids)),
                "total_safety_events": len(all_events),
                "activity_distribution": activity_distribution,
                "status_distribution": status_distribution,
            },
            "events": all_events,
            "tracks": all_records,
        }

        with open(dst_json, "w", encoding="utf-8") as f:
            json.dump(json_payload, f, indent=2)

        return {
            "input_path": str(src.resolve()),
            "output_video_path": str(dst_video.resolve()),
            "json_output_path": str(dst_json.resolve()),
            "width": width,
            "height": height,
            "fps": fps,
            "total_frames_processed": frames_processed,
            "unique_person_count": len(unique_track_ids),
            "unique_track_ids": sorted(list(unique_track_ids)),
            "total_tracking_records": len(all_records),
            "total_safety_events": len(all_events),
            "activity_distribution": activity_distribution,
            "status_distribution": status_distribution,
            "elapsed_seconds": round(elapsed, 2),
            "processing_fps": round(avg_fps, 2),
            "events": all_events,
            "tracks": all_records,
        }

    @staticmethod
    def _create_video_writer(
        output_path: Path,
        fps: float,
        frame_size: Tuple[int, int],
    ) -> Optional[cv2.VideoWriter]:
        """Attempt to instantiate VideoWriter with compatible video codecs."""
        codecs = ["mp4v", "avc1", "XVID", "MJPG"]
        for codec in codecs:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            writer = cv2.VideoWriter(str(output_path), fourcc, fps, frame_size)
            if writer.isOpened():
                return writer
            writer.release()
        return None
