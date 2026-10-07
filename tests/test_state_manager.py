"""
Tests for State Manager (transitions, durations, hysteresis, inactivity).
"""

import pytest
from behavior.schemas import ActivityType, EventType
from behavior.config import BehaviorEngineConfig
from behavior.state_manager import StateManager


def test_state_manager_transition_with_min_duration():
    cfg = BehaviorEngineConfig()
    cfg.smoothing.min_duration_seconds = 0.50
    mgr = StateManager(cfg)

    # Initial frame at t=0.0s (STANDING)
    act, prev, dur, trans, evt = mgr.update(1, 0.0, ActivityType.STANDING, 0.95)
    assert act == ActivityType.STANDING
    assert prev is None
    assert trans is None

    # Propose WALKING at t=0.2s (< 0.50s min duration)
    act, prev, dur, trans, evt = mgr.update(1, 0.2, ActivityType.WALKING, 0.95)
    assert act == ActivityType.STANDING  # Still STANDING due to min duration guard
    assert trans is None

    # Continue proposing WALKING at t=0.6s (0.6 - 0.2 = 0.4s < 0.50s)
    act, prev, dur, trans, evt = mgr.update(1, 0.6, ActivityType.WALKING, 0.95)
    assert act == ActivityType.STANDING
    assert trans is None

    # Propose WALKING at t=0.8s (0.8 - 0.2 = 0.6s >= 0.50s) -> commits transition!
    act, prev, dur, trans, evt = mgr.update(1, 0.8, ActivityType.WALKING, 0.95)
    assert act == ActivityType.WALKING
    assert prev == ActivityType.STANDING
    assert trans is not None
    assert trans.from_activity == ActivityType.STANDING
    assert trans.to_activity == ActivityType.WALKING
    assert evt is not None
    assert evt.event_type == EventType.ACTIVITY_CHANGE

    # Next frame at t=1.0s (continuing WALKING) -> no new transition emitted
    act, prev, dur, trans, evt = mgr.update(1, 1.0, ActivityType.WALKING, 0.95)
    assert act == ActivityType.WALKING
    assert trans is None
    assert evt is None


def test_state_manager_prolonged_inactivity():
    cfg = BehaviorEngineConfig()
    cfg.motion.prolonged_inactivity_seconds = 3.0  # short threshold for testing
    mgr = StateManager(cfg)

    # Person stands from t=0.0 to t=4.0
    mgr.update(1, 0.0, ActivityType.STANDING, 0.95)
    mgr.update(1, 1.0, ActivityType.STANDING, 0.95)
    mgr.update(1, 2.0, ActivityType.STANDING, 0.95)

    # At t=3.5s, duration = 3.5s >= 3.0s -> triggers PROLONGED_INACTIVITY
    act, prev, dur, trans, evt = mgr.update(1, 3.5, ActivityType.STANDING, 0.95)
    assert evt is not None
    assert evt.event_type == EventType.PROLONGED_INACTIVITY
    assert evt.details["duration"] >= 3.0

    # At t=4.0s, does not re-trigger repeatedly
    act, prev, dur, trans, evt = mgr.update(1, 4.0, ActivityType.STANDING, 0.95)
    assert evt is None
