"""
Warehouse Sentinel - Temporal Buffer
Maintains rolling temporal buffers of observations, kinematic measurements,
and poses independently for each tracked person.
"""

from __future__ import annotations
import math
import logging
from collections import deque
from typing import Dict, List, Optional, Tuple, Any

from .schemas import BoundingBox, Keypoint
from .config import HistoryConfig

logger = logging.getLogger(__name__)


class TrackHistory:
    """Rolling temporal history for a single tracked person."""

    def __init__(self, track_id: int, config: HistoryConfig):
        self.track_id = track_id
        self.config = config

        self.timestamps: deque[float] = deque(maxlen=config.max_frames)
        self.centers: deque[Tuple[float, float]] = deque(maxlen=config.max_frames)
        self.bboxes: deque[BoundingBox] = deque(maxlen=config.max_frames)
        self.keypoints: deque[Optional[List[Keypoint]]] = deque(maxlen=config.max_frames)
        self.confidences: deque[float] = deque(maxlen=config.max_frames)
        self.velocities: deque[float] = deque(maxlen=config.max_frames)
        self.accelerations: deque[float] = deque(maxlen=config.max_frames)
        self.vertical_velocities: deque[float] = deque(maxlen=config.max_frames)

        self.last_updated: float = 0.0

    def __len__(self) -> int:
        return len(self.timestamps)

    def add(
        self,
        timestamp: float,
        bbox: BoundingBox,
        keypoints: Optional[List[Keypoint]],
        confidence: float,
    ) -> None:
        """Add observation and compute instantaneous motion kinematics."""
        self.last_updated = timestamp

        # Calculate instantaneous kinematics if previous observation exists
        v = 0.0
        vy = 0.0
        a = 0.0

        if len(self.timestamps) > 0:
            prev_time = self.timestamps[-1]
            dt = timestamp - prev_time

            # Guard against duplicate or negative dt
            if dt > 1e-4:
                prev_cx, prev_cy = self.centers[-1]
                cur_cx, cur_cy = bbox.center

                dx = cur_cx - prev_cx
                dy = cur_cy - prev_cy
                dist = math.hypot(dx, dy)

                v = dist / dt
                vy = dy / dt  # Positive downward in screen coordinates

                if len(self.velocities) > 0:
                    prev_v = self.velocities[-1]
                    a = (v - prev_v) / dt
            else:
                # Same timestamp or non-positive dt; inherit previous speed if available
                v = self.velocities[-1] if len(self.velocities) > 0 else 0.0
                vy = self.vertical_velocities[-1] if len(self.vertical_velocities) > 0 else 0.0
                a = 0.0

        # Append new values
        self.timestamps.append(timestamp)
        self.centers.append(bbox.center)
        self.bboxes.append(bbox)
        self.keypoints.append(keypoints)
        self.confidences.append(confidence)
        self.velocities.append(v)
        self.accelerations.append(a)
        self.vertical_velocities.append(vy)

        # Evict entries outside the max_seconds window
        cutoff = timestamp - self.config.max_seconds
        while len(self.timestamps) > 1 and self.timestamps[0] < cutoff:
            self.timestamps.popleft()
            self.centers.popleft()
            self.bboxes.popleft()
            self.keypoints.popleft()
            self.confidences.popleft()
            self.velocities.popleft()
            self.accelerations.popleft()
            self.vertical_velocities.popleft()

    def get_latest(self) -> Dict[str, Any]:
        """Return the most recent observation."""
        if not self.timestamps:
            return {}
        return {
            "timestamp": self.timestamps[-1],
            "center": self.centers[-1],
            "bbox": self.bboxes[-1],
            "keypoints": self.keypoints[-1],
            "confidence": self.confidences[-1],
            "velocity": self.velocities[-1],
            "acceleration": self.accelerations[-1],
            "vertical_velocity": self.vertical_velocities[-1],
        }


class TemporalBuffer:
    """Manages rolling temporal histories across all tracked people."""

    def __init__(self, config: HistoryConfig):
        self.config = config
        self.tracks: Dict[int, TrackHistory] = {}

    def update(
        self,
        track_id: int,
        timestamp: float,
        bbox: BoundingBox,
        keypoints: Optional[List[Keypoint]],
        confidence: float,
    ) -> TrackHistory:
        """Update track buffer with new observation and auto-prune stale tracks."""
        # Auto-prune tracks that haven't been seen recently
        self.prune_stale_tracks(timestamp)

        if track_id not in self.tracks:
            self.tracks[track_id] = TrackHistory(track_id, self.config)

        track = self.tracks[track_id]
        track.add(timestamp, bbox, keypoints, confidence)
        return track

    def prune_stale_tracks(self, current_timestamp: float) -> List[int]:
        """Remove tracks whose last update exceeds stale_track_seconds."""
        stale_ids = []
        for tid, track in list(self.tracks.items()):
            if current_timestamp - track.last_updated > self.config.stale_track_seconds:
                stale_ids.append(tid)

        for tid in stale_ids:
            logger.debug(f"Evicting stale track {tid} (idle > {self.config.stale_track_seconds}s)")
            del self.tracks[tid]

        return stale_ids

    def get_track(self, track_id: int) -> Optional[TrackHistory]:
        return self.tracks.get(track_id)

    def remove_track(self, track_id: int) -> bool:
        if track_id in self.tracks:
            del self.tracks[track_id]
            return True
        return False

    def clear(self) -> None:
        self.tracks.clear()
