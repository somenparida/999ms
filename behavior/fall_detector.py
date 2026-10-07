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
        # 1. Require sufficient history to avoid tracker initialization jitter
        if len(history) < 5 or (history.timestamps[-1] - history.timestamps[0]) < 0.25:
            return False, 0.0, [], None

        cur_time = history.timestamps[-1]

        # 2. Check cooldown
        if track_id in self._last_fall_time:
            if cur_time - self._last_fall_time[track_id] < self.config.cooldown_seconds:
                return False, 0.0, ["Fall detection cooldown active"], None

        # 3. Filter observations within the detection window
        window_start = cur_time - self.config.detection_window_seconds
        timestamps = list(history.timestamps)
        indices = [i for i, t in enumerate(timestamps) if t >= window_start]
        if len(indices) < 5:
            return False, 0.0, [], None

        # Split window into early (pre-fall baseline) and late (impact/posture collapse)
        half = max(2, len(indices) // 2)
        early_indices = indices[:half]
        late_indices = indices[half:]

        latest_bbox = history.bboxes[-1]
        early_bboxes = [history.bboxes[i] for i in early_indices]
        late_bboxes = [history.bboxes[i] for i in late_indices]

        # 4. Posture and vertical extent analysis
        mean_early_ar = float(np.mean([b.aspect_ratio for b in early_bboxes]))
        mean_late_ar = float(np.mean([b.aspect_ratio for b in late_bboxes]))
        mean_early_h = float(np.mean([b.height for b in early_bboxes]))
        mean_late_h = float(np.mean([b.height for b in late_bboxes]))

        ar_ratio = mean_late_ar / max(0.1, mean_early_ar)
        height_ratio = mean_late_h / max(1.0, mean_early_h)

        # Check torso inclination if pose is available
        torso_collapsed = False
        if pose.available and pose.torso_angle_deg >= 50.0:
            torso_collapsed = True

        posture_thresh = self.config.posture_change_ratio_min
        aspect_ratio_collapsed = (ar_ratio >= posture_thresh) or (mean_early_ar <= 0.75 and latest_bbox.aspect_ratio >= 0.90)
        height_collapsed = (height_ratio <= 0.70)
        has_collapsed_posture = aspect_ratio_collapsed or height_collapsed or torso_collapsed

        # STRICT VETO 1: Upright posture veto
        # If the person is still an upright vertical rectangle without significant height loss or torso tilt
        if not has_collapsed_posture and latest_bbox.aspect_ratio <= 0.75 and height_ratio > 0.78:
            return False, 0.0, [], None

        # STRICT VETO 2: Active running / high continuous motion veto
        # A fallen person does not continue sprinting across the camera view
        recent_vel = motion.recent_velocity
        current_vel = motion.pixel_velocity
        if (recent_vel > 22.0 or current_vel > 26.0) and latest_bbox.aspect_ratio < 0.95 and not torso_collapsed:
            return False, 0.0, [], None

        # 5. Evaluate downward vertical velocity spike
        vert_vels = [history.vertical_velocities[i] for i in indices]
        max_downward_vy = float(np.max(vert_vels))
        vy_thresh = self.config.min_downward_velocity

        if max_downward_vy >= vy_thresh:
            s_vertical = min(1.0, max_downward_vy / (vy_thresh * 1.5))
        else:
            s_vertical = max(0.0, max_downward_vy / vy_thresh * 0.4)

        # 6. Evaluate acceleration spike during the descent
        accels = [history.accelerations[i] for i in indices]
        max_accel = float(np.max(np.abs(accels)))
        accel_thresh = self.config.min_downward_acceleration

        if max_accel >= accel_thresh:
            s_accel = min(1.0, max_accel / (accel_thresh * 1.5))
        else:
            s_accel = max(0.0, max_accel / accel_thresh * 0.4)

        # 7. Posture collapse score
        if has_collapsed_posture:
            collapse_magnitude = max(ar_ratio / posture_thresh, (1.0 - height_ratio) / 0.35)
            s_posture = min(1.0, 0.65 + 0.35 * min(1.0, collapse_magnitude))
        else:
            s_posture = 0.0

        # 8. Post-fall stability (cessation of significant movement)
        vel_max = self.config.post_fall_velocity_max
        if recent_vel <= vel_max:
            s_post_fall = min(1.0, 1.0 - (recent_vel / (vel_max * 2.0)))
        elif recent_vel <= vel_max * 2.0:
            s_post_fall = max(0.0, 1.0 - (recent_vel / (vel_max * 2.0)))
        else:
            s_post_fall = 0.0

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
        if has_collapsed_posture:
            reasons.append(f"posture collapse to horizontal (aspect ratio change {mean_early_ar:.2f} -> {mean_late_ar:.2f}, height ratio {height_ratio:.2f})")
        if recent_vel <= vel_max:
            reasons.append(f"low post-fall movement ({recent_vel:.1f} px/s <= {vel_max:.1f})")

        # Threshold check:
        # A genuine fall MUST have confirmed posture collapse AND kinetic descent/impact AND fall_score >= threshold
        detected = False
        event: Optional[BehaviorEvent] = None

        if (
            has_collapsed_posture
            and (max_downward_vy >= vy_thresh or max_accel >= accel_thresh)
            and fall_score >= self.config.possible_fall_threshold
            and len(reasons) >= 2
        ):
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
                    "height_ratio": round(height_ratio, 2),
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
