"""Unit tests for Phase 2 Video Object Detection module.

Tests:
1. VideoDetector instantiation and configuration
2. Error handling on non-existent input video
3. Error handling on unreadable/invalid video file
4. Frame processing and HUD annotation
5. Synthetic video end-to-end processing preserving width, height, and FPS
6. Person filtering configuration
"""

import shutil
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from detection.detector import YOLODetector
from detection.video_detector import VideoDetector


class TestVideoDetector(unittest.TestCase):
    """Test suite for VideoDetector component."""

    @classmethod
    def setUpClass(cls) -> None:
        """Instantiate a shared YOLODetector to avoid reloading weights repeatedly."""
        cls.detector = YOLODetector()

    def setUp(self) -> None:
        """Create a temporary directory for test video artifacts."""
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_video_"))

    def tearDown(self) -> None:
        """Clean up temporary directory and files."""
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
        """Generate a small synthetic test video without external dependencies."""
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(filepath), fourcc, fps, (width, height))
        for i in range(num_frames):
            frame = np.full((height, width, 3), 120, dtype=np.uint8)
            # Draw simple motion pattern
            cv2.rectangle(frame, (20 + i * 10, 30), (80 + i * 10, 100), (0, 200, 50), -1)
            writer.write(frame)
        writer.release()
        return filepath

    def test_instantiation_with_shared_detector(self) -> None:
        """Verify VideoDetector can reuse an existing YOLODetector instance."""
        v_det = VideoDetector(detector=self.detector, conf_threshold=0.3)
        self.assertIs(v_det.detector, self.detector)
        self.assertFalse(v_det.person_only)

    def test_person_only_configuration(self) -> None:
        """Verify person_only flag correctly configures target classes."""
        v_det = VideoDetector(detector=self.detector, person_only=True)
        self.assertTrue(v_det.person_only)
        self.assertEqual(v_det.target_classes, ["person"])

    def test_missing_video_error(self) -> None:
        """Verify passing a non-existent video path raises FileNotFoundError."""
        v_det = VideoDetector(detector=self.detector)
        missing_path = self.test_dir / "does_not_exist.mp4"

        with self.assertRaises(FileNotFoundError) as ctx:
            v_det.process_video(missing_path)

        self.assertIn("Input video file not found", str(ctx.exception))

    def test_invalid_video_error(self) -> None:
        """Verify passing an unreadable/invalid video file raises ValueError."""
        v_det = VideoDetector(detector=self.detector)
        corrupt_file = self.test_dir / "corrupted.mp4"
        corrupt_file.write_text("This is plain text, not a valid video file.")

        with self.assertRaises(ValueError):
            v_det.process_video(corrupt_file)

    def test_process_frame_annotation(self) -> None:
        """Verify single frame processing produces valid annotated output."""
        v_det = VideoDetector(detector=self.detector)
        frame = np.zeros((240, 320, 3), dtype=np.uint8)

        annotated, detections = v_det.process_frame(frame, frame_idx=1, total_frames=1)
        self.assertIsInstance(annotated, np.ndarray)
        self.assertEqual(annotated.shape, (240, 320, 3))
        self.assertIsInstance(detections, list)

    def test_process_video_synthetic_end_to_end(self) -> None:
        """Verify end-to-end processing preserves width, height, and FPS."""
        input_video = self.test_dir / "synthetic_input.mp4"
        output_video = self.test_dir / "synthetic_output.mp4"

        w, h, fps, count = 320, 240, 10.0, 5
        self._create_synthetic_video(input_video, num_frames=count, width=w, height=h, fps=fps)

        v_det = VideoDetector(detector=self.detector)
        summary = v_det.process_video(input_video, output_video)

        # Verify summary statistics
        self.assertEqual(summary["total_frames_processed"], count)
        self.assertEqual(summary["width"], w)
        self.assertEqual(summary["height"], h)
        self.assertEqual(summary["fps"], fps)
        self.assertTrue(output_video.exists())
        self.assertGreater(output_video.stat().st_size, 0)

        # Inspect generated output video using cv2.VideoCapture
        cap = cv2.VideoCapture(str(output_video))
        self.assertTrue(cap.isOpened(), "Output video could not be opened by OpenCV.")
        out_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        out_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out_fps = cap.get(cv2.CAP_PROP_FPS)

        self.assertEqual(out_w, w)
        self.assertEqual(out_h, h)
        self.assertAlmostEqual(out_fps, fps, delta=1.0)

        # Verify readable frames
        read_frames = 0
        while True:
            ret, _ = cap.read()
            if not ret:
                break
            read_frames += 1
        cap.release()

        self.assertEqual(read_frames, count)


if __name__ == "__main__":
    unittest.main(verbosity=2)
