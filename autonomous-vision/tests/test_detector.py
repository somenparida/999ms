"""Unit tests for the Member 1 YOLO Detector module.

Verifies:
1. Ultralytics YOLO can be imported
2. YOLO11n can be loaded
3. The detector object can be instantiated
4. Detection inference functions properly without requiring external image files
5. Missing image paths raise a clear, informative error
"""

import unittest
from pathlib import Path

import numpy as np


class TestYOLODetector(unittest.TestCase):
    """Test suite for YOLO detector imports, loading, instantiation, and error handling."""

    def test_ultralytics_import(self) -> None:
        """Verify Ultralytics YOLO can be imported."""
        try:
            from ultralytics import YOLO
            self.assertTrue(callable(YOLO))
        except ImportError as exc:
            self.fail(f"Failed to import YOLO from ultralytics: {exc}")

    def test_yolo_model_loading(self) -> None:
        """Verify YOLO11n model can be loaded successfully."""
        from ultralytics import YOLO

        project_root = Path(__file__).resolve().parent.parent
        model_path = project_root / "models" / "yolo11n.pt"
        if not model_path.exists():
            model_path = project_root / "yolo11n.pt"

        self.assertTrue(model_path.exists(), f"Model file not found at {model_path}")
        model = YOLO(str(model_path))
        self.assertIsNotNone(model)

    def test_detector_instantiation(self) -> None:
        """Verify the YOLODetector object can be instantiated."""
        from detection.detector import YOLODetector

        detector = YOLODetector()
        self.assertIsNotNone(detector)
        self.assertIsNotNone(detector.model)
        self.assertEqual(detector.conf_threshold, 0.25)
        self.assertEqual(detector.iou_threshold, 0.45)

    def test_detector_inference_synthetic_image(self) -> None:
        """Verify detector can perform inference on an in-memory image without external files."""
        from detection.detector import YOLODetector

        detector = YOLODetector()
        # Create an in-memory synthetic image (640x480x3 uint8)
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)

        detections = detector.detect(dummy_image)
        self.assertIsInstance(detections, list)

        # If any detections occur, verify schema contract
        for det in detections:
            self.assertIn("class_id", det)
            self.assertIn("class_name", det)
            self.assertIn("confidence", det)
            self.assertIn("bbox", det)
            self.assertEqual(len(det["bbox"]), 4)

    def test_missing_image_error(self) -> None:
        """Verify missing image paths raise a clear FileNotFoundError."""
        from detection.detector import YOLODetector

        detector = YOLODetector()
        non_existent_path = "data/input/definitely_missing_file_12345.jpg"

        with self.assertRaises(FileNotFoundError) as ctx:
            detector.detect(non_existent_path)

        self.assertIn("Image file not found", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
