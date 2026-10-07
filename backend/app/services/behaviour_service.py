from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.video import Video
from app.models.track import Track
from app.models.behaviour import Behaviour
from app.schemas.behaviour import BehaviourImportRequest
from app.services.event_service import EventService
from app.core.logging import logger

class BehaviourService:
    @staticmethod
    def import_behaviours(db: Session, video_id: int, import_data: BehaviourImportRequest) -> List[Behaviour]:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video with ID {video_id} not found")

        imported_behaviours = []

        for item in import_data.behaviours:
            # Locate track for this video
            track = db.query(Track).filter(
                Track.video_id == video_id,
                Track.track_id == item.track_id
            ).first()

            if not track:
                # Create a placeholder track if Member 2 imports behaviour before Member 1 finishes
                track = Track(
                    video_id=video_id,
                    track_id=item.track_id,
                    object_type="person",
                    start_time=item.start_time,
                    end_time=item.end_time,
                    first_seen_frame=0,
                    last_seen_frame=0,
                    average_confidence=item.confidence or 1.0,
                    metadata_json={}
                )
                db.add(track)
                db.flush()

            # Check if behaviour already imported (deduplication check)
            existing = db.query(Behaviour).filter(
                Behaviour.video_id == video_id,
                Behaviour.track_id == track.id,
                Behaviour.behaviour_type == item.behaviour_type,
                Behaviour.start_time == item.start_time
            ).first()

            if not existing:
                behaviour = Behaviour(
                    video_id=video_id,
                    track_id=track.id,
                    behaviour_type=item.behaviour_type,
                    start_time=item.start_time,
                    end_time=item.end_time,
                    confidence=item.confidence or 1.0,
                    classification=item.classification or "normal",
                    reason=item.reason,
                    metadata_json=item.metadata or {}
                )
                db.add(behaviour)
                db.flush()
            else:
                behaviour = existing

            # Trigger event creation if abnormal
            if behaviour.classification.lower() == "abnormal":
                EventService.create_event_from_behaviour(db, behaviour)

            imported_behaviours.append(behaviour)

        db.commit()
        for b in imported_behaviours:
            db.refresh(b)

        logger.info(f"Imported {len(imported_behaviours)} behaviours for Video ID {video_id}")
        return imported_behaviours

    @staticmethod
    def get_behaviours_for_video(db: Session, video_id: int) -> List[Behaviour]:
        return db.query(Behaviour).filter(Behaviour.video_id == video_id).order_by(Behaviour.start_time.asc()).all()
