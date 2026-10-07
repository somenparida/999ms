"""
Warehouse Sentinel - Behavior Intelligence Engine
Member 2 Subsystem Public Interface (HackNex 2026)

Orchestrates temporal buffering, motion/pose feature extraction,
rule-based activity classification, temporal smoothing, state management,
fall detection, and structured event dispatching.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .schemas import (
    ActivityType,
    BoundingBox,
    Keypoint,
    MotionFeatures,
    PoseFeatures,
    ActivityTransition,
    BehaviorEvent,
    BehaviorResult,
)
from .config import BehaviorEngineConfig, load_config
from .temporal_buffer import TemporalBuffer
from .motion_analyzer import MotionAnalyzer
from .pose_analyzer import PoseAnalyzer
from .activity_classifier import ActivityClassifier, RuleBasedActivityClassifier
from .smoothing import TemporalSmoother
from .state_manager import StateManager
from .fall_detector import FallDetector

logger = logging.getLogger("behavior_engine")


class BehaviorEngine:
    """Black-box Behavior Intelligence Engine for Warehouse Sentinel."""

    def __init__(
        self,
        config: Optional[Union[BehaviorEngineConfig, str, Path, Dict[str, Any]]] = None,
        classifier: Optional[ActivityClassifier] = None,
    ):
        # Resolve configuration
        if config is None:
            self.config = load_config()
        elif isinstance(config, (str, Path)):
            self.config = load_config(config)
        elif isinstance(config, dict):
            self.config = BehaviorEngineConfig.from_dict(config)
        elif isinstance(config, BehaviorEngineConfig):
            self.config = config
        else:
            raise TypeError(f"Unsupported config type: {type(config)}")

        # Initialize subsystem pipeline components
        self.buffer = TemporalBuffer(self.config.history)
        self.motion_analyzer = MotionAnalyzer(self.config.motion)
        self.pose_analyzer = PoseAnalyzer(self.config.pose)
        self.classifier: ActivityClassifier = (
            classifier if classifier is not None else RuleBasedActivityClassifier(self.config)
        )
        self.smoother = TemporalSmoother(self.config.smoothing)
        self.state_manager = StateManager(self.config)
        self.fall_detector = FallDetector(self.config.fall_detection)

    def update(
        self,
        track_id: int,
        timestamp: float,
        bbox: Any,
        keypoints: Optional[Any] = None,
        detection_confidence: float = 1.0,
    ) -> BehaviorResult:
        """
        Process a new observation for a tracked subject.

        Args:
            track_id: Unique persistent ID assigned to the tracked person.
            timestamp: Observation timestamp in seconds (monotonic).
            bbox: Bounding box [x1, y1, x2, y2].
            keypoints: Optional list of 17 keypoints [[x, y, conf], ...].
            detection_confidence: Detector confidence score [0.0 - 1.0].

        Returns:
            BehaviorResult containing classified activity, confidence, duration,
            transitions, and any behavioral events.
        """
        # 1. Parse and validate inputs
        parsed_bbox = (
            bbox if isinstance(bbox, BoundingBox) else BoundingBox.from_iterable(bbox)
        )

        parsed_kpts: Optional[List[Keypoint]] = None
        if keypoints is not None:
            try:
                parsed_kpts = [
                    kp if isinstance(kp, Keypoint) else Keypoint.from_iterable(kp)
                    for kp in keypoints
                ]
            except Exception as e:
                logger.debug(f"Track {track_id} keypoint parsing fallback: {e}")
                parsed_kpts = None

        # 2. Update temporal buffer
        history = self.buffer.update(
            track_id=track_id,
            timestamp=timestamp,
            bbox=parsed_bbox,
            keypoints=parsed_kpts,
            confidence=detection_confidence,
        )

        # 3. Extract motion and pose features
        motion_features = self.motion_analyzer.extract_features(history)
        pose_features = self.pose_analyzer.extract_features(parsed_kpts, parsed_bbox)

        # 4. Activity classification
        raw_pred = self.classifier.predict(
            motion=motion_features,
            pose=pose_features,
            detection_confidence=detection_confidence,
        )

        # 5. Temporal smoothing
        smoothed_pred = self.smoother.smooth(
            track_id=track_id,
            timestamp=timestamp,
            prediction=raw_pred,
        )

        # 6. Fall detection analysis
        fall_detected, fall_score, fall_reasons, fall_event = self.fall_detector.analyze(
            track_id=track_id,
            history=history,
            motion=motion_features,
            pose=pose_features,
        )

        # Determine proposed activity
        if fall_detected:
            proposed_activity = ActivityType.FALLING
            proposed_confidence = fall_score
        else:
            proposed_activity = smoothed_pred.activity
            proposed_confidence = smoothed_pred.confidence

        # 7. State management & transition tracking
        (
            current_activity,
            prev_activity,
            duration,
            transition,
            state_event,
        ) = self.state_manager.update(
            track_id=track_id,
            timestamp=timestamp,
            proposed_activity=proposed_activity,
            confidence=proposed_confidence,
        )

        # 8. Event arbitration: prioritize fall events over standard state change events
        active_event: Optional[BehaviorEvent] = fall_event if fall_event is not None else state_event

        # 9. Structured logging
        logger.debug(
            f"[{timestamp:.2f}] Track {track_id} "
            f"Activity: {current_activity.value} "
            f"Confidence: {proposed_confidence:.2f} "
            f"Velocity: {motion_features.pixel_velocity:.1f} px/s"
        )

        return BehaviorResult(
            track_id=track_id,
            timestamp=timestamp,
            activity=current_activity,
            confidence=proposed_confidence,
            previous_activity=prev_activity,
            activity_duration=duration,
            transition=transition,
            motion_features=motion_features,
            pose_features=pose_features,
            event=active_event,
        )

    def remove_track(self, track_id: int) -> bool:
        """Remove all tracking history and state for a person (e.g. on exit from frame)."""
        b_res = self.buffer.remove_track(track_id)
        self.smoother.remove_track(track_id)
        self.state_manager.remove_track(track_id)
        self.fall_detector.remove_track(track_id)
        return b_res

    def get_track_state(self, track_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve current activity state and duration for a track."""
        return self.state_manager.get_track_state(track_id)

    def reset(self) -> None:
        """Reset the behavior engine to its initial state."""
        self.buffer.clear()
        self.smoother.clear()
        self.state_manager.clear()
        self.fall_detector.clear()
        logger.info("BehaviorEngine state reset")
