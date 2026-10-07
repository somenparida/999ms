from typing import List, Optional, Union
from sqlalchemy.orm import Session
from app.models.video import Video
from app.models.track import Track
from app.models.track_position import TrackPosition
from app.models.behaviour import Behaviour
from app.schemas.behaviour import BehaviourImportRequest, BehaviourItemImport
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
            activity_name = item.behaviour_type
            start_t = item.start_time
            end_t = item.end_time if item.end_time is not None else (start_t + (item.duration or 0.0))

            # Resolve classification & status
            raw_cls = (item.classification or "normal").lower()
            if raw_cls in ["abnormal", "potentially_unusual"]:
                classification = "abnormal"
            elif raw_cls == "unknown":
                classification = "unknown"
            else:
                classification = "normal"

            # Format reason
            reason_val = item.reason
            if isinstance(reason_val, list):
                reason_val = " | ".join(reason_val)

            # Build metadata dict for extra Member 2 fields
            meta_dict = item.metadata.copy() if item.metadata else {}
            if item.previous_activity:
                meta_dict["previous_activity"] = item.previous_activity
            if item.duration is not None:
                meta_dict["duration"] = item.duration
            if item.transition:
                meta_dict["transition"] = item.transition
            if item.event:
                meta_dict["event"] = item.event
            if item.severity:
                meta_dict["severity"] = item.severity
            if item.keypoints:
                meta_dict["keypoints"] = item.keypoints
            if item.bbox:
                meta_dict["bbox"] = item.bbox

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
                    start_time=start_t,
                    end_time=end_t,
                    first_seen_frame=item.frame_number or int(start_t * 30.0),
                    last_seen_frame=item.frame_number or int(end_t * 30.0),
                    average_confidence=item.confidence or 1.0,
                    metadata_json={}
                )
                db.add(track)
                db.flush()
            else:
                # Update track bounds
                if start_t < track.start_time:
                    track.start_time = start_t
                if end_t > track.end_time:
                    track.end_time = end_t
                if item.frame_number:
                    if item.frame_number < track.first_seen_frame:
                        track.first_seen_frame = item.frame_number
                    if item.frame_number > track.last_seen_frame:
                        track.last_seen_frame = item.frame_number

            # If bbox is present in item (from Member 2 JSON file), save TrackPosition if not existing
            if item.bbox and len(item.bbox) == 4:
                b = item.bbox
                if b[2] > b[0] and b[3] > b[1]:
                    x, y, w, h = b[0], b[1], b[2] - b[0], b[3] - b[1]
                else:
                    x, y, w, h = b[0], b[1], b[2], b[3]
                frame_num = item.frame_number if item.frame_number is not None else int(start_t * 30.0)

                existing_pos = db.query(TrackPosition).filter(
                    TrackPosition.track_id == track.id,
                    TrackPosition.frame_number == frame_num
                ).first()

                if not existing_pos:
                    tp = TrackPosition(
                        track_id=track.id,
                        frame_number=frame_num,
                        timestamp=start_t,
                        x=x,
                        y=y,
                        width=w,
                        height=h,
                        center_x=x + w / 2.0,
                        center_y=y + h / 2.0,
                        confidence=item.confidence or 1.0,
                        metadata_json={"keypoints": item.keypoints} if item.keypoints else {}
                    )
                    db.add(tp)
                    db.flush()

            # Check if behaviour already imported (deduplication check)
            existing = db.query(Behaviour).filter(
                Behaviour.video_id == video_id,
                Behaviour.track_id == track.id,
                Behaviour.behaviour_type == activity_name,
                Behaviour.start_time == start_t
            ).first()

            if not existing:
                behaviour = Behaviour(
                    video_id=video_id,
                    track_id=track.id,
                    behaviour_type=activity_name,
                    start_time=start_t,
                    end_time=end_t,
                    confidence=item.confidence or 1.0,
                    classification=classification,
                    reason=reason_val,
                    metadata_json=meta_dict
                )
                db.add(behaviour)
                db.flush()
            else:
                behaviour = existing
                if meta_dict:
                    curr_meta = behaviour.metadata_json or {}
                    curr_meta.update(meta_dict)
                    behaviour.metadata_json = curr_meta

            # Trigger event creation if:
            # 1. Classification is abnormal/potentially unusual
            # 2. Item contains an explicit event payload (e.g. ACTIVITY_CHANGE, FALL_DETECTED)
            # 3. Item severity is explicit and non-NONE
            has_explicit_event = bool(item.event and isinstance(item.event, dict) and item.event.get("type"))
            has_non_none_severity = bool(item.severity and str(item.severity).upper() not in ["NONE", "NORMAL", ""])

            if classification == "abnormal" or has_explicit_event or has_non_none_severity:
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
