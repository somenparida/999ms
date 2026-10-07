"""Detection package for Autonomous Vision & Behaviour Understanding System."""

from typing import Any

__all__ = [
    "YOLODetector",
    "VideoDetector",
    "PersonTracker",
    "to_behavior_engine_kwargs",
    "dispatch_to_behavior_engine",
]


def __getattr__(name: str) -> Any:
    """Lazy import to avoid circular or runpy module pre-load warnings."""
    if name == "YOLODetector":
        from detection.detector import YOLODetector
        return YOLODetector
    if name == "VideoDetector":
        from detection.video_detector import VideoDetector
        return VideoDetector
    if name == "PersonTracker":
        from detection.tracker import PersonTracker
        return PersonTracker
    if name == "to_behavior_engine_kwargs":
        from detection.tracker import to_behavior_engine_kwargs
        return to_behavior_engine_kwargs
    if name == "dispatch_to_behavior_engine":
        from detection.tracker import dispatch_to_behavior_engine
        return dispatch_to_behavior_engine
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
