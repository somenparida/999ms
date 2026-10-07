"""
Warehouse Sentinel - Fall Detection
Evaluates temporal kinematics across a sliding window to detect genuine falls
(standing/walking -> downward velocity spike -> posture collapse -> post-fall stillness)
while avoiding false positives from intentional lying down or normal sitting.
"""

from __future__ import annotations
import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from .schemas import (
    ActivityType,
    EventType,
    Severity,
    MotionFeatures,
    PoseFeatures,
    BehaviorEvent,
)
from .temporal_buffer import TrackHistory
from .config import FallDetectionConfig

logger = logging.getLogger(__name__)


class FallDetector:
    """Multi-stage temporal human fall detector."""

    def __init__(self, config: FallDetectionConfig):
        self.config = config
        self._last_fall_time: Dict[int, float] = {}

    def analyze(
        self,
        track_id: int,
        history: TrackHistory,
        motion: MotionFeatures,
        pose: PoseFeatures,
    ) -> Tuple[bool, float, List[str], Optional[BehaviorEvent]]:
        """
        Analyze temporal history for fall pattern.
        Returns:
            (detected, fall_score, reasons, event)
        """
        if len(history) < 4:
            return False, 0.0, [], None

        cur_time = history.timestamps[-1]

        # Check cooldown
        if track_id in self._last_fall_time:
            if cur_time - self._last_fall_time[track_id] < self.config.cooldown_seconds:
                return False, 0.0, ["Fall detection cooldown active"], None

        # Filter observations within the detection window
        window_start = cur_time - self.config.detection_window_seconds
        timestamps = list(history.timestamps)
        indices = [i for i, t in enumerate(timestamps) if t >= window_start]
        if len(indices) < 4:
            return False, 0.0, [], None

        # 1. Evaluate downward vertical velocity spike
        vert_vels = [history.vertical_velocities[i] for i in indices]
        max_downward_vy = float(np.max(vert_vels))

        vy_thresh = self.config.min_downward_velocity
        if max_downward_vy >= vy_thresh:
            s_vertical = min(1.0, max_downward_vy / (vy_thresh * 1.5))
        else:
            s_vertical = max(0.0, max_downward_vy / vy_thresh * 0.5)

        # 2. Evaluate acceleration spike during the descent
        accels = [history.accelerations[i] for i in indices]
        max_accel = float(np.max(np.abs(accels)))
        accel_thresh = self.config.min_downward_acceleration
        if max_accel >= accel_thresh:
            s_accel = min(1.0, max_accel / (accel_thresh * 1.5))
        else:
            s_accel = max(0.0, max_accel / accel_thresh * 0.5)

        # 3. Evaluate posture change (aspect ratio / height collapse)
        # Compare early window bounding boxes/poses to latest
        half = max(1, len(indices) // 2)
        early_indices = indices[:half]
        late_indices = indices[half:]

        early_ars = [history.bboxes[i].aspect_ratio for i in early_indices]
        late_ars = [history.bboxes[i].aspect_ratio for i in late_indices]

        mean_early_ar = float(np.mean(early_ars))
        mean_late_ar = float(np.mean(late_ars))

        # Check if subject was originally upright and is now horizontal
        ar_ratio = mean_late_ar / max(0.1, mean_early_ar)

        # Also check torso inclination change if pose is available
        torso_collapsed = False
        if pose.available and pose.torso_angle_deg >= 55.0:
            torso_collapsed = True

        posture_thresh = self.config.posture_change_ratio_min
        if ar_ratio >= posture_thresh or torso_collapsed:
            s_posture = min(1.0, 0.6 + 0.4 * (ar_ratio / posture_thresh))
        else:
            s_posture = max(0.0, (ar_ratio - 1.0) / (posture_thresh - 1.0)) if posture_thresh > 1.0 else 0.0

        # 4. Evaluate post-fall stability (cessation of significant movement)
        recent_vel = motion.recent_velocity
        vel_max = self.config.post_fall_velocity_max
        if recent_vel <= vel_max:
            s_post_fall = min(1.0, 1.0 - (recent_vel / (vel_max * 2.0)))
        else:
            s_post_fall = max(0.0, 1.0 - (recent_vel / (vel_max * 3.0)))

        # Composite score
        w = self.config.weights
        fall_score = (
            w.vertical_motion * s_vertical
            + w.posture_change * s_posture
            + w.acceleration * s_accel
            + w.post_fall_stability * s_post_fall
        )
        fall_score = round(float(np.clip(fall_score, 0.0, 1.0)), 4)

        # Collect explainable reasons
        reasons = []
        if max_downward_vy >= vy_thresh:
            reasons.append(f"rapid downward movement ({max_downward_vy:.1f} px/s >= {vy_thresh:.1f})")
        if max_accel >= accel_thresh:
            reasons.append(f"impact acceleration spike ({max_accel:.1f} px/s² >= {accel_thresh:.1f})")
        if ar_ratio >= posture_thresh or torso_collapsed:
            reasons.append(f"posture transition to horizontal (aspect ratio change {mean_early_ar:.2f} -> {mean_late_ar:.2f})")
        if recent_vel <= vel_max:
            reasons.append(f"low post-fall movement ({recent_vel:.1f} px/s <= {vel_max:.1f})")

        # Threshold check
        detected = False
        event: Optional[BehaviorEvent] = None

        if fall_score >= self.config.possible_fall_threshold and len(reasons) >= 2:
            detected = True
            self._last_fall_time[track_id] = cur_time

            if fall_score >= self.config.fall_detected_threshold:
                event_type = EventType.FALL_DETECTED
                severity = Severity.CRITICAL
            else:
                event_type = EventType.POSSIBLE_FALL
                severity = Severity.HIGH

            event = BehaviorEvent(
                event_type=event_type,
                track_id=track_id,
                timestamp=cur_time,
                confidence=fall_score,
                severity=severity,
                reason=reasons,
                details={
                    "max_downward_velocity": round(max_downward_vy, 2),
                    "max_acceleration": round(max_accel, 2),
                    "aspect_ratio_change": round(ar_ratio, 2),
                    "post_fall_velocity": round(recent_vel, 2),
                    "composite_fall_score": fall_score,
                },
            )
            logger.warning(
                f"[{cur_time:.2f}] Track {track_id} EVENT: {event_type} "
                f"(confidence={fall_score:.2f}, severity={severity})"
            )

        return detected, fall_score, reasons, event

    def remove_track(self, track_id: int) -> None:
        if track_id in self._last_fall_time:
            del self._last_fall_time[track_id]

    def clear(self) -> None:
        self._last_fall_time.clear()
