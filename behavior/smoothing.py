"""
Warehouse Sentinel - Temporal Smoothing
Applies recency-weighted majority voting across a rolling prediction window
to eliminate single-frame classification flicker and transient noise.
"""

from __future__ import annotations
from collections import deque, defaultdict
from typing import Dict, Tuple
import numpy as np

from .schemas import ActivityType, ActivityPrediction
from .config import SmoothingConfig


class TemporalSmoother:
    """Per-track rolling window temporal prediction smoother."""

    def __init__(self, config: SmoothingConfig):
        self.config = config
        self._windows: Dict[int, deque[Tuple[float, ActivityPrediction]]] = defaultdict(
            lambda: deque(maxlen=self.config.window_size)
        )

    def smooth(
        self,
        track_id: int,
        timestamp: float,
        prediction: ActivityPrediction,
    ) -> ActivityPrediction:
        """Add prediction to track history and return weighted smoothed activity."""
        window = self._windows[track_id]
        window.append((timestamp, prediction))

        if len(window) == 1:
            return prediction

        # Recency-weighted majority voting
        scores: Dict[ActivityType, float] = defaultdict(float)
        total_weight = 0.0
        n = len(window)

        for i, (_, pred) in enumerate(window):
            # Recency weight: decay^(n - 1 - i)
            # Most recent frame has weight 1.0, older frames have weight < 1.0
            weight = (self.config.recency_weight_decay ** (n - 1 - i)) * pred.confidence
            scores[pred.activity] += weight
            total_weight += weight

        if total_weight < 1e-4:
            return prediction

        # Pick winning activity
        best_activity = max(scores.keys(), key=lambda act: scores[act])
        smoothed_conf = scores[best_activity] / total_weight

        # Combine explanation reasons
        combined_reasons = list(prediction.reasons)
        if best_activity != prediction.activity:
            combined_reasons.append(
                f"Smoothed from raw {prediction.activity.value} to {best_activity.value} via majority voting"
            )

        return ActivityPrediction(
            activity=best_activity,
            confidence=round(min(1.0, float(smoothed_conf)), 4),
            reasons=combined_reasons,
        )

    def remove_track(self, track_id: int) -> None:
        """Clear smoothing history for track."""
        if track_id in self._windows:
            del self._windows[track_id]

    def clear(self) -> None:
        """Clear all smoothing windows."""
        self._windows.clear()
