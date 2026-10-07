"""
Tests for Temporal Smoothing (weighted majority voting, flicker filtering).
"""

import pytest
from behavior.schemas import ActivityType, ActivityPrediction
from behavior.config import SmoothingConfig
from behavior.smoothing import TemporalSmoother


def test_smoothing_filters_single_frame_flicker():
    cfg = SmoothingConfig(window_size=7, recency_weight_decay=0.85)
    smoother = TemporalSmoother(cfg)

    # 3 frames of WALKING
    for i in range(3):
        p = ActivityPrediction(ActivityType.WALKING, 0.90)
        res = smoother.smooth(track_id=1, timestamp=float(i), prediction=p)
        assert res.activity == ActivityType.WALKING

    # 1 anomalous frame of STANDING (e.g. tracking glitch)
    flicker = ActivityPrediction(ActivityType.STANDING, 0.85)
    smoothed = smoother.smooth(track_id=1, timestamp=3.0, prediction=flicker)
    # Majority should maintain WALKING
    assert smoothed.activity == ActivityType.WALKING

    # Subsequent frames back to WALKING
    for i in range(4, 7):
        p = ActivityPrediction(ActivityType.WALKING, 0.92)
        res = smoother.smooth(track_id=1, timestamp=float(i), prediction=p)
        assert res.activity == ActivityType.WALKING
