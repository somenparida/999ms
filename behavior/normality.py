"""
Warehouse Sentinel - Normality Intelligence Layer
Provides explainable normal vs. abnormal behavioral classification based on
activity type, temporal duration, and critical transition sequences.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union, Dict, Any

from .schemas import ActivityType, BehaviorStatus, Severity
from .config import NormalityConfig


@dataclass
class NormalityResult:
    """Result of normal vs abnormal behavioral evaluation."""
    status: BehaviorStatus
    severity: Severity
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "severity": self.severity.value,
            "reason": self.reason,
        }


class NormalityClassifier:
    """Rule-based, explainable behavioral normality evaluator."""

    def __init__(self, config: Optional[NormalityConfig] = None):
        self.config = config or NormalityConfig()

    def classify(
        self,
        activity: Union[ActivityType, str],
        duration: float,
        previous_activity: Optional[Union[ActivityType, str]] = None,
        has_fallen: bool = False,
    ) -> NormalityResult:
        """
        Evaluate if an activity observation is NORMAL, POTENTIALLY_UNUSUAL, or ABNORMAL.

        Args:
            activity: Current classified activity.
            duration: Contiguous duration in seconds of current activity.
            previous_activity: Previous activity before the last state transition.
            has_fallen: Boolean indicating if this person experienced a fall during this incident.

        Returns:
            NormalityResult(status, severity, reason)
        """
        # Convert strings to ActivityType if needed
        act = ActivityType(activity) if isinstance(activity, str) else activity
        prev_act = (
            ActivityType(previous_activity)
            if isinstance(previous_activity, str) and previous_activity is not None
            else previous_activity
        )

        # 1. UNKNOWN activity
        if act == ActivityType.UNKNOWN:
            return NormalityResult(
                status=BehaviorStatus.UNKNOWN,
                severity=Severity.NONE,
                reason=None,
            )

        # 2. FALLING is always high-severity ABNORMAL
        if act == ActivityType.FALLING:
            return NormalityResult(
                status=BehaviorStatus.ABNORMAL,
                severity=Severity.HIGH,
                reason="Possible fall detected",
            )

        # 3. Special Case: LYING following a fall -> ABNORMAL
        if act == ActivityType.LYING and (prev_act == ActivityType.FALLING or has_fallen):
            return NormalityResult(
                status=BehaviorStatus.ABNORMAL,
                severity=Severity.HIGH,
                reason="Lying following a fall",
            )

        # 4. Standard LYING (not following a fall)
        if act == ActivityType.LYING:
            if duration > self.config.prolonged_lying_seconds:
                return NormalityResult(
                    status=BehaviorStatus.POTENTIALLY_UNUSUAL,
                    severity=Severity.LOW,
                    reason="Prolonged lying",
                )
            return NormalityResult(
                status=BehaviorStatus.NORMAL,
                severity=Severity.NONE,
                reason=None,
            )

        # 5. BENDING (normally acceptable, prolonged is POTENTIALLY_UNUSUAL)
        if act == ActivityType.BENDING:
            if duration > self.config.prolonged_bending_seconds:
                return NormalityResult(
                    status=BehaviorStatus.POTENTIALLY_UNUSUAL,
                    severity=Severity.LOW,
                    reason="Prolonged bending",
                )
            return NormalityResult(
                status=BehaviorStatus.NORMAL,
                severity=Severity.NONE,
                reason=None,
            )

        # 6. CROUCHING (normally acceptable, prolonged is POTENTIALLY_UNUSUAL)
        if act == ActivityType.CROUCHING:
            if duration > self.config.prolonged_crouching_seconds:
                return NormalityResult(
                    status=BehaviorStatus.POTENTIALLY_UNUSUAL,
                    severity=Severity.LOW,
                    reason="Prolonged crouching",
                )
            return NormalityResult(
                status=BehaviorStatus.NORMAL,
                severity=Severity.NONE,
                reason=None,
            )

        # 7. Standard expected activities: STANDING, WALKING, RUNNING, SITTING
        return NormalityResult(
            status=BehaviorStatus.NORMAL,
            severity=Severity.NONE,
            reason=None,
        )


def classify_behavior(
    activity: Union[ActivityType, str],
    duration: float,
    previous_activity: Optional[Union[ActivityType, str]] = None,
    has_fallen: bool = False,
    config: Optional[NormalityConfig] = None,
) -> NormalityResult:
    """Convenience functional interface for behavioral normality classification."""
    classifier = NormalityClassifier(config)
    return classifier.classify(
        activity=activity,
        duration=duration,
        previous_activity=previous_activity,
        has_fallen=has_fallen,
    )
