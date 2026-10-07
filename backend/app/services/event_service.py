from typing import List, Optional, Union
from sqlalchemy.orm import Session
from app.models.event import Event
from app.models.evidence import Evidence
from app.models.behaviour import Behaviour
from app.models.track_position import TrackPosition
from app.core.logging import logger

class EventService:
    @staticmethod
    def determine_severity(behaviour_type: str, classification: str, explicit_severity: str = None) -> str:
        if explicit_severity and explicit_severity.upper() in ["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            sev = explicit_severity.lower()
            return "medium" if sev == "none" else sev

        b_type = behaviour_type.lower()
        cls = classification.lower()

        if "fall" in b_type or "critical" in b_type or "weapon" in b_type:
            return "critical" if "detected" in b_type else "high"
        elif "restricted" in b_type or "boundary" in b_type or "entry" in b_type:
            return "high"
        elif "inactivity" in b_type or "loitering" in b_type or "running" in b_type or "bending" in b_type or "crouching" in b_type:
            return "medium" if cls == "abnormal" else "low"
        else:
            return "low" if cls == "normal" else "medium"

    @staticmethod
    def create_event_from_behaviour(db: Session, behaviour: Behaviour) -> Event:
        # Check idempotency: avoid duplicate event for same behaviour
        existing_event = db.query(Event).filter(
            Event.video_id == behaviour.video_id,
            Event.track_id == behaviour.track_id,
            Event.behaviour_id == behaviour.id
        ).first()

        if existing_event:
            return existing_event

        meta = behaviour.metadata_json or {}
        explicit_event = meta.get("event") or {}
        explicit_severity = meta.get("severity") or explicit_event.get("severity")
        event_type_name = explicit_event.get("type") or behaviour.behaviour_type

        severity = EventService.determine_severity(
            behaviour_type=event_type_name,
            classification=behaviour.classification,
            explicit_severity=explicit_severity
        )

        reason_val = behaviour.reason or explicit_event.get("reason")
        if isinstance(reason_val, list):
            reason_str = " | ".join(reason_val)
        elif isinstance(reason_val, str):
            reason_str = reason_val
        else:
            reason_str = f"Behavior activity '{behaviour.behaviour_type}' event detected for Track {behaviour.track_id}"

        event = Event(
            video_id=behaviour.video_id,
            track_id=behaviour.track_id,
            behaviour_id=behaviour.id,
            event_type=event_type_name,
            severity=severity,
            start_time=behaviour.start_time,
            end_time=behaviour.end_time,
            confidence=behaviour.confidence,
            reason=reason_str,
            status="detected",
            metadata_json=meta
        )
        db.add(event)
        db.flush()

        # Automatically generate evidence items for this event
        position = db.query(TrackPosition).filter(
            TrackPosition.track_id == behaviour.track_id,
            TrackPosition.timestamp >= behaviour.start_time
        ).order_by(TrackPosition.timestamp.asc()).first()

        frame_num = position.frame_number if position else int(behaviour.start_time * 30.0)
        timestamp = position.timestamp if position else behaviour.start_time

        # 1. Bounding Box Evidence
        if position:
            bbox_evidence = Evidence(
                event_id=event.id,
                evidence_type="bounding_box",
                timestamp=timestamp,
                frame_number=frame_num,
                description=f"Bounding box location for Track #{behaviour.track_id} at timestamp {timestamp:.2f}s",
                metadata_json={
                    "bbox": [position.x, position.y, position.width, position.height],
                    "center": [position.center_x, position.center_y],
                    "confidence": position.confidence
                }
            )
            db.add(bbox_evidence)

        # 2. Trajectory Evidence
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

        # 3. Pose Keypoints Evidence (if keypoints exist in metadata)
        keypoints = meta.get("keypoints")
        if keypoints:
            keypoints_evidence = Evidence(
                event_id=event.id,
                evidence_type="frame",
                timestamp=timestamp,
                frame_number=frame_num,
                description=f"Biomechanical 17-keypoint skeleton pose data",
                metadata_json={"keypoints": keypoints}
            )
            db.add(keypoints_evidence)

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
