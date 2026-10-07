"""
Tests for Pose Analyzer (COCO 17-keypoint parsing, angles, aspect ratios, fallbacks).
"""

import pytest
from behavior.schemas import BoundingBox
from behavior.config import PoseConfig
from behavior.pose_analyzer import PoseAnalyzer
from data.synthetic.generator import (
    create_upright_keypoints,
    create_sitting_keypoints,
    create_lying_keypoints,
)


def test_pose_analyzer_none_keypoints_fallback():
    cfg = PoseConfig()
    analyzer = PoseAnalyzer(cfg)
    bbox = BoundingBox(100, 100, 160, 260)  # w = 60, h = 160, aspect_ratio = 60/160 = 0.375

    features = analyzer.extract_features(keypoints=None, bbox=bbox)
    assert not features.available
    assert features.aspect_ratio == pytest.approx(0.375)
    assert features.pose_confidence == 0.0


def test_pose_analyzer_incomplete_keypoints_fallback():
    cfg = PoseConfig()
    analyzer = PoseAnalyzer(cfg)
    bbox = BoundingBox(100, 100, 160, 260)
    # Only 5 keypoints instead of 17
    partial_kpts = [[100, 100, 0.9]] * 5

    features = analyzer.extract_features(keypoints=partial_kpts, bbox=bbox)
    assert not features.available
    assert features.aspect_ratio == pytest.approx(0.375)


def test_pose_analyzer_upright_posture():
    cfg = PoseConfig()
    analyzer = PoseAnalyzer(cfg)
    bbox = BoundingBox(170, 220, 230, 380)  # center at (200, 300), h=160, w=60
    kpts = create_upright_keypoints(cx=200, cy=300, height=160, width=60, conf=0.95)

    features = analyzer.extract_features(keypoints=kpts, bbox=bbox)
    assert features.available
    assert features.torso_angle_deg < 15.0  # Upright torso
    assert features.knee_angle_deg > 160.0  # Straight legs
    assert features.aspect_ratio < 0.60
    assert features.pose_confidence > 0.80


def test_pose_analyzer_sitting_bent_knees():
    cfg = PoseConfig()
    analyzer = PoseAnalyzer(cfg)
    bbox = BoundingBox(215, 300, 285, 400)  # center at (250, 350), h=100, w=70
    kpts = create_sitting_keypoints(cx=250, cy=350, height=100, width=70, conf=0.95)

    features = analyzer.extract_features(keypoints=kpts, bbox=bbox)
    assert features.available
    assert features.torso_angle_deg < 25.0  # Upright torso while sitting
    assert features.knee_angle_deg <= 135.0  # Bent knees characteristic of sitting


def test_pose_analyzer_lying_horizontal():
    cfg = PoseConfig()
    analyzer = PoseAnalyzer(cfg)
    bbox = BoundingBox(215, 375, 385, 425)  # center at (300, 400), w=170, h=50
    kpts = create_lying_keypoints(cx=300, cy=400, width=170, height=50, conf=0.95)

    features = analyzer.extract_features(keypoints=kpts, bbox=bbox)
    assert features.available
    assert features.aspect_ratio > 1.2  # Horizontal aspect ratio
    assert features.torso_angle_deg >= 55.0  # Horizontal torso inclination


def test_pose_analyzer_crouching_squat():
    from data.synthetic.generator import create_crouching_keypoints
    cfg = PoseConfig()
    analyzer = PoseAnalyzer(cfg)
    bbox = BoundingBox(215, 305, 285, 395)  # center at (250, 350), h=90, w=70
    kpts = create_crouching_keypoints(cx=250, cy=350, height=90, width=70, conf=0.95)

    features = analyzer.extract_features(keypoints=kpts, bbox=bbox)
    assert features.available
    assert features.knee_angle_deg <= 115.0  # Deep knee flexion
    assert features.hip_ankle_dy_ratio <= 0.35  # Hips close to ankles


def test_pose_analyzer_bending_forward():
    from data.synthetic.generator import create_bending_keypoints
    cfg = PoseConfig()
    analyzer = PoseAnalyzer(cfg)
    bbox = BoundingBox(207, 275, 292, 385)  # center at (250, 330), h=110, w=85
    kpts = create_bending_keypoints(cx=250, cy=330, height=110, width=85, conf=0.95)

    features = analyzer.extract_features(keypoints=kpts, bbox=bbox)
    assert features.available
    assert 35.0 <= features.torso_angle_deg <= 75.0  # Torso tilted forward
    assert features.knee_angle_deg >= 130.0  # Straight legs maintained
