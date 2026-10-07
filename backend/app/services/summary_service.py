from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.video import Video
from app.models.track import Track
from app.models.behaviour import Behaviour
from app.models.event import Event
from app.schemas.timeline import TimelineItemResponse
from app.schemas.summary import VideoSummaryResponse

class SummaryService:
    @staticmethod
    def get_timeline(db: Session, video_id: int) -> List[TimelineItemResponse]:
        behaviours = db.query(Behaviour).filter(Behaviour.video_id == video_id).order_by(Behaviour.start_time.asc()).all()
        events = db.query(Event).filter(Event.video_id == video_id).all()

        # Map event by behaviour_id
        event_map = {e.behaviour_id: e for e in events if e.behaviour_id}

        timeline = []
        for b in behaviours:
            ev = event_map.get(b.id)
            track_public_id = b.track.track_id if b.track else b.track_id
            timeline.append(
                TimelineItemResponse(
                    timestamp=round(b.start_time, 2),
                    track_id=track_public_id,
                    type=b.behaviour_type,
                    classification=b.classification,
                    event_id=ev.id if ev else None,
                    severity=ev.severity if ev else None,
                    reason=b.reason or (ev.reason if ev else None),
                    metadata=b.metadata_json or {}
                )
            )

        timeline.sort(key=lambda x: x.timestamp)
        return timeline

    @staticmethod
    def get_summary(db: Session, video_id: int) -> VideoSummaryResponse:
        video = db.query(Video).filter(Video.id == video_id).first()
        duration = video.duration if (video and video.duration) else 0.0

        # Unique tracks
        tracks = db.query(Track).filter(Track.video_id == video_id).all()
        unique_tracks = len(tracks)

        people_count = len([t for t in tracks if t.object_type.lower() == "person"])
        if people_count == 0 and unique_tracks > 0:
            people_count = unique_tracks

        # Behaviours & Events
        behaviours = db.query(Behaviour).filter(Behaviour.video_id == video_id).all()
        normal_events = len([b for b in behaviours if b.classification.lower() == "normal"])
        
        events = db.query(Event).filter(Event.video_id == video_id).all()
        abnormal_events = len(events) if events else len([b for b in behaviours if b.classification.lower() == "abnormal"])

        high_risk_events = len([e for e in events if e.severity in ["high", "critical"]])

        # Average confidence
        confidences = [t.average_confidence for t in tracks if t.average_confidence] + [b.confidence for b in behaviours if b.confidence]
        avg_confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0.90

        return VideoSummaryResponse(
            people_detected=people_count,
            unique_tracks=unique_tracks,
            normal_events=normal_events,
            abnormal_events=abnormal_events,
            high_risk_events=high_risk_events,
            average_confidence=avg_confidence,
            duration=round(duration, 2)
        )
