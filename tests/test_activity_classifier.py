"""
Tests for Rule-Based Activity Classifier (STANDING, WALKING, RUNNING, SITTING, LYING, UNKNOWN).
"""

import pytest
from behavior.schemas import (
    ActivityType,
    MotionFeatures,
    PoseFeatures,
)
from behavior.config import BehaviorEngineConfig
from behavior.activity_classifier import RuleBasedActivityClassifier


def test_classify_standing():
    cfg = BehaviorEngineConfig()
    classifier = RuleBasedActivityClassifier(cfg)

    motion = MotionFeatures(pixel_velocity=2.0, recent_velocity=2.0)
    pose = PoseFeatures(available=True, aspect_ratio=0.45, torso_angle_deg=5.0, knee_angle_deg=175.0)

    pred = classifier.predict(motion, pose, detection_confidence=0.95)
    assert pred.activity == ActivityType.STANDING
    assert pred.confidence > 0.80
    assert any("Upright" in r for r in pred.reasons)


def test_classify_walking():
    cfg = BehaviorEngineConfig()
    classifier = RuleBasedActivityClassifier(cfg)

    motion = MotionFeatures(pixel_velocity=15.0, recent_velocity=15.0)
    pose = PoseFeatures(available=True, aspect_ratio=0.45, torso_angle_deg=10.0, knee_angle_deg=170.0)

    pred = classifier.predict(motion, pose, detection_confidence=0.95)
    assert pred.activity == ActivityType.WALKING
    assert pred.confidence > 0.80


def test_classify_running():
    cfg = BehaviorEngineConfig()
    classifier = RuleBasedActivityClassifier(cfg)

    motion = MotionFeatures(pixel_velocity=35.0, recent_velocity=35.0, acceleration=18.0)
    pose = PoseFeatures(available=True, aspect_ratio=0.45, torso_angle_deg=15.0)

    pred = classifier.predict(motion, pose, detection_confidence=0.95)
    assert pred.activity == ActivityType.RUNNING
    assert pred.confidence > 0.80


def test_classify_sitting():
    cfg = BehaviorEngineConfig()
    classifier = RuleBasedActivityClassifier(cfg)

    motion = MotionFeatures(pixel_velocity=1.0, recent_velocity=1.0)
    pose = PoseFeatures(
        available=True,
        aspect_ratio=0.65,
        torso_angle_deg=12.0,
        knee_angle_deg=95.0,
        hip_ankle_dy_ratio=0.45,
    )

    pred = classifier.predict(motion, pose, detection_confidence=0.95)
    assert pred.activity == ActivityType.SITTING
    assert pred.confidence > 0.80


def test_classify_lying():
    cfg = BehaviorEngineConfig()
    classifier = RuleBasedActivityClassifier(cfg)

    motion = MotionFeatures(pixel_velocity=1.0, recent_velocity=1.0)
    pose = PoseFeatures(available=True, aspect_ratio=1.6, torso_angle_deg=75.0)

    pred = classifier.predict(motion, pose, detection_confidence=0.95)
    assert pred.activity == ActivityType.LYING
    assert pred.confidence > 0.80


def test_classify_crouching():
    cfg = BehaviorEngineConfig()
    classifier = RuleBasedActivityClassifier(cfg)

    motion = MotionFeatures(pixel_velocity=1.0, recent_velocity=1.0)
    pose = PoseFeatures(
        available=True,
        aspect_ratio=0.75,
        torso_angle_deg=12.0,
        knee_angle_deg=92.0,
        hip_ankle_dy_ratio=0.25,
        normalized_height=0.55,
    )

    pred = classifier.predict(motion, pose, detection_confidence=0.95)
    assert pred.activity == ActivityType.CROUCHING
    assert pred.confidence > 0.80
    assert any("knee flexion" in r.lower() for r in pred.reasons)


def test_classify_bending():
    cfg = BehaviorEngineConfig()
    classifier = RuleBasedActivityClassifier(cfg)

    motion = MotionFeatures(pixel_velocity=1.0, recent_velocity=1.0)
    pose = PoseFeatures(
        available=True,
        aspect_ratio=0.85,
        torso_angle_deg=55.0,
        knee_angle_deg=170.0,
    )

    pred = classifier.predict(motion, pose, detection_confidence=0.95)
    assert pred.activity == ActivityType.BENDING
    assert pred.confidence > 0.80
    assert any("tilted forward" in r.lower() for r in pred.reasons)


def test_classify_unknown_on_low_confidence():
    cfg = BehaviorEngineConfig()
    classifier = RuleBasedActivityClassifier(cfg)

    motion = MotionFeatures(pixel_velocity=15.0)
    pose = PoseFeatures(available=False, aspect_ratio=0.45)

    # Detection confidence 0.30 is below min_detection_confidence (0.45)
    pred = classifier.predict(motion, pose, detection_confidence=0.30)
    assert pred.activity == ActivityType.UNKNOWN
    assert any("Low detection confidence" in r for r in pred.reasons)
