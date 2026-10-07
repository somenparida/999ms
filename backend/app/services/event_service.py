from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.event import Event
from app.models.evidence import Evidence
from app.models.behaviour import Behaviour
from app.models.track_position import TrackPosition
from app.core.logging import logger

class EventService:
    @staticmethod
    def determine_severity(behaviour_type: str, classification: str) -> str:
        b_type = behaviour_type.lower()
        if "fall" in b_type or "critical" in b_type or "weapon" in b_type:
            return "critical"
        elif "restricted" in b_type or "boundary" in b_type or "entry" in b_type:
            return "high"
        elif "inactivity" in b_type or "loitering" in b_type or "running" in b_type:
            return "medium"
        else:
            return "low" if classification == "normal" else "medium"

    @staticmethod
    def create_event_from_behaviour(db: Session, behaviour: Behaviour) -> Event:
        # 1. Check idempotency: avoid duplicate event for same behaviour
        existing_event = db.query(Event).filter(
            Event.video_id == behaviour.video_id,
            Event.track_id == behaviour.track_id,
            Event.behaviour_id == behaviour.id
        ).first()

        if existing_event:
            return existing_event

        severity = EventService.determine_severity(behaviour.behaviour_type, behaviour.classification)

        event = Event(
            video_id=behaviour.video_id,
            track_id=behaviour.track_id,
            behaviour_id=behaviour.id,
            event_type=behaviour.behaviour_type,
            severity=severity,
            start_time=behaviour.start_time,
            end_time=behaviour.end_time,
            confidence=behaviour.confidence,
            reason=behaviour.reason or f"Abnormal behaviour '{behaviour.behaviour_type}' detected for track {behaviour.track_id}",
            status="detected",
            metadata_json=behaviour.metadata_json or {}
        )
        db.add(event)
        db.flush()

        # 2. Automatically generate evidence items for this event
        # Find position closest to start_time for this track
        position = db.query(TrackPosition).filter(
            TrackPosition.track_id == behaviour.track_id,
            TrackPosition.timestamp >= behaviour.start_time
        ).order_by(TrackPosition.timestamp.asc()).first()

        frame_num = position.frame_number if position else 0
        timestamp = position.timestamp if position else behaviour.start_time

        # Bounding box evidence item
        if position:
            bbox_evidence = Evidence(
                event_id=event.id,
                evidence_type="bounding_box",
                timestamp=timestamp,
                frame_number=frame_num,
                description=f"Bounding box location at timestamp {timestamp:.2f}s",
                metadata_json={
                    "bbox": [position.x, position.y, position.width, position.height],
                    "center": [position.center_x, position.center_y],
                    "confidence": position.confidence
                }
            )
            db.add(bbox_evidence)

        # Trajectory evidence item
        traj_positions = db.query(TrackPosition).filter(
            TrackPosition.track_id == behaviour.track_id
        ).order_by(TrackPosition.timestamp.asc()).all()

        if traj_positions:
            coords = [[p.center_x, p.center_y, p.timestamp] for p in traj_positions]
            traj_evidence = Evidence(
                event_id=event.id,
                evidence_type="trajectory",
                timestamp=timestamp,
                frame_number=frame_num,
                description=f"Track trajectory path containing {len(coords)} waypoints",
                metadata_json={"trajectory": coords}
            )
            db.add(traj_evidence)

        db.commit()
        db.refresh(event)
        logger.info(f"Generated Event ID {event.id} ({event.event_type}, severity={event.severity}) for Video ID {behaviour.video_id}")
        return event

    @staticmethod
    def get_events_for_video(db: Session, video_id: int) -> List[Event]:
        return db.query(Event).filter(Event.video_id == video_id).order_by(Event.start_time.asc()).all()

    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Optional[Event]:
        return db.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def update_event_status(db: Session, event_id: int, new_status: str) -> Optional[Event]:
        event = EventService.get_event_by_id(db, event_id)
        if not event:
            return None
        event.status = new_status
        db.commit()
        db.refresh(event)
        logger.info(f"Updated Event ID {event_id} status to {new_status}")
        return event
