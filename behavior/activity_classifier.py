"""
Warehouse Sentinel - Activity Classifier
Extensible architecture with base ActivityClassifier and explainable
RuleBasedActivityClassifier without magic numbers.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from .schemas import ActivityType, MotionFeatures, PoseFeatures, ActivityPrediction
from .config import BehaviorEngineConfig


class ActivityClassifier(ABC):
    """Abstract interface for activity classification.

    Designed to allow plugging in future ML/LSTM/GRU/TCN classifiers
    without modifying the rest of the behavior engine.
    """

    @abstractmethod
    def predict(
        self,
        motion: MotionFeatures,
        pose: PoseFeatures,
        detection_confidence: float = 1.0,
    ) -> ActivityPrediction:
        """Classify human activity from extracted motion and pose features."""
        pass


class RuleBasedActivityClassifier(ActivityClassifier):
    """Deterministic, explainable rule-based human activity classifier."""

    def __init__(self, config: BehaviorEngineConfig):
        self.config = config

    def predict(
        self,
        motion: MotionFeatures,
        pose: PoseFeatures,
        detection_confidence: float = 1.0,
    ) -> ActivityPrediction:
        """Classify activity based on kinematic and postural thresholds."""
        reasons: List[str] = []

        # 1. Check for low detection confidence
        if detection_confidence < self.config.classifier.min_detection_confidence:
            return ActivityPrediction(
                activity=ActivityType.UNKNOWN,
                confidence=round(detection_confidence, 4),
                reasons=[
                    f"Low detection confidence ({detection_confidence:.2f} < "
                    f"{self.config.classifier.min_detection_confidence:.2f})"
                ],
            )

        # Base confidence calculation
        base_confidence = min(1.0, detection_confidence)
        if not pose.available:
            base_confidence = max(
                0.2,
                base_confidence - self.config.classifier.missing_pose_confidence_penalty,
            )

        vel = motion.recent_velocity if motion.recent_velocity > 0 else motion.pixel_velocity
        ar = pose.aspect_ratio
        is_horizontal = (
            ar >= self.config.pose.lying_aspect_ratio_min
            or (pose.available and pose.torso_angle_deg >= self.config.pose.torso_horizontal_min_deg)
        )
        is_upright = (
            ar <= self.config.pose.standing_aspect_ratio_max
            or (pose.available and pose.torso_angle_deg <= self.config.pose.torso_upright_max_deg)
        )

        # 2. Check for BENDING (torso tilted forward at waist + straight legs + low/moderate velocity)
        # Bending occurs while standing on feet with straight legs and forward-inclined torso
        if (
            pose.available
            and vel <= self.config.motion.walking.min_velocity
            and self.config.pose.bending_torso_angle_min <= pose.torso_angle_deg <= self.config.pose.bending_torso_angle_max
            and pose.knee_angle_deg >= self.config.pose.bending_knee_angle_min
            and ar < self.config.pose.lying_aspect_ratio_min
        ):
            reasons.append(
                f"Torso tilted forward ({pose.torso_angle_deg:.1f} deg in "
                f"[{self.config.pose.bending_torso_angle_min:.1f}, {self.config.pose.bending_torso_angle_max:.1f}])"
            )
            reasons.append(f"Straight legs maintained (knee angle {pose.knee_angle_deg:.1f} deg >= {self.config.pose.bending_knee_angle_min:.1f} deg)")
            reasons.append(f"Stationary/slow velocity ({vel:.1f} px/s)")
            conf = min(0.95, base_confidence * 0.93)
            return ActivityPrediction(ActivityType.BENDING, round(conf, 4), reasons)

        # 3. Check for LYING (horizontal posture + low velocity)
        if is_horizontal and vel <= self.config.motion.walking.min_velocity:
            reasons.append("Horizontal posture detected")
            if pose.available and pose.torso_angle_deg >= self.config.pose.torso_horizontal_min_deg:
                reasons.append(f"Torso inclination {pose.torso_angle_deg:.1f} deg >= {self.config.pose.torso_horizontal_min_deg:.1f} deg")
            else:
                reasons.append(f"Aspect ratio {ar:.2f} >= {self.config.pose.lying_aspect_ratio_min:.2f}")
            reasons.append(f"Low velocity ({vel:.1f} px/s)")
            conf = min(0.96, base_confidence * (0.95 if pose.available else 0.85))
            return ActivityPrediction(ActivityType.LYING, round(conf, 4), reasons)

        # 4. Check for CROUCHING (deep knee flexion + hips dropped low to ankles + low velocity)
        if (
            pose.available
            and vel <= self.config.motion.standing.max_velocity
            and pose.knee_angle_deg <= self.config.pose.crouching_knee_angle_max
            and (
                (0.0 < pose.hip_ankle_dy_ratio <= self.config.pose.crouching_hip_ankle_dy_ratio)
                or (0.0 < pose.normalized_height <= 0.65)
            )
            and pose.torso_angle_deg <= 45.0
        ):
            reasons.append(f"Deep knee flexion ({pose.knee_angle_deg:.1f} deg <= {self.config.pose.crouching_knee_angle_max:.1f} deg)")
            reasons.append(f"Hips lowered close to ankles (ratio {pose.hip_ankle_dy_ratio:.2f} <= {self.config.pose.crouching_hip_ankle_dy_ratio:.2f})")
            reasons.append(f"Low velocity ({vel:.1f} px/s)")
            conf = min(0.95, base_confidence * 0.93)
            return ActivityPrediction(ActivityType.CROUCHING, round(conf, 4), reasons)

        # 5. Check for SITTING (low velocity + bent knees + upright torso + pose available)
        if (
            pose.available
            and vel <= self.config.motion.standing.max_velocity
            and pose.knee_angle_deg <= self.config.pose.sitting_knee_angle_max
            and pose.torso_angle_deg <= self.config.pose.torso_upright_max_deg
        ):
            reasons.append(f"Bent knee angle ({pose.knee_angle_deg:.1f} deg <= {self.config.pose.sitting_knee_angle_max:.1f} deg)")
            reasons.append(f"Upright torso ({pose.torso_angle_deg:.1f} deg)")
            reasons.append(f"Stationary velocity ({vel:.1f} px/s)")
            conf = min(0.95, base_confidence * 0.92)
            return ActivityPrediction(ActivityType.SITTING, round(conf, 4), reasons)

        # 4. Check for RUNNING (high velocity + upright posture)
        if vel >= self.config.motion.running.min_velocity and is_upright:
            reasons.append(f"High pixel velocity ({vel:.1f} >= {self.config.motion.running.min_velocity:.1f} px/s)")
            reasons.append("Upright body orientation")
            conf = min(0.96, base_confidence * 0.94)
            return ActivityPrediction(ActivityType.RUNNING, round(conf, 4), reasons)

        # 5. Check for WALKING (moderate velocity + upright posture)
        if (
            self.config.motion.walking.min_velocity <= vel < self.config.motion.running.min_velocity
            and is_upright
        ):
            reasons.append(
                f"Moderate velocity ({vel:.1f} px/s in [{self.config.motion.walking.min_velocity:.1f}, {self.config.motion.running.min_velocity:.1f}])"
            )
            reasons.append("Upright trajectory motion")
            conf = min(0.95, base_confidence * 0.92)
            return ActivityPrediction(ActivityType.WALKING, round(conf, 4), reasons)

        # 8. Check for STANDING (low velocity + upright posture)
        if vel <= self.config.motion.standing.max_velocity and is_upright:
            # If pose is available, ensure knees are straight and torso is upright
            if not (
                pose.available
                and (
                    pose.knee_angle_deg <= self.config.pose.sitting_knee_angle_max
                    or pose.torso_angle_deg >= self.config.pose.bending_torso_angle_min
                )
            ):
                reasons.append(f"Low velocity ({vel:.1f} <= {self.config.motion.standing.max_velocity:.1f} px/s)")
                reasons.append("Upright posture")
                conf = min(0.95, base_confidence * 0.92)
                return ActivityPrediction(ActivityType.STANDING, round(conf, 4), reasons)

        # 7. Ambiguous or conflicting signals -> UNKNOWN
        reasons.append(f"Uncertain or conflicting kinematic signals (velocity={vel:.1f}, aspect_ratio={ar:.2f})")
        return ActivityPrediction(
            ActivityType.UNKNOWN,
            round(min(0.50, base_confidence * 0.5), 4),
            reasons,
        )
