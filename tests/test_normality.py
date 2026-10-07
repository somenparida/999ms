"""
Warehouse Sentinel - Normality Intelligence Layer Tests
Validates all simple normal vs abnormal behavior rules, durations, and fall transitions.
"""

import pytest
from behavior.schemas import ActivityType, BehaviorStatus, Severity
from behavior.config import NormalityConfig
from behavior.normality import NormalityClassifier, classify_behavior
from behavior.behavior_engine import BehaviorEngine


def test_normality_standing_is_normal():
    res = classify_behavior(ActivityType.STANDING, duration=5.0)
    assert res.status == BehaviorStatus.NORMAL
    assert res.severity == Severity.NONE
    assert res.reason is None


def test_normality_walking_is_normal():
    res = classify_behavior(ActivityType.WALKING, duration=12.0)
    assert res.status == BehaviorStatus.NORMAL
    assert res.severity == Severity.NONE
    assert res.reason is None


def test_normality_running_is_normal():
    res = classify_behavior(ActivityType.RUNNING, duration=4.0)
    assert res.status == BehaviorStatus.NORMAL
    assert res.severity == Severity.NONE
    assert res.reason is None


def test_normality_sitting_is_normal():
    res = classify_behavior(ActivityType.SITTING, duration=25.0)
    assert res.status == BehaviorStatus.NORMAL
    assert res.severity == Severity.NONE
    assert res.reason is None


def test_normality_short_bending_is_normal():
    res = classify_behavior(ActivityType.BENDING, duration=5.0)
    assert res.status == BehaviorStatus.NORMAL
    assert res.severity == Severity.NONE
    assert res.reason is None


def test_normality_short_crouching_is_normal():
    res = classify_behavior(ActivityType.CROUCHING, duration=8.0)
    assert res.status == BehaviorStatus.NORMAL
    assert res.severity == Severity.NONE
    assert res.reason is None


def test_normality_short_lying_is_normal():
    res = classify_behavior(ActivityType.LYING, duration=10.0, has_fallen=False)
    assert res.status == BehaviorStatus.NORMAL
    assert res.severity == Severity.NONE
    assert res.reason is None


def test_normality_long_lying_is_potentially_unusual():
    cfg = NormalityConfig(prolonged_lying_seconds=30.0)
    classifier = NormalityClassifier(cfg)
    res = classifier.classify(ActivityType.LYING, duration=45.0, has_fallen=False)
    assert res.status == BehaviorStatus.POTENTIALLY_UNUSUAL
    assert res.severity == Severity.LOW
    assert res.reason == "Prolonged lying"


def test_normality_long_bending_is_potentially_unusual():
    cfg = NormalityConfig(prolonged_bending_seconds=30.0)
    classifier = NormalityClassifier(cfg)
    res = classifier.classify(ActivityType.BENDING, duration=35.0)
    assert res.status == BehaviorStatus.POTENTIALLY_UNUSUAL
    assert res.severity == Severity.LOW
    assert res.reason == "Prolonged bending"


def test_normality_long_crouching_is_potentially_unusual():
    cfg = NormalityConfig(prolonged_crouching_seconds=30.0)
    classifier = NormalityClassifier(cfg)
    res = classifier.classify(ActivityType.CROUCHING, duration=40.0)
    assert res.status == BehaviorStatus.POTENTIALLY_UNUSUAL
    assert res.severity == Severity.LOW
    assert res.reason == "Prolonged crouching"


def test_normality_falling_is_abnormal():
    res = classify_behavior(ActivityType.FALLING, duration=1.0)
    assert res.status == BehaviorStatus.ABNORMAL
    assert res.severity == Severity.HIGH
    assert res.reason == "Possible fall detected"


def test_normality_falling_then_lying_is_abnormal():
    # Previous activity was FALLING or has_fallen flag is set
    res = classify_behavior(
        activity=ActivityType.LYING,
        duration=5.0,
        previous_activity=ActivityType.FALLING,
        has_fallen=True,
    )
    assert res.status == BehaviorStatus.ABNORMAL
    assert res.severity == Severity.HIGH
    assert res.reason == "Lying following a fall"


def test_normality_unknown_is_unknown():
    res = classify_behavior(ActivityType.UNKNOWN, duration=2.0)
    assert res.status == BehaviorStatus.UNKNOWN
    assert res.severity == Severity.NONE
    assert res.reason is None


def test_normality_integration_with_behavior_engine():
    """Verify BehaviorEngine output includes status, severity, and reason."""
    engine = BehaviorEngine()

    # Frame 1: walking
    r1 = engine.update(
        track_id=1,
        timestamp=0.0,
        bbox=[100, 100, 160, 260],
        detection_confidence=0.95,
    )
    assert r1.status == BehaviorStatus.NORMAL
    assert r1.severity == Severity.NONE
    assert r1["status"] == "NORMAL"
    assert r1["severity"] == "NONE"
    assert "status" in r1.to_dict()
    assert "severity" in r1.to_dict()
