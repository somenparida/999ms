"""
Warehouse Sentinel - Behavior Intelligence Configuration
Loads and validates engine configuration with strong typing and default fallbacks.
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


@dataclass
class HistoryConfig:
    max_seconds: float = 5.0
    stale_track_seconds: float = 2.0
    max_frames: int = 150


@dataclass
class StandingMotionConfig:
    max_velocity: float = 8.0


@dataclass
class WalkingMotionConfig:
    min_velocity: float = 6.0
    max_velocity: float = 28.0


@dataclass
class RunningMotionConfig:
    min_velocity: float = 26.0
    min_acceleration: float = 15.0


@dataclass
class MotionConfig:
    standing: StandingMotionConfig = field(default_factory=StandingMotionConfig)
    walking: WalkingMotionConfig = field(default_factory=WalkingMotionConfig)
    running: RunningMotionConfig = field(default_factory=RunningMotionConfig)
    stationary_variance_max: float = 12.0
    prolonged_inactivity_seconds: float = 60.0


@dataclass
class PoseConfig:
    min_keypoint_confidence: float = 0.35
    min_valid_keypoint_ratio: float = 0.40
    lying_aspect_ratio_min: float = 1.15
    standing_aspect_ratio_max: float = 0.75
    torso_upright_max_deg: float = 35.0
    torso_horizontal_min_deg: float = 60.0
    sitting_knee_angle_max: float = 135.0
    sitting_hip_knee_dy_ratio: float = 0.45
    crouching_knee_angle_max: float = 115.0
    crouching_hip_ankle_dy_ratio: float = 0.35
    bending_torso_angle_min: float = 35.0
    bending_torso_angle_max: float = 75.0
    bending_knee_angle_min: float = 130.0


@dataclass
class SmoothingConfig:
    window_size: int = 7
    min_duration_seconds: float = 0.40
    recency_weight_decay: float = 0.85


@dataclass
class FallWeightsConfig:
    vertical_motion: float = 0.35
    posture_change: float = 0.25
    acceleration: float = 0.20
    post_fall_stability: float = 0.20


@dataclass
class FallDetectionConfig:
    detection_window_seconds: float = 2.5
    min_downward_velocity: float = 40.0
    min_downward_acceleration: float = 30.0
    posture_change_ratio_min: float = 1.40
    post_fall_velocity_max: float = 8.0
    post_fall_duration_min: float = 0.60
    weights: FallWeightsConfig = field(default_factory=FallWeightsConfig)
    possible_fall_threshold: float = 0.60
    fall_detected_threshold: float = 0.82
    cooldown_seconds: float = 5.0


@dataclass
class ClassifierConfig:
    min_detection_confidence: float = 0.45
    missing_pose_confidence_penalty: float = 0.15


@dataclass
class NormalityConfig:
    prolonged_bending_seconds: float = 30.0
    prolonged_crouching_seconds: float = 30.0
    prolonged_lying_seconds: float = 30.0


@dataclass
class BehaviorEngineConfig:
    history: HistoryConfig = field(default_factory=HistoryConfig)
    motion: MotionConfig = field(default_factory=MotionConfig)
    pose: PoseConfig = field(default_factory=PoseConfig)
    smoothing: SmoothingConfig = field(default_factory=SmoothingConfig)
    fall_detection: FallDetectionConfig = field(default_factory=FallDetectionConfig)
    classifier: ClassifierConfig = field(default_factory=ClassifierConfig)
    normality: NormalityConfig = field(default_factory=NormalityConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BehaviorEngineConfig:
        history_data = data.get("history", {})
        motion_data = data.get("motion", {})
        pose_data = data.get("pose", {})
        smoothing_data = data.get("smoothing", {})
        fall_data = data.get("fall_detection", {})
        classifier_data = data.get("classifier", {})

        history_cfg = HistoryConfig(
            max_seconds=float(history_data.get("max_seconds", 5.0)),
            stale_track_seconds=float(history_data.get("stale_track_seconds", 2.0)),
            max_frames=int(history_data.get("max_frames", 150)),
        )

        standing_data = motion_data.get("standing", {})
        walking_data = motion_data.get("walking", {})
        running_data = motion_data.get("running", {})

        motion_cfg = MotionConfig(
            standing=StandingMotionConfig(
                max_velocity=float(standing_data.get("max_velocity", 8.0))
            ),
            walking=WalkingMotionConfig(
                min_velocity=float(walking_data.get("min_velocity", 6.0)),
                max_velocity=float(walking_data.get("max_velocity", 28.0)),
            ),
            running=RunningMotionConfig(
                min_velocity=float(running_data.get("min_velocity", 26.0)),
                min_acceleration=float(running_data.get("min_acceleration", 15.0)),
            ),
            stationary_variance_max=float(
                motion_data.get("stationary_variance_max", 12.0)
            ),
            prolonged_inactivity_seconds=float(
                motion_data.get("prolonged_inactivity_seconds", 60.0)
            ),
        )

        pose_cfg = PoseConfig(
            min_keypoint_confidence=float(
                pose_data.get("min_keypoint_confidence", 0.35)
            ),
            min_valid_keypoint_ratio=float(
                pose_data.get("min_valid_keypoint_ratio", 0.40)
            ),
            lying_aspect_ratio_min=float(pose_data.get("lying_aspect_ratio_min", 1.15)),
            standing_aspect_ratio_max=float(
                pose_data.get("standing_aspect_ratio_max", 0.75)
            ),
            torso_upright_max_deg=float(pose_data.get("torso_upright_max_deg", 35.0)),
            torso_horizontal_min_deg=float(
                pose_data.get("torso_horizontal_min_deg", 60.0)
            ),
            sitting_knee_angle_max=float(pose_data.get("sitting_knee_angle_max", 135.0)),
            sitting_hip_knee_dy_ratio=float(
                pose_data.get("sitting_hip_knee_dy_ratio", 0.45)
            ),
            crouching_knee_angle_max=float(pose_data.get("crouching_knee_angle_max", 115.0)),
            crouching_hip_ankle_dy_ratio=float(pose_data.get("crouching_hip_ankle_dy_ratio", 0.35)),
            bending_torso_angle_min=float(pose_data.get("bending_torso_angle_min", 35.0)),
            bending_torso_angle_max=float(pose_data.get("bending_torso_angle_max", 75.0)),
            bending_knee_angle_min=float(pose_data.get("bending_knee_angle_min", 130.0)),
        )

        smoothing_cfg = SmoothingConfig(
            window_size=int(smoothing_data.get("window_size", 7)),
            min_duration_seconds=float(
                smoothing_data.get("min_duration_seconds", 0.40)
            ),
            recency_weight_decay=float(
                smoothing_data.get("recency_weight_decay", 0.85)
            ),
        )

        fall_weights_data = fall_data.get("weights", {})
        fall_weights = FallWeightsConfig(
            vertical_motion=float(fall_weights_data.get("vertical_motion", 0.35)),
            posture_change=float(fall_weights_data.get("posture_change", 0.25)),
            acceleration=float(fall_weights_data.get("acceleration", 0.20)),
            post_fall_stability=float(
                fall_weights_data.get("post_fall_stability", 0.20)
            ),
        )

        fall_cfg = FallDetectionConfig(
            detection_window_seconds=float(
                fall_data.get("detection_window_seconds", 2.5)
            ),
            min_downward_velocity=float(fall_data.get("min_downward_velocity", 40.0)),
            min_downward_acceleration=float(
                fall_data.get("min_downward_acceleration", 30.0)
            ),
            posture_change_ratio_min=float(
                fall_data.get("posture_change_ratio_min", 1.40)
            ),
            post_fall_velocity_max=float(
                fall_data.get("post_fall_velocity_max", 8.0)
            ),
            post_fall_duration_min=float(
                fall_data.get("post_fall_duration_min", 0.60)
            ),
            weights=fall_weights,
            possible_fall_threshold=float(
                fall_data.get("possible_fall_threshold", 0.60)
            ),
            fall_detected_threshold=float(
                fall_data.get("fall_detected_threshold", 0.82)
            ),
            cooldown_seconds=float(fall_data.get("cooldown_seconds", 5.0)),
        )

        classifier_cfg = ClassifierConfig(
            min_detection_confidence=float(
                classifier_data.get("min_detection_confidence", 0.45)
            ),
            missing_pose_confidence_penalty=float(
                classifier_data.get("missing_pose_confidence_penalty", 0.15)
            ),
        )

        normality_data = data.get("normality", {})
        normality_cfg = NormalityConfig(
            prolonged_bending_seconds=float(normality_data.get("prolonged_bending_seconds", 30.0)),
            prolonged_crouching_seconds=float(normality_data.get("prolonged_crouching_seconds", 30.0)),
            prolonged_lying_seconds=float(normality_data.get("prolonged_lying_seconds", 30.0)),
        )

        return cls(
            history=history_cfg,
            motion=motion_cfg,
            pose=pose_cfg,
            smoothing=smoothing_cfg,
            fall_detection=fall_cfg,
            classifier=classifier_cfg,
            normality=normality_cfg,
        )


def load_config(config_path: Optional[str | Path] = None) -> BehaviorEngineConfig:
    """Load configuration from a YAML file or return defaults."""
    if config_path is None:
        # Check standard default locations
        candidate = Path("configs/behavior.yaml")
        if candidate.exists():
            config_path = candidate
        else:
            return BehaviorEngineConfig()

    p = Path(config_path)
    if not p.exists():
        return BehaviorEngineConfig()

    with open(p, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return BehaviorEngineConfig.from_dict(data)
