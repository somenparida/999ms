"""
Tests for Motion Analyzer (kinematics, velocity, acceleration, direction, durations).
"""

import math
import pytest
from behavior.schemas import BoundingBox
from behavior.config import HistoryConfig, MotionConfig
from behavior.temporal_buffer import TrackHistory
from behavior.motion_analyzer import MotionAnalyzer


def test_motion_analyzer_velocity_and_direction():
    hist_cfg = HistoryConfig()
    motion_cfg = MotionConfig()
    analyzer = MotionAnalyzer(motion_cfg)
    history = TrackHistory(track_id=1, config=hist_cfg)

    # Frame 1: center at (100, 100), t = 0.0s
    history.add(0.0, BoundingBox(70, 20, 130, 180), None, 1.0)
    # Frame 2: center at (130, 140), t = 1.0s (dx = 30, dy = 40, dist = 50, v = 50 px/s)
    history.add(1.0, BoundingBox(100, 60, 160, 220), None, 1.0)

    features = analyzer.extract_features(history)
    assert features.pixel_velocity == pytest.approx(50.0, abs=1e-2)
    assert features.vertical_velocity == pytest.approx(40.0, abs=1e-2)
    assert features.direction_rad == pytest.approx(math.atan2(40, 30), abs=1e-2)
    assert features.displacement == pytest.approx(50.0, abs=1e-2)


def test_motion_analyzer_acceleration():
    hist_cfg = HistoryConfig()
    motion_cfg = MotionConfig()
    analyzer = MotionAnalyzer(motion_cfg)
    history = TrackHistory(track_id=1, config=hist_cfg)

    # t = 0: (0, 0)
    history.add(0.0, BoundingBox(-10, -10, 10, 10), None, 1.0)
    # t = 1: (10, 0) -> v = 10 px/s
    history.add(1.0, BoundingBox(0, -10, 20, 10), None, 1.0)
    # t = 2: (40, 0) -> v = 30 px/s, a = (30 - 10) / 1.0 = 20 px/s²
    history.add(2.0, BoundingBox(30, -10, 50, 10), None, 1.0)

    features = analyzer.extract_features(history)
    assert features.pixel_velocity == pytest.approx(30.0, abs=1e-2)
    assert features.acceleration == pytest.approx(20.0, abs=1e-2)
    assert features.max_velocity == pytest.approx(30.0, abs=1e-2)
    assert features.mean_velocity == pytest.approx((0 + 10 + 30) / 3.0, abs=1e-2)


def test_motion_analyzer_stationary_duration():
    hist_cfg = HistoryConfig()
    motion_cfg = MotionConfig()
    analyzer = MotionAnalyzer(motion_cfg)
    history = TrackHistory(track_id=1, config=hist_cfg)

    # 5 frames stationary (v = 0)
    for i in range(5):
        history.add(float(i), BoundingBox(100, 100, 160, 260), None, 1.0)

    features = analyzer.extract_features(history)
    # Stationary continuously from t=0.0 to t=4.0 -> duration = 4.0s
    assert features.stationary_duration == pytest.approx(4.0)
    assert features.movement_duration == 0.0
