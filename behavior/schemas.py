"""
Warehouse Sentinel - Behavior Intelligence Schemas
Defines strictly-typed data models for inputs, motion/pose features,
transitions, events, and engine results.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any


class ActivityType(str, Enum):
    STANDING = "STANDING"
    WALKING = "WALKING"
    RUNNING = "RUNNING"
    SITTING = "SITTING"
    CROUCHING = "CROUCHING"
    BENDING = "BENDING"
    LYING = "LYING"
    FALLING = "FALLING"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return self.value


class EventType(str, Enum):
    ACTIVITY_CHANGE = "ACTIVITY_CHANGE"
    POSSIBLE_FALL = "POSSIBLE_FALL"
    FALL_DETECTED = "FALL_DETECTED"
    PROLONGED_INACTIVITY = "PROLONGED_INACTIVITY"

    def __str__(self) -> str:
        return self.value


class BehaviorStatus(str, Enum):
    NORMAL = "NORMAL"
    POTENTIALLY_UNUSUAL = "POTENTIALLY_UNUSUAL"
    ABNORMAL = "ABNORMAL"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return self.value


class Severity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def aspect_ratio(self) -> float:
        """Width to height ratio (W/H). Lying > 1.0, Upright < 0.8."""
        h = self.height
        return (self.width / h) if h > 1e-4 else 0.0

    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2.0

    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2.0

    @property
    def center(self) -> Tuple[float, float]:
        return (self.center_x, self.center_y)

    def to_list(self) -> List[float]:
        return [self.x1, self.y1, self.x2, self.y2]

    @classmethod
    def from_iterable(cls, coords: Any) -> BoundingBox:
        if len(coords) != 4:
            raise ValueError(f"Expected 4 bounding box coordinates, got {len(coords)}")
        return cls(
            x1=float(coords[0]),
            y1=float(coords[1]),
            x2=float(coords[2]),
            y2=float(coords[3]),
        )


@dataclass(frozen=True)
class Keypoint:
    x: float
    y: float
    confidence: float

    @classmethod
    def from_iterable(cls, item: Any) -> Keypoint:
        if len(item) < 2:
            raise ValueError(f"Keypoint requires at least [x, y], got {item}")
        x = float(item[0])
        y = float(item[1])
        conf = float(item[2]) if len(item) > 2 else 1.0
        return cls(x=x, y=y, confidence=conf)


@dataclass
class MotionFeatures:
    pixel_velocity: float = 0.0
    mean_velocity: float = 0.0
    max_velocity: float = 0.0
    recent_velocity: float = 0.0
    acceleration: float = 0.0
    direction_rad: float = 0.0
    displacement: float = 0.0
    variance: float = 0.0
    stationary_duration: float = 0.0
    movement_duration: float = 0.0
    vertical_velocity: float = 0.0
    dt: float = 0.0


@dataclass
class PoseFeatures:
    available: bool = False
    body_width: float = 0.0
    body_height: float = 0.0
    aspect_ratio: float = 0.0
    torso_angle_deg: float = 0.0
    hip_angle_deg: float = 0.0
    knee_angle_deg: float = 0.0
    shoulder_angle_deg: float = 0.0
    vertical_extent: float = 0.0
    horizontal_extent: float = 0.0
    normalized_height: float = 0.0
    hip_ankle_dy_ratio: float = 0.0
    pose_confidence: float = 0.0


@dataclass
class ActivityTransition:
    from_activity: ActivityType
    to_activity: ActivityType
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": str(self.from_activity),
            "to": str(self.to_activity),
            "timestamp": self.timestamp,
        }


@dataclass
class BehaviorEvent:
    event_type: EventType
    track_id: int
    timestamp: float
    confidence: float
    severity: Severity = Severity.MEDIUM
    reason: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": str(self.event_type),
            "track_id": self.track_id,
            "timestamp": self.timestamp,
            "confidence": round(self.confidence, 4),
            "severity": str(self.severity),
            "reason": list(self.reason),
            "details": dict(self.details),
        }


@dataclass
class ActivityPrediction:
    activity: ActivityType
    confidence: float
    reasons: List[str] = field(default_factory=list)


@dataclass
class BehaviorResult:
    track_id: int
    timestamp: float
    activity: ActivityType
    confidence: float
    previous_activity: Optional[ActivityType] = None
    activity_duration: float = 0.0
    transition: Optional[ActivityTransition] = None
    motion_features: Optional[MotionFeatures] = None
    pose_features: Optional[PoseFeatures] = None
    event: Optional[BehaviorEvent] = None
    status: BehaviorStatus = BehaviorStatus.NORMAL
    severity: Severity = Severity.NONE
    status_reason: Optional[str] = None

    @property
    def reasons(self) -> List[str]:
        """Convenience property returning status reason or event reasons as a list."""
        if self.status_reason:
            return [self.status_reason]
        if self.event and self.event.reason:
            return list(self.event.reason)
        return []

    def __getitem__(self, key: str) -> Any:
        """Enable dictionary-style access result['activity']."""
        if key == "duration":
            return self.activity_duration
        if key == "reason":
            return self.status_reason
        if hasattr(self, key):
            val = getattr(self, key)
            if isinstance(val, (ActivityType, EventType, Severity, BehaviorStatus)):
                return val.value
            return val
        raise KeyError(key)

    def to_dict(self) -> Dict[str, Any]:
        """Produce the standard structured representation for downstream consumers."""
        res: Dict[str, Any] = {
            "track_id": self.track_id,
            "timestamp": self.timestamp,
            "activity": self.activity.value,
            "status": self.status.value,
            "severity": self.severity.value,
            "confidence": round(self.confidence, 4),
            "reason": self.status_reason,
            "previous_activity": self.previous_activity.value if self.previous_activity else None,
            "duration": round(self.activity_duration, 2),
            "transition": self.transition.to_dict() if self.transition else None,
            "event": self.event.to_dict() if self.event else None,
        }
        return res
