"""YOLO Object Detection Module for Autonomous Vision & Behaviour Understanding System.

Member 1 Module:
- YOLO11n object/person detection
- Standardized detection schema for downstream tracking (ByteTrack/BoT-SORT) and Member 2 modules
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import cv2
import numpy as np
from ultralytics import YOLO


class YOLODetector:
    """Reusable YOLO detector wrapper supporting image inference and structured outputs."""

    def __init__(
        self,
        model_path: Union[str, Path] = "models/yolo11n.pt",
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        device: Optional[str] = None,
    ) -> None:
        """Initialize the YOLO detector.

        Args:
            model_path: Path to the model weights file (defaults to models/yolo11n.pt).
            conf_threshold: Minimum confidence score to filter detections.
            iou_threshold: NMS IoU threshold.
            device: Computation device ('cpu', 'cuda', etc.). None for auto-selection.
        """
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        self.model_path = self._resolve_model_path(model_path)

        # Load YOLO model instance
        self.model = YOLO(self.model_path)

    @staticmethod
    def _resolve_model_path(model_path: Union[str, Path]) -> str:
        """Resolve model weights path against working directory and project root."""
        path_obj = Path(model_path)
        if path_obj.is_file():
            return str(path_obj.resolve())

        # Check relative to project root
        project_root = Path(__file__).resolve().parent.parent
        candidate_models = project_root / "models" / path_obj.name
        if candidate_models.is_file():
            return str(candidate_models.resolve())

        candidate_root = project_root / path_obj.name
        if candidate_root.is_file():
            return str(candidate_root.resolve())

        # Return original string for Ultralytics default lookup
        return str(model_path)

    def detect(
        self,
        source: Union[str, Path, np.ndarray],
        conf_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Run object detection on an image input.

        Args:
            source: File path to image or a numpy image array (BGR format).
            conf_threshold: Optional per-call confidence threshold override.

        Returns:
            List of detected object dictionaries, each containing:
                - 'class_id': int
                - 'class_name': str
                - 'confidence': float (rounded to 4 decimal places)
                - 'bbox': [x1, y1, x2, y2] (float coords rounded to 2 decimal places)

        Raises:
            FileNotFoundError: If the source path does not exist.
            ValueError: If the source path cannot be read as an image.
        """
        threshold = conf_threshold if conf_threshold is not None else self.conf_threshold

        # Validate input path if a string or Path is provided
        if isinstance(source, (str, Path)):
            img_path = Path(source)
            if not img_path.exists():
                raise FileNotFoundError(
                    f"Image file not found: '{source}'. Please provide a valid file path."
                )
            if not img_path.is_file():
                raise ValueError(
                    f"Provided path '{source}' exists but is not a file."
                )

            image = cv2.imread(str(img_path))
            if image is None:
                raise ValueError(
                    f"Unable to decode image at '{source}'. Check file integrity and image format."
                )
        elif isinstance(source, np.ndarray):
            image = source
        else:
            raise TypeError(
                f"Unsupported image input type: {type(source)}. Expected str, Path, or numpy.ndarray."
            )

        # Run inference
        results = self.model(
            image,
            conf=threshold,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False,
        )

        detections: List[Dict[str, Any]] = []

        if not results:
            return detections

        first_res = results[0]
        boxes = first_res.boxes
        if boxes is None or len(boxes) == 0:
            return detections

        # Extract names lookup dictionary
        names = self.model.names if hasattr(self.model, "names") else {}

        # Parse bounding boxes
        xyxy_coords = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        classes = boxes.cls.cpu().numpy().astype(int)

        for coord, conf, cls_id in zip(xyxy_coords, confs, classes):
            cls_name = names.get(cls_id, str(cls_id))
            detection_dict: Dict[str, Any] = {
                "class_id": int(cls_id),
                "class_name": str(cls_name),
                "confidence": round(float(conf), 4),
                "bbox": [round(float(c), 2) for c in coord.tolist()],
            }
            detections.append(detection_dict)

        return detections

    def draw_detections(
        self,
        image: np.ndarray,
        detections: List[Dict[str, Any]],
        color: tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
    ) -> np.ndarray:
        """Annotate image with bounding boxes and labels.

        Args:
            image: Original BGR image as a numpy array.
            detections: List of detection dictionaries from detect().
            color: Box and text color (BGR).
            thickness: Line thickness.

        Returns:
            Annotated BGR image as a numpy array.
        """
        annotated = image.copy()
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
            label = f"{det['class_name']} {det['confidence']:.2f}"

            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness)

            # Draw label tag with background
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated, (x1, max(0, y1 - 20)), (x1 + w, max(0, y1)), color, -1)
            cv2.putText(
                annotated,
                label,
                (x1, max(14, y1 - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

        return annotated


def format_detections_summary(detections: List[Dict[str, Any]]) -> str:
    """Format detection list into a clean, human-readable summary table."""
    if not detections:
        return "No objects detected."

    header = f"{'#':<4} | {'Class Name':<16} | {'Class ID':<8} | {'Confidence':<10} | {'BBox [x1, y1, x2, y2]'}"
    separator = "-" * len(header)
    lines = [f"Total Detections: {len(detections)}", separator, header, separator]

    for idx, det in enumerate(detections, start=1):
        bbox_str = f"[{det['bbox'][0]:.1f}, {det['bbox'][1]:.1f}, {det['bbox'][2]:.1f}, {det['bbox'][3]:.1f}]"
        line = (
            f"{idx:<4} | "
            f"{det['class_name']:<16} | "
            f"{det['class_id']:<8} | "
            f"{det['confidence']:<10.4f} | "
            f"{bbox_str}"
        )
        lines.append(line)
    lines.append(separator)
    return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 60)
    print("Autonomous Vision & Behaviour Understanding System")
    print("Member 1 Module: YOLO Object Detector")
    print("=" * 60)

    # Initialize detector
    detector = YOLODetector()
    print(f"Model loaded: {detector.model_path}")
    print(f"Default confidence threshold: {detector.conf_threshold}")

    # Check for a sample image in data/input or generate a synthetic test image
    sample_dir = Path(__file__).resolve().parent.parent / "data" / "input"
    sample_image_path = sample_dir / "sample.jpg"

    if not sample_image_path.exists():
        # Create a clean synthetic image with simple shapes for direct execution demo
        sample_dir.mkdir(parents=True, exist_ok=True)
        synthetic_img = np.full((480, 640, 3), 200, dtype=np.uint8)
        # Draw a synthetic colored shape
        cv2.rectangle(synthetic_img, (150, 100), (350, 400), (40, 40, 220), -1)
        cv2.putText(
            synthetic_img,
            "YOLO Test Pattern",
            (160, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (20, 20, 20),
            2,
        )
        cv2.imwrite(str(sample_image_path), synthetic_img)
        print(f"Generated sample demonstration image at: {sample_image_path}")

    print(f"\nRunning detection on: {sample_image_path}")
    results = detector.detect(sample_image_path)
    print("\n" + format_detections_summary(results))
