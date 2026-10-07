"""
Warehouse Sentinel - Activity State Manager
Maintains persistent state machines per track, enforces minimum activity
durations, generates transitions without duplicate events, and detects inactivity.
"""

from __future__ import annotations
import logging
from typing import Dict, Optional, Tuple, Any

from .schemas import (
    ActivityType,
    EventType,
    Severity,
    ActivityTransition,
    BehaviorEvent,
)
from .config import BehaviorEngineConfig

logger = logging.getLogger(__name__)


class TrackState:
    """State record for an individual tracked person."""

    def __init__(self, track_id: int, initial_activity: ActivityType, timestamp: float):
        self.track_id = track_id
        self.current_activity: ActivityType = initial_activity
        self.previous_activity: Optional[ActivityType] = None
        self.activity_start_time: float = timestamp
        self.last_timestamp: float = timestamp

        # Candidate state for minimum-duration hysteresis
        self.candidate_activity: Optional[ActivityType] = None
        self.candidate_first_seen: float = timestamp

        # Inactivity alert flag
        self.inactivity_alert_sent: bool = False

    @property
    def duration(self) -> float:
        return max(0.0, self.last_timestamp - self.activity_start_time)


class StateManager:
    """Manages activity states, transitions, and inactivity tracking across all tracks."""

    def __init__(self, config: BehaviorEngineConfig):
        self.config = config
        self.tracks: Dict[int, TrackState] = {}

    def update(
        self,
        track_id: int,
        timestamp: float,
        proposed_activity: ActivityType,
        confidence: float,
    ) -> Tuple[ActivityType, Optional[ActivityType], float, Optional[ActivityTransition], Optional[BehaviorEvent]]:
        """
        Update the state machine for a track.
        Returns:
            (current_activity, previous_activity, duration, transition, event)
        """
        min_duration = self.config.smoothing.min_duration_seconds
        transition: Optional[ActivityTransition] = None
        event: Optional[BehaviorEvent] = None

        if track_id not in self.tracks:
            # Initialize track
            state = TrackState(track_id, proposed_activity, timestamp)
            self.tracks[track_id] = state
            logger.info(f"[{timestamp:.2f}] Track {track_id} initialized with activity: {proposed_activity}")
            return (
                state.current_activity,
                state.previous_activity,
                0.0,
                None,
                None,
            )

        state = self.tracks[track_id]
        state.last_timestamp = timestamp

        # Check if activity matches current state
        if proposed_activity == state.current_activity:
            state.candidate_activity = None
        else:
            # Emergency/fall transitions commit immediately without waiting for min_duration
            is_emergency = proposed_activity == ActivityType.FALLING

            if state.candidate_activity != proposed_activity:
                state.candidate_activity = proposed_activity
                state.candidate_first_seen = timestamp

            candidate_duration = timestamp - state.candidate_first_seen
            if is_emergency or candidate_duration >= min_duration:
                # Commit state transition
                old_act = state.current_activity
                new_act = state.candidate_activity

                state.previous_activity = old_act
                state.current_activity = new_act
                state.activity_start_time = timestamp
                state.candidate_activity = None
                state.inactivity_alert_sent = False

                transition = ActivityTransition(
                    from_activity=old_act,
                    to_activity=new_act,
                    timestamp=timestamp,
                )

                logger.info(
                    f"[{timestamp:.2f}] Track {track_id} Transition: {old_act} -> {new_act}"
                )

                # Generate ACTIVITY_CHANGE event
                event = BehaviorEvent(
                    event_type=EventType.ACTIVITY_CHANGE,
                    track_id=track_id,
                    timestamp=timestamp,
                    confidence=confidence,
                    severity=Severity.LOW,
                    reason=[f"Transitioned from {old_act.value} to {new_act.value}"],
                    details={
                        "from_activity": old_act.value,
                        "to_activity": new_act.value,
                        "previous_duration": round(state.duration, 2),
                    },
                )

        # Check for prolonged inactivity
        duration = state.duration
        inactivity_thresh = self.config.motion.prolonged_inactivity_seconds
        stationary_activities = {
            ActivityType.STANDING,
            ActivityType.SITTING,
            ActivityType.LYING,
        }

        if (
            state.current_activity in stationary_activities
            and duration >= inactivity_thresh
            and not state.inactivity_alert_sent
        ):
            state.inactivity_alert_sent = True
            logger.warning(
                f"[{timestamp:.2f}] Track {track_id} PROLONGED_INACTIVITY: {duration:.1f}s"
            )
            event = BehaviorEvent(
                event_type=EventType.PROLONGED_INACTIVITY,
                track_id=track_id,
                timestamp=timestamp,
                confidence=0.90,
                severity=Severity.MEDIUM,
                reason=[
                    f"Stationary activity {state.current_activity.value} persisted for {duration:.1f}s "
                    f"(threshold {inactivity_thresh:.1f}s)"
                ],
                details={
                    "activity": state.current_activity.value,
                    "duration": round(duration, 2),
                    "threshold": inactivity_thresh,
                },
            )

        return (
            state.current_activity,
            state.previous_activity,
            round(state.duration, 2),
            transition,
            event,
        )

    def get_track_state(self, track_id: int) -> Optional[Dict[str, Any]]:
        """Return state snapshot for a track."""
        if track_id not in self.tracks:
            return None
        st = self.tracks[track_id]
        return {
            "track_id": track_id,
            "current_activity": st.current_activity.value,
            "previous_activity": st.previous_activity.value if st.previous_activity else None,
            "activity_start_time": st.activity_start_time,
            "duration": round(st.duration, 2),
        }

    def remove_track(self, track_id: int) -> None:
        if track_id in self.tracks:
            del self.tracks[track_id]

    def clear(self) -> None:
        self.tracks.clear()
