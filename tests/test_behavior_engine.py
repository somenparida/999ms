"""
Warehouse Sentinel - End-to-End Behavior Intelligence Tests
Comprehensive validation of all 10 mandatory specification scenarios.
"""

import pytest
from behavior.behavior_engine import BehaviorEngine
from behavior.schemas import ActivityType, EventType
from data.synthetic.generator import (
    generate_standing_sequence,
    generate_walking_sequence,
    generate_running_sequence,
    generate_sitting_sequence,
    generate_lying_sequence,
    generate_fall_sequence,
)


def test_scenario_1_stationary_person_standing():
    """Test 1: Stationary person -> STANDING."""
    engine = BehaviorEngine()
    sequence = generate_standing_sequence(track_id=1, duration=2.0, fps=10.0)

    results = [
        engine.update(f["track_id"], f["timestamp"], f["bbox"], f["keypoints"], f["detection_confidence"])
        for f in sequence
    ]
    # Check that after stabilization, state is STANDING
    assert results[-1].activity == ActivityType.STANDING
    assert results[-1].confidence >= 0.80


def test_scenario_2_moderate_continuous_movement_walking():
    """Test 2: Moderate continuous movement -> WALKING."""
    engine = BehaviorEngine()
    sequence = generate_walking_sequence(track_id=1, duration=2.5, fps=10.0, velocity_px_s=15.0)

    results = [
        engine.update(f["track_id"], f["timestamp"], f["bbox"], f["keypoints"], f["detection_confidence"])
        for f in sequence
    ]
    assert results[-1].activity == ActivityType.WALKING
    assert results[-1].confidence >= 0.80


def test_scenario_3_high_continuous_movement_running():
    """Test 3: High continuous movement -> RUNNING."""
    engine = BehaviorEngine()
    sequence = generate_running_sequence(track_id=1, duration=2.5, fps=10.0, velocity_px_s=36.0)

    results = [
        engine.update(f["track_id"], f["timestamp"], f["bbox"], f["keypoints"], f["detection_confidence"])
        for f in sequence
    ]
    assert results[-1].activity == ActivityType.RUNNING
    assert results[-1].confidence >= 0.80


def test_scenario_4_stable_sitting_pose_sitting():
    """Test 4: Stable sitting pose -> SITTING."""
    engine = BehaviorEngine()
    sequence = generate_sitting_sequence(track_id=1, duration=2.0, fps=10.0)

    results = [
        engine.update(f["track_id"], f["timestamp"], f["bbox"], f["keypoints"], f["detection_confidence"])
        for f in sequence
    ]
    assert results[-1].activity == ActivityType.SITTING
    assert results[-1].confidence >= 0.80


def test_scenario_5_horizontal_stable_posture_lying():
    """Test 5: Horizontal stable posture -> LYING."""
    engine = BehaviorEngine()
    sequence = generate_lying_sequence(track_id=1, duration=2.0, fps=10.0)

    results = [
        engine.update(f["track_id"], f["timestamp"], f["bbox"], f["keypoints"], f["detection_confidence"])
        for f in sequence
    ]
    assert results[-1].activity == ActivityType.LYING
    assert results[-1].confidence >= 0.80


def test_scenario_6_temporal_fall_sequence_possible_fall():
    """Test 6: Standing -> rapid downward displacement -> horizontal -> low movement -> POSSIBLE_FALL / FALL_DETECTED."""
    engine = BehaviorEngine()
    sequence = generate_fall_sequence(track_id=1, start_time=10.0, fps=10.0)

    fall_events = []
    for f in sequence:
        res = engine.update(f["track_id"], f["timestamp"], f["bbox"], f["keypoints"], f["detection_confidence"])
        if res.event and "FALL" in str(res.event.event_type):
            fall_events.append(res.event)

    assert len(fall_events) > 0, "Fall detection failed to trigger during temporal fall sequence"
    assert fall_events[0].event_type in (EventType.POSSIBLE_FALL, EventType.FALL_DETECTED)
    assert fall_events[0].confidence >= 0.60
    assert len(fall_events[0].reason) >= 2


