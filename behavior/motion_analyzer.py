"""
Warehouse Sentinel - Motion Feature Extractor
Extracts kinematic and movement statistics from temporal track history.
"""

from __future__ import annotations
import math
from typing import List, Tuple
import numpy as np

from .schemas import MotionFeatures
from .temporal_buffer import TrackHistory
from .config import MotionConfig


class MotionAnalyzer:
    """Analyzes 2D motion kinematics and trajectory statistics for a tracked subject."""

    def __init__(self, config: MotionConfig):
        self.config = config

    def extract_features(self, history: TrackHistory) -> MotionFeatures:
        """Compute comprehensive motion features from track history."""
        if len(history) == 0:
            return MotionFeatures()

        if len(history) == 1:
            return MotionFeatures(
                pixel_velocity=0.0,
                mean_velocity=0.0,
                max_velocity=0.0,
                recent_velocity=0.0,
                acceleration=0.0,
                direction_rad=0.0,
                displacement=0.0,
                variance=0.0,
                stationary_duration=0.0,
                movement_duration=0.0,
                vertical_velocity=0.0,
                dt=0.0,
            )

        velocities: List[float] = list(history.velocities)
        cur_velocity = velocities[-1]
        cur_accel = history.accelerations[-1]
        cur_vy = history.vertical_velocities[-1]
        dt = history.timestamps[-1] - history.timestamps[-2]

        # Recent velocity (short window of last 3-5 frames)
        recent_n = min(5, len(velocities))
        recent_slice = velocities[-recent_n:]
        recent_velocity = float(np.mean(recent_slice))

        # Mean and max velocity across the active history buffer
        mean_velocity = float(np.mean(velocities))
        max_velocity = float(np.max(velocities))
        variance = float(np.var(velocities)) if len(velocities) > 1 else 0.0

        # Net displacement from oldest point in buffer to current
        oldest_cx, oldest_cy = history.centers[0]
        cur_cx, cur_cy = history.centers[-1]
        net_dx = cur_cx - oldest_cx
        net_dy = cur_cy - oldest_cy
        displacement = float(math.hypot(net_dx, net_dy))

        # Direction of instantaneous displacement
        prev_cx, prev_cy = history.centers[-2]
        step_dx = cur_cx - prev_cx
        step_dy = cur_cy - prev_cy
        direction_rad = float(math.atan2(step_dy, step_dx))

        # Calculate continuous stationary and movement durations
        stationary_duration, movement_duration = self._compute_durations(history)

        return MotionFeatures(
            pixel_velocity=float(cur_velocity),
            mean_velocity=mean_velocity,
            max_velocity=max_velocity,
            recent_velocity=recent_velocity,
            acceleration=float(cur_accel),
            direction_rad=direction_rad,
            displacement=displacement,
            variance=variance,
            stationary_duration=stationary_duration,
            movement_duration=movement_duration,
            vertical_velocity=float(cur_vy),
            dt=float(dt),
        )

    def _compute_durations(self, history: TrackHistory) -> Tuple[float, float]:
        """Compute contiguous stationary duration and movement duration in seconds."""
        if len(history) < 2:
            return 0.0, 0.0

        timestamps = list(history.timestamps)
        velocities = list(history.velocities)
        cur_time = timestamps[-1]

        stationary_duration = 0.0
        if velocities[-1] <= self.config.standing.max_velocity:
            stat_start_idx = len(velocities) - 1
            while stat_start_idx >= 0 and velocities[stat_start_idx] <= self.config.standing.max_velocity:
                stat_start_idx -= 1
            stat_start_idx += 1
            stationary_duration = max(0.0, cur_time - timestamps[stat_start_idx])

        movement_duration = 0.0
        if velocities[-1] >= self.config.walking.min_velocity:
            mov_start_idx = len(velocities) - 1
            while mov_start_idx >= 0 and velocities[mov_start_idx] >= self.config.walking.min_velocity:
                mov_start_idx -= 1
            mov_start_idx += 1
            movement_duration = max(0.0, cur_time - timestamps[mov_start_idx])

        return stationary_duration, movement_duration
