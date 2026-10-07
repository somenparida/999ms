"""
Tests for Fall Detector (temporal multi-stage validation, intentional lying rejection).
"""

import pytest
from behavior.config import FallDetectionConfig, HistoryConfig, MotionConfig, PoseConfig
from behavior.temporal_buffer import TrackHistory
from behavior.motion_analyzer import MotionAnalyzer
from behavior.pose_analyzer import PoseAnalyzer
from behavior.fall_detector import FallDetector
from data.synthetic.generator import generate_fall_sequence, generate_lying_sequence


def test_fall_detector_detects_genuine_fall():
    fall_cfg = FallDetectionConfig()
    hist_cfg = HistoryConfig()
    motion_cfg = MotionConfig()
    pose_cfg = PoseConfig()

    detector = FallDetector(fall_cfg)
    motion_analyzer = MotionAnalyzer(motion_cfg)
    pose_analyzer = PoseAnalyzer(pose_cfg)
    history = TrackHistory(track_id=1, config=hist_cfg)

    fall_frames = generate_fall_sequence(track_id=1, start_time=10.0, fps=10.0)

    detected_any = False
    for frame in fall_frames:
        history.add(
            frame["timestamp"],
            # parse bbox
            from_iter := __import__("behavior.schemas").schemas.BoundingBox.from_iterable(frame["bbox"]),
            frame["keypoints"],
            frame["detection_confidence"],
        )
        motion = motion_analyzer.extract_features(history)
        pose = pose_analyzer.extract_features(frame["keypoints"], from_iter)

        detected, score, reasons, event = detector.analyze(1, history, motion, pose)
        if detected:
            detected_any = True
            assert score >= fall_cfg.possible_fall_threshold
            assert event is not None
            assert "FALL" in str(event.event_type)
            assert len(reasons) >= 2
            break

    assert detected_any, "Expected genuine fall sequence to trigger fall detector"


def test_fall_detector_rejects_intentional_gradual_lying():
    fall_cfg = FallDetectionConfig()
    hist_cfg = HistoryConfig()
    motion_cfg = MotionConfig()
    pose_cfg = PoseConfig()

    detector = FallDetector(fall_cfg)
    motion_analyzer = MotionAnalyzer(motion_cfg)
    pose_analyzer = PoseAnalyzer(pose_cfg)
    history = TrackHistory(track_id=1, config=hist_cfg)

    # Stationary lying frames without any prior downward descent spike
    lying_frames = generate_lying_sequence(track_id=1, start_time=0.0, duration=3.0, fps=10.0)

    for frame in lying_frames:
        bbox = __import__("behavior.schemas").schemas.BoundingBox.from_iterable(frame["bbox"])
        history.add(frame["timestamp"], bbox, frame["keypoints"], frame["detection_confidence"])
        motion = motion_analyzer.extract_features(history)
        pose = pose_analyzer.extract_features(frame["keypoints"], bbox)

        detected, score, reasons, event = detector.analyze(1, history, motion, pose)
        assert not detected, "Intentional lying should not be classified as a fall"
