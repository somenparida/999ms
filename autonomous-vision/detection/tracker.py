"""Multi-Object Person Tracking Module for Autonomous Vision & Behaviour Understanding System.

Member 1 Module - Phase 3:
- Detects persons using YOLO11n
- Multi-object tracking with persistent track IDs using Ultralytics ByteTrack integration
- Formats tracking records with bbox, center, confidence, track_id, timestamp, and frame_number
- Writes annotated video with Person IDs and HUD overlay
- Exports tracking telemetry to JSON (data/output/tracks.json)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from ultralytics import YOLO

from detection.detector import YOLODetector


class PersonTracker:
    """ByteTrack-based multi-object tracker for person detection and trajectory logging."""

    def __init__(
        self,
        model_path: Union[str, Path] = "models/yolo11n.pt",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        tracker_config: str = "bytetrack.yaml",
        target_classes: Optional[List[int]] = None,
        device: Optional[str] = None,
    ) -> None:
        """Initialize the PersonTracker.

        Args:
            model_path: Path to YOLO weights.
            conf_threshold: Minimum detection confidence score.
            iou_threshold: NMS IoU threshold.
            tracker_config: Tracking configuration ('bytetrack.yaml').
            target_classes: List of class IDs to track (default: [0] for COCO 'person').
            device: Computation device ('cpu', 'cuda', etc.).
        """
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.tracker_config = tracker_config
        self.device = device

        # Default strictly to COCO class 0 ('person')
        self.target_classes = target_classes if target_classes is not None else [0]

        # Resolve model path using existing YOLODetector resolver
        self.model_path = YOLODetector._resolve_model_path(model_path)
        self.model = YOLO(self.model_path)

    @staticmethod
    def calculate_center(bbox: List[float]) -> List[float]:
        """Compute the [cx, cy] center point of a bounding box [x1, y1, x2, y2]."""
        x1, y1, x2, y2 = bbox
        cx = round((x1 + x2) / 2.0, 2)
        cy = round((y1 + y2) / 2.0, 2)
        return [cx, cy]

    @staticmethod
    def to_behavior_engine_kwargs(record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a tracking record into the argument structure expected by Member 2.

        Enables direct integration calls such as:
            behavior_engine.update(**PersonTracker.to_behavior_engine_kwargs(record))

        Args:
            record: Standard tracking record dictionary from PersonTracker.

        Returns:
            Dictionary matching the behavior_engine.update signature:
                - track_id: int
                - timestamp: float
                - bbox: [x1, y1, x2, y2]
                - keypoints: Optional[Any] (None / null if unprovided)
                - detection_confidence: float
        """
        return to_behavior_engine_kwargs(record)

    def track_frame(
        self,
        frame: np.ndarray,
        frame_number: int = 1,
        timestamp: float = 0.0,
        persist: bool = True,
        conf_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Perform YOLO + ByteTrack tracking on a single frame.

        Args:
            frame: Input image array (BGR).
            frame_number: Current 1-based frame index.
            timestamp: Elapsed video timestamp in seconds.
            persist: Whether to persist track states across frames.
            conf_threshold: Optional confidence threshold override.

        Returns:
            List of tracking records in the standardized schema:
            {
                "track_id": int,
                "timestamp": float,
                "bbox": [x1, y1, x2, y2],
                "keypoints": None,  # Reserved for pose/keypoints provider
                "detection_confidence": float,
                "frame_number": int,
                "center": [cx, cy],
                "class_id": int,
                "class_name": str,
                "confidence": float
            }
        """
        threshold = conf_threshold if conf_threshold is not None else self.conf_threshold

        results = self.model.track(
            source=frame,
            persist=persist,
            tracker=self.tracker_config,
            classes=self.target_classes,
            conf=threshold,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False,
        )

        records: List[Dict[str, Any]] = []

        if not results:
            return records

        first_res = results[0]
        boxes = first_res.boxes
        if boxes is None or len(boxes) == 0:
            return records

        # If ByteTrack has assigned IDs
        if boxes.id is None:
            return records

        track_ids = boxes.id.cpu().numpy().astype(int)
        xyxy_coords = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        classes = boxes.cls.cpu().numpy().astype(int)
        names = self.model.names if hasattr(self.model, "names") else {}

        for t_id, coord, conf, cls_id in zip(track_ids, xyxy_coords, confs, classes):
            bbox = [round(float(c), 2) for c in coord.tolist()]
            center = self.calculate_center(bbox)
            cls_name = names.get(cls_id, str(cls_id))
            conf_val = round(float(conf), 4)

            record: Dict[str, Any] = {
                "track_id": int(t_id),
                "timestamp": round(float(timestamp), 2),
                "bbox": bbox,
                "keypoints": None,  # Reserved for pose/keypoint estimation provider (Member 1/Pose)
                "detection_confidence": conf_val,
                "frame_number": int(frame_number),
                "center": center,
                "class_id": int(cls_id),
                "class_name": str(cls_name),
                "confidence": conf_val,  # Retained as backward-compatible alias
            }
            records.append(record)

        return records

    def annotate_frame(
        self,
        frame: np.ndarray,
        records: List[Dict[str, Any]],
        frame_number: int,
        total_frames: int,
    ) -> np.ndarray:
        """Annotate frame with persistent track bounding boxes, IDs, and HUD.

        Args:
            frame: Raw BGR frame.
            records: Tracking records for the current frame.
            frame_number: Current frame index.
            total_frames: Total video frame count.

        Returns:
            Annotated BGR frame.
        """
        annotated = frame.copy()
        h, w = annotated.shape[:2]

        for rec in records:
            t_id = rec["track_id"]
            conf = rec["confidence"]
            x1, y1, x2, y2 = [int(v) for v in rec["bbox"]]

            # Color generation seeded by track ID for visual distinction
            color = self._get_track_color(t_id)

            # Clamp coords
            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(0, min(x2, w - 1))
            y2 = max(0, min(y2, h - 1))

            # Bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Label badge: "Person ID: X | 0.94"
            label = f"Person ID: {t_id} ({conf:.2f})"
            (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            badge_y1 = max(0, y1 - lh - 8)
            badge_y2 = y1
            cv2.rectangle(
                annotated,
                (x1, badge_y1),
                (min(w, x1 + lw + 6), badge_y2),
                color,
                -1,
            )
            cv2.putText(
                annotated,
                label,
                (x1 + 3, max(lh + 2, y1 - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

            # Draw center point
            cx, cy = [int(v) for v in rec["center"]]
            cv2.circle(annotated, (cx, cy), 3, (0, 0, 255), -1)

        # Top HUD banner
        hud_text = f"Frame: {frame_number}/{total_frames} | Active Tracks: {len(records)} | Tracker: ByteTrack"
        (hw, hh), _ = cv2.getTextSize(hud_text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.rectangle(annotated, (10, 10), (20 + hw, 20 + hh + 10), (25, 25, 25), -1)
        cv2.rectangle(annotated, (10, 10), (20 + hw, 20 + hh + 10), (0, 200, 255), 1)
        cv2.putText(
            annotated,
            hud_text,
            (15, 20 + hh),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        return annotated

    @staticmethod
    def _get_track_color(track_id: int) -> Tuple[int, int, int]:
        """Generate consistent BGR color based on track ID."""
        palette = [
            (50, 220, 50),    # Bright Green
            (235, 175, 50),   # Sky Blue / Cyan
            (0, 165, 255),    # Orange
            (204, 78, 255),   # Magenta
            (255, 200, 0),    # Gold
            (0, 255, 200),    # Lime
            (180, 105, 255),  # Pink
            (255, 144, 30),   # Deep Blue
        ]
        return palette[track_id % len(palette)]

    def process_video(
        self,
        input_path: Union[str, Path],
        output_video_path: Optional[Union[str, Path]] = None,
        json_output_path: Optional[Union[str, Path]] = None,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Process video frame-by-frame with ByteTrack, producing annotated video and tracks.json.

        Args:
            input_path: Source video path.
            output_video_path: Destination for annotated tracking video.
            json_output_path: Destination for telemetry JSON (default: data/output/tracks.json).
            progress_callback: Optional callback(current_frame, total_frames).

        Returns:
            Dictionary summary with telemetry and output paths.

        Raises:
            FileNotFoundError: If input video is missing.
            ValueError: If video is unreadable or has 0 frames.
            RuntimeError: If VideoWriter fails to open.
        """
        src = Path(input_path)
        if not src.exists():
            raise FileNotFoundError(
                f"Input video file not found: '{input_path}'. Please provide a valid file path."
            )
        if not src.is_file():
            raise ValueError(
                f"Input video path '{input_path}' is not a regular file."
            )

        cap = cv2.VideoCapture(str(src))
        if not cap.isOpened():
            raise ValueError(
                f"Failed to open video file: '{input_path}'. Format may be corrupted or unsupported."
            )

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if width <= 0 or height <= 0:
            cap.release()
            raise ValueError(f"Invalid video dimensions ({width}x{height}) in '{input_path}'.")

        if fps <= 0 or np.isnan(fps):
            fps = 25.0

        project_root = Path(__file__).resolve().parent.parent

        # Resolve output video path
        if output_video_path is None:
            out_dir = project_root / "data" / "output"
            out_dir.mkdir(parents=True, exist_ok=True)
            dst_video = out_dir / f"{src.stem}_tracked.mp4"
        else:
            dst_video = Path(output_video_path)
            dst_video.parent.mkdir(parents=True, exist_ok=True)

        # Resolve JSON telemetry destination
        if json_output_path is None:
            dst_json = project_root / "data" / "output" / "tracks.json"
            dst_json.parent.mkdir(parents=True, exist_ok=True)
        else:
            dst_json = Path(json_output_path)
            dst_json.parent.mkdir(parents=True, exist_ok=True)

        # Initialize VideoWriter
        writer = self._create_video_writer(dst_video, fps, (width, height))
        if writer is None or not writer.isOpened():
            cap.release()
            raise RuntimeError(f"Failed to open VideoWriter for destination: '{dst_video}'.")

        all_records: List[Dict[str, Any]] = []
        unique_track_ids: set[int] = set()
        frames_processed = 0
        start_time = time.time()

        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                frames_processed += 1
                timestamp = (frames_processed - 1) / fps

                frame_records = self.track_frame(
                    frame=frame,
                    frame_number=frames_processed,
                    timestamp=timestamp,
                    persist=True,
                )

                for r in frame_records:
                    unique_track_ids.add(r["track_id"])
                    all_records.append(r)

                annotated = self.annotate_frame(
                    frame=frame,
                    records=frame_records,
                    frame_number=frames_processed,
                    total_frames=total_frames if total_frames > 0 else frames_processed,
                )
                writer.write(annotated)

                if progress_callback:
                    progress_callback(frames_processed, total_frames)

        finally:
            cap.release()
            writer.release()

        elapsed = time.time() - start_time
        avg_fps = frames_processed / elapsed if elapsed > 0 else 0.0

        if frames_processed == 0:
            raise ValueError(f"Video file '{input_path}' contains 0 readable frames.")

        # Export JSON structure
        json_payload = {
            "metadata": {
                "video_source": str(src.resolve()),
                "tracker": "ByteTrack",
                "model": str(Path(self.model_path).name),
                "width": width,
                "height": height,
                "fps": round(fps, 2),
                "total_frames": frames_processed,
            },
            "summary": {
                "total_records": len(all_records),
                "unique_person_count": len(unique_track_ids),
                "unique_track_ids": sorted(list(unique_track_ids)),
            },
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
            "elapsed_seconds": round(elapsed, 2),
            "processing_fps": round(avg_fps, 2),
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


def to_behavior_engine_kwargs(record: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a tracking record into keyword arguments expected by Member 2's behavior engine.

    The returned dictionary matches the exact parameter signature for:
        behavior_engine.update(
            track_id=...,
            timestamp=...,
            bbox=...,
            keypoints=...,
            detection_confidence=...
        )

    Args:
        record: Tracking dictionary from PersonTracker.

    Returns:
        Dictionary with keys:
            - 'track_id': int
            - 'timestamp': float
            - 'bbox': List[float] [x1, y1, x2, y2]
            - 'keypoints': Optional[Any] (None / null if unprovided)
            - 'detection_confidence': float
    """
    return {
        "track_id": int(record["track_id"]),
        "timestamp": float(record["timestamp"]),
        "bbox": [float(c) for c in record["bbox"]],
        "keypoints": record.get("keypoints", None),
        "detection_confidence": float(
            record.get("detection_confidence", record.get("confidence", 0.0))
        ),
    }


def dispatch_to_behavior_engine(behavior_engine: Any, record: Dict[str, Any]) -> Any:
    """Convenience helper to dispatch a tracking record to Member 2's behavior engine.

    Args:
        behavior_engine: Object implementing an .update(track_id, timestamp, bbox, keypoints, detection_confidence) method.
        record: Standard tracking record dictionary from PersonTracker.

    Returns:
        Result of the behavior_engine.update(...) call.
    """
    kwargs = to_behavior_engine_kwargs(record)
    return behavior_engine.update(**kwargs)


def main() -> None:
    """CLI entry point for person tracking."""
    parser = argparse.ArgumentParser(
        description="Autonomous Vision & Behaviour Understanding System - Person Tracking (Member 1)"
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=str,
        help="Path to input video file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Path to output annotated video (default: data/output/<input_stem>_tracked.mp4)",
    )
    parser.add_argument(
        "--json-output",
        "-j",
        type=str,
        default=None,
        help="Path to tracking JSON telemetry (default: data/output/tracks.json)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/yolo11n.pt",
        help="Path to YOLO model weights (default: models/yolo11n.pt)",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold (default: 0.25)",
    )
    parser.add_argument(
        "--tracker-config",
        type=str,
        default="bytetrack.yaml",
        help="Tracking configuration (default: bytetrack.yaml)",
    )

    args = parser.parse_args()

    print("=" * 65)
    print("Autonomous Vision & Behaviour Understanding System")
    print("Member 1 Module: Person Tracking with ByteTrack (Phase 3)")
    print("=" * 65)

    try:
        tracker = PersonTracker(
            model_path=args.model,
            conf_threshold=args.conf,
            tracker_config=args.tracker_config,
        )

        def print_progress(cur: int, total: int) -> None:
            if total > 0 and (cur % 5 == 0 or cur == total):
                percent = (cur / total) * 100
                sys.stdout.write(f"\rTracking frame: {cur}/{total} ({percent:.1f}%)")
                sys.stdout.flush()

        print(f"Input Video : {args.input}")
        print(f"Model       : {tracker.model_path}")
        print(f"Tracker     : {args.tracker_config}")
        print(f"Confidence  : {args.conf}")
        print(f"Target Class: person (COCO ID 0)")
        print("-" * 65)

        summary = tracker.process_video(
            input_path=args.input,
            output_video_path=args.output,
            json_output_path=args.json_output,
            progress_callback=print_progress,
        )

        print("\n" + "=" * 65)
        print("Tracking Complete!")
        print("=" * 65)
        print(f"Annotated Video   : {summary['output_video_path']}")
        print(f"JSON Telemetry    : {summary['json_output_path']}")
        print(f"Dimensions        : {summary['width']}x{summary['height']} @ {summary['fps']:.2f} FPS")
        print(f"Frames Processed  : {summary['total_frames_processed']}")
        print(f"Unique Persons    : {summary['unique_person_count']}")
        print(f"Unique Track IDs  : {summary['unique_track_ids']}")
        print(f"Total Records     : {summary['total_tracking_records']}")
        print(f"Elapsed Time      : {summary['elapsed_seconds']}s ({summary['processing_fps']} FPS)")
        print("=" * 65)

    except Exception as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
