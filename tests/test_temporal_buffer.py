"""
Tests for Temporal Buffer (per-track history, eviction, bounded memory).
"""

import pytest
from behavior.schemas import BoundingBox, Keypoint
from behavior.config import HistoryConfig
from behavior.temporal_buffer import TemporalBuffer, TrackHistory


def test_track_history_add_and_pruning():
    cfg = HistoryConfig(max_seconds=2.0, stale_track_seconds=1.0, max_frames=20)
    history = TrackHistory(track_id=1, config=cfg)

    # Add 10 observations spaced 0.1s apart (total 0.9s duration)
    for i in range(10):
        t = 10.0 + i * 0.1
        bbox = BoundingBox(100 + i * 2, 100, 160 + i * 2, 260)
        history.add(timestamp=t, bbox=bbox, keypoints=None, confidence=0.9)

    assert len(history) == 10
    assert history.last_updated == pytest.approx(10.9)
    # Check that velocity was calculated (dx = 2px, dt = 0.1s -> 20px/s)
    assert history.velocities[-1] == pytest.approx(20.0, abs=1e-2)

    # Now add an observation at t = 13.0s (> 2.0s cutoff from t=10.0s)
    bbox_new = BoundingBox(200, 100, 260, 260)
    history.add(timestamp=13.0, bbox=bbox_new, keypoints=None, confidence=0.9)

    # Observations older than 13.0 - 2.0 = 11.0 should have been popped
    for t in history.timestamps:
        assert t >= 11.0


def test_temporal_buffer_multi_track_independence():
    cfg = HistoryConfig(max_seconds=5.0, stale_track_seconds=2.0, max_frames=50)
    buffer = TemporalBuffer(cfg)

    # Track 1
    t1_box = BoundingBox(10, 10, 50, 90)
    h1 = buffer.update(track_id=1, timestamp=1.0, bbox=t1_box, keypoints=None, confidence=0.95)

    # Track 2
    t2_box = BoundingBox(200, 200, 250, 320)
    h2 = buffer.update(track_id=2, timestamp=1.0, bbox=t2_box, keypoints=None, confidence=0.88)

    assert h1.track_id == 1
    assert h2.track_id == 2
    assert len(buffer.tracks) == 2
    assert buffer.get_track(1) is h1
    assert buffer.get_track(2) is h2


def test_temporal_buffer_stale_track_eviction():
    cfg = HistoryConfig(max_seconds=5.0, stale_track_seconds=1.5, max_frames=50)
    buffer = TemporalBuffer(cfg)

    # Track 1 updated at t=1.0
    buffer.update(track_id=1, timestamp=1.0, bbox=BoundingBox(0, 0, 10, 10), keypoints=None, confidence=1.0)
    # Track 2 updated at t=2.0
    buffer.update(track_id=2, timestamp=2.0, bbox=BoundingBox(0, 0, 10, 10), keypoints=None, confidence=1.0)

    # Update Track 2 at t=3.0 (idle for Track 1 is 3.0 - 1.0 = 2.0s > 1.5s)
    buffer.update(track_id=2, timestamp=3.0, bbox=BoundingBox(5, 5, 15, 15), keypoints=None, confidence=1.0)

    # Track 1 should have been automatically pruned
    assert buffer.get_track(1) is None
    assert buffer.get_track(2) is not None


def test_temporal_buffer_zero_dt_handling():
    cfg = HistoryConfig(max_seconds=5.0, stale_track_seconds=2.0, max_frames=50)
    history = TrackHistory(track_id=1, config=cfg)

    # Same timestamp added consecutively should not divide by zero
    history.add(timestamp=10.0, bbox=BoundingBox(10, 10, 50, 90), keypoints=None, confidence=0.9)
    history.add(timestamp=10.0, bbox=BoundingBox(12, 10, 52, 90), keypoints=None, confidence=0.9)

    assert len(history) == 2
    assert history.velocities[-1] == 0.0
