"""Video Object Detection Module for Autonomous Vision & Behaviour Understanding System.

Member 1 Module - Phase 2:
- Frame-by-frame video processing using YOLO11n
- Leverages existing YOLODetector infrastructure
- Preserves original video metadata (width, height, FPS)
- Highlights and filters objects, with special focus on the 'person' class
- Produces annotated output video saved to data/output/
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

from detection.detector import YOLODetector


class VideoDetector:
    """Processes video streams and files frame-by-frame with YOLO detection."""

    def __init__(
        self,
        detector: Optional[YOLODetector] = None,
        model_path: Union[str, Path] = "models/yolo11n.pt",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        target_classes: Optional[List[str]] = None,
        person_only: bool = False,
        device: Optional[str] = None,
    ) -> None:
        """Initialize the video detector.

        Args:
            detector: Existing YOLODetector instance to reuse model weights.
            model_path: Model weights path if instantiating a new detector.
            conf_threshold: Minimum detection confidence threshold.
            iou_threshold: NMS IoU threshold.
            target_classes: Specific class names to filter (e.g. ['person']).
            person_only: If True, restricts detections strictly to 'person'.
            device: Compute device ('cpu', 'cuda', etc.).
        """
        if detector is not None:
            self.detector = detector
        else:
            self.detector = YOLODetector(
                model_path=model_path,
                conf_threshold=conf_threshold,
                iou_threshold=iou_threshold,
                device=device,
            )

        self.person_only = person_only
        self.target_classes = [c.lower() for c in target_classes] if target_classes else None
        if self.person_only:
            self.target_classes = ["person"]

    def process_frame(
        self,
        frame: np.ndarray,
        frame_idx: int = 0,
        total_frames: int = 0,
    ) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """Detect objects and annotate a single video frame.

        Args:
            frame: Input video frame (BGR).
            frame_idx: Current frame index (1-based or 0-based for display).
            total_frames: Total video frame count for HUD overlay.

        Returns:
            Tuple of (annotated_frame, filtered_detections).
        """
        all_detections = self.detector.detect(frame)

        # Filter detections if target classes or person_only is active
        if self.target_classes is not None:
            filtered_detections = [
                d for d in all_detections if d["class_name"].lower() in self.target_classes
            ]
        else:
            filtered_detections = all_detections

        annotated_frame = self.annotate_frame(
            frame,
            filtered_detections,
            frame_idx=frame_idx,
            total_frames=total_frames,
        )

        return annotated_frame, filtered_detections

    def annotate_frame(
        self,
        frame: np.ndarray,
        detections: List[Dict[str, Any]],
        frame_idx: int = 0,
        total_frames: int = 0,
    ) -> np.ndarray:
        """Draw bounding boxes, labels, and informative HUD on a frame.

        Args:
            frame: Raw BGR frame.
            detections: List of detection dictionaries.
            frame_idx: Current frame number.
            total_frames: Total frame count.

        Returns:
            Annotated BGR frame.
        """
        annotated = frame.copy()
        h, w = annotated.shape[:2]

        person_count = 0
        total_count = len(detections)

        for det in detections:
            cls_name = det["class_name"]
            is_person = cls_name.lower() == "person"
            if is_person:
                person_count += 1
                box_color = (0, 230, 0)      # Bright Green for person
                text_color = (0, 0, 0)
                badge_color = (0, 230, 0)
            else:
                box_color = (235, 175, 50)   # Cyan/Gold for other objects
                text_color = (255, 255, 255)
                badge_color = (180, 120, 20)

            x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
            conf = det["confidence"]

            # Clamp coordinates to frame boundaries
            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(0, min(x2, w - 1))
            y2 = max(0, min(y2, h - 1))

            # Bounding box
            thickness = 2 if not is_person else 3
            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, thickness)

            # Label badge
            label = f"{cls_name} {conf:.2f}"
            (lw, lh), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            badge_y1 = max(0, y1 - lh - 8)
            badge_y2 = y1
            cv2.rectangle(
                annotated,
                (x1, badge_y1),
                (min(w, x1 + lw + 6), badge_y2),
                badge_color,
                -1,
            )
            cv2.putText(
                annotated,
                label,
                (x1 + 3, max(lh + 2, y1 - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                text_color,
                1,
                cv2.LINE_AA,
            )

        # HUD Overlay Banner at top-left
        hud_text = f"Frame: {frame_idx}/{total_frames} | Persons: {person_count} | Detections: {total_count}"
        (hw, hh), _ = cv2.getTextSize(hud_text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.rectangle(annotated, (10, 10), (20 + hw, 20 + hh + 10), (30, 30, 30), -1)
        cv2.rectangle(annotated, (10, 10), (20 + hw, 20 + hh + 10), (0, 230, 0), 1)
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

    def process_video(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Process an input video frame-by-frame and write annotated video output.

        Args:
            input_path: Path to source video file.
            output_path: Destination path for annotated video. Defaults to
                data/output/<input_stem>_detected.mp4.
            progress_callback: Optional callable receiving (current_frame, total_frames).

        Returns:
            Dictionary containing processing summary statistics.

        Raises:
            FileNotFoundError: If input video file does not exist.
            ValueError: If input video cannot be read or contains no frames.
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

        # Open video capture
        cap = cv2.VideoCapture(str(src))
        if not cap.isOpened():
            raise ValueError(
                f"Failed to open video file: '{input_path}'. Format may be unsupported or corrupted."
            )

        # Extract video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if width <= 0 or height <= 0:
            cap.release()
            raise ValueError(
                f"Invalid video dimensions ({width}x{height}) in '{input_path}'."
            )

        # Validate FPS fallback
        if fps <= 0 or np.isnan(fps):
            fps = 25.0

        # Resolve output destination
        if output_path is None:
            project_root = Path(__file__).resolve().parent.parent
            out_dir = project_root / "data" / "output"
            out_dir.mkdir(parents=True, exist_ok=True)
            dst = out_dir / f"{src.stem}_detected.mp4"
        else:
            dst = Path(output_path)
            dst.parent.mkdir(parents=True, exist_ok=True)

        # Initialize VideoWriter with codec fallback
        writer = self._create_video_writer(dst, fps, (width, height))
        if writer is None or not writer.isOpened():
            cap.release()
            raise RuntimeError(
                f"Failed to open VideoWriter for destination: '{dst}'."
            )

        frames_processed = 0
        total_detections_count = 0
        total_person_count = 0
        start_time = time.time()

        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                frames_processed += 1
                annotated_frame, detections = self.process_frame(
                    frame,
                    frame_idx=frames_processed,
                    total_frames=total_frames if total_frames > 0 else frames_processed,
                )

                writer.write(annotated_frame)

                # Track metrics
                total_detections_count += len(detections)
                total_person_count += sum(
                    1 for d in detections if d["class_name"].lower() == "person"
                )

                if progress_callback:
                    progress_callback(frames_processed, total_frames)

        finally:
            cap.release()
            writer.release()

        elapsed = time.time() - start_time
        avg_fps = frames_processed / elapsed if elapsed > 0 else 0.0

        if frames_processed == 0:
            raise ValueError(
                f"Video file '{input_path}' contains 0 readable frames."
            )

        return {
            "input_path": str(src.resolve()),
            "output_path": str(dst.resolve()),
            "width": width,
            "height": height,
            "fps": fps,
            "total_frames_processed": frames_processed,
            "total_detections": total_detections_count,
            "total_person_detections": total_person_count,
            "elapsed_seconds": round(elapsed, 2),
            "processing_fps": round(avg_fps, 2),
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


def main() -> None:
    """CLI entry point for video object detection."""
    parser = argparse.ArgumentParser(
        description="Autonomous Vision & Behaviour Understanding System - Video Detection (Member 1)"
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
        help="Path to output annotated video (default: data/output/<input_stem>_detected.mp4)",
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
        "--person-only",
        action="store_true",
        help="Focus exclusively on the 'person' class",
    )
    parser.add_argument(
        "--classes",
        nargs="+",
        default=None,
        help="Filter specific target classes (e.g. --classes person car)",
    )

    args = parser.parse_args()

    print("=" * 65)
    print("Autonomous Vision & Behaviour Understanding System")
    print("Member 1 Module: Video Detection (Phase 2)")
    print("=" * 65)

    try:
        video_detector = VideoDetector(
            model_path=args.model,
            conf_threshold=args.conf,
            target_classes=args.classes,
            person_only=args.person_only,
        )

        def print_progress(cur: int, total: int) -> None:
            if total > 0 and (cur % 10 == 0 or cur == total):
                percent = (cur / total) * 100
                sys.stdout.write(f"\rProcessing frame: {cur}/{total} ({percent:.1f}%)")
                sys.stdout.flush()

        print(f"Input Video : {args.input}")
        print(f"Model       : {video_detector.detector.model_path}")
        print(f"Confidence  : {args.conf}")
        print(f"Focus       : {'person only' if args.person_only else args.classes or 'all objects (person highlighted)'}")
        print("-" * 65)

        summary = video_detector.process_video(
            input_path=args.input,
            output_path=args.output,
            progress_callback=print_progress,
        )

        print("\n" + "=" * 65)
        print("Processing Complete!")
        print("=" * 65)
        print(f"Saved Output Video    : {summary['output_path']}")
        print(f"Dimensions            : {summary['width']}x{summary['height']} @ {summary['fps']:.2f} FPS")
        print(f"Frames Processed      : {summary['total_frames_processed']}")
        print(f"Total Detections      : {summary['total_detections']}")
        print(f"Person Detections     : {summary['total_person_detections']}")
        print(f"Elapsed Time          : {summary['elapsed_seconds']}s ({summary['processing_fps']} FPS)")
        print("=" * 65)

    except Exception as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