def test_scenario_7_multiple_people_independence():
    """Test 7: Person #1 walking, Person #2 standing, Person #3 running concurrently."""
    engine = BehaviorEngine()

    p1_seq = generate_walking_sequence(track_id=1, duration=2.0, fps=10.0, velocity_px_s=15.0)
    p2_seq = generate_standing_sequence(track_id=2, duration=2.0, fps=10.0)
    p3_seq = generate_running_sequence(track_id=3, duration=2.0, fps=10.0, velocity_px_s=38.0)

    for f1, f2, f3 in zip(p1_seq, p2_seq, p3_seq):
        r1 = engine.update(f1["track_id"], f1["timestamp"], f1["bbox"], f1["keypoints"], f1["detection_confidence"])
        r2 = engine.update(f2["track_id"], f2["timestamp"], f2["bbox"], f2["keypoints"], f2["detection_confidence"])
        r3 = engine.update(f3["track_id"], f3["timestamp"], f3["bbox"], f3["keypoints"], f3["detection_confidence"])

    # Verify track states are completely isolated
    assert r1.track_id == 1 and r1.activity == ActivityType.WALKING
    assert r2.track_id == 2 and r2.activity == ActivityType.STANDING
    assert r3.track_id == 3 and r3.activity == ActivityType.RUNNING


def test_scenario_8_temporary_missing_frames():
    """Test 8: Temporary missing frames. System must not crash and handle dt gaps."""
    engine = BehaviorEngine()

    # Normal frame at t=0.0
    engine.update(track_id=1, timestamp=0.0, bbox=[100, 100, 160, 260], keypoints=None, detection_confidence=0.9)
    # Gap of 1.5 seconds (dropped frames)
    res = engine.update(track_id=1, timestamp=1.5, bbox=[120, 100, 180, 260], keypoints=None, detection_confidence=0.9)
    assert res is not None
    assert res.motion_features.dt == pytest.approx(1.5)


def test_scenario_9_no_pose_keypoints_motion_fallback():
    """Test 9: No pose/keypoints. Ensure motion-only fallback operates cleanly."""
    engine = BehaviorEngine()
    sequence = generate_walking_sequence(track_id=1, duration=2.0, fps=10.0, include_keypoints=False)

    results = [
        engine.update(f["track_id"], f["timestamp"], f["bbox"], keypoints=None, detection_confidence=0.95)
        for f in sequence
    ]
    # Motion alone correctly identifies walking based on velocity and bounding box aspect ratio
    assert results[-1].activity == ActivityType.WALKING
    assert not results[-1].pose_features.available
    # Slight discount applied when pose is missing
    assert results[-1].confidence >= 0.70


def test_scenario_10_low_confidence_detection_unknown():
    """Test 10: Low-confidence detection. Ensure confidence is reduced or activity becomes UNKNOWN."""
    engine = BehaviorEngine()

    # Detection confidence is 0.20 (well below 0.45 threshold)
    res = engine.update(
        track_id=1,
        timestamp=0.0,
        bbox=[100, 100, 160, 260],
        keypoints=None,
        detection_confidence=0.20,
    )
    assert res.activity == ActivityType.UNKNOWN
    assert res.confidence <= 0.30


def test_scenario_11_crouching_squat():
    """Test 11: Stationary crouching / squatting posture -> CROUCHING."""
    from data.synthetic.generator import generate_crouching_sequence
    engine = BehaviorEngine()
    sequence = generate_crouching_sequence(track_id=1, duration=2.0, fps=10.0)

    results = [
        engine.update(f["track_id"], f["timestamp"], f["bbox"], f["keypoints"], f["detection_confidence"])
        for f in sequence
    ]
    assert results[-1].activity == ActivityType.CROUCHING
    assert results[-1].confidence >= 0.80


def test_scenario_12_bending_stoop():
    """Test 12: Stationary forward bent posture at waist with straight legs -> BENDING."""
    from data.synthetic.generator import generate_bending_sequence
    engine = BehaviorEngine()
    sequence = generate_bending_sequence(track_id=1, duration=2.0, fps=10.0)

    results = [
        engine.update(f["track_id"], f["timestamp"], f["bbox"], f["keypoints"], f["detection_confidence"])
        for f in sequence
    ]
    assert results[-1].activity == ActivityType.BENDING
    assert results[-1].confidence >= 0.80
