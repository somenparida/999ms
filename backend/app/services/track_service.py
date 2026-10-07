from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.video import Video
from app.models.track import Track
from app.models.track_position import TrackPosition
from app.schemas.track import TrackImportRequest, TrackItemImport
from app.core.logging import logger

class TrackService:
    @staticmethod
    def import_tracks(db: Session, video_id: int, import_data: TrackImportRequest) -> List[Track]:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video with ID {video_id} not found")

        imported_tracks = {}

        for item in import_data.tracks:
            # 1. Fetch or create Track parent object
            track = db.query(Track).filter(
                Track.video_id == video_id,
                Track.track_id == item.track_id
            ).first()

            # Parse bounding box: bbox can be [x, y, w, h]
            bbox = item.bbox
            x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3] if len(bbox) >= 4 else (bbox[2] - bbox[0], bbox[3] - bbox[1])
            
            center = item.center
            if center and len(center) >= 2:
                center_x, center_y = center[0], center[1]
            else:
                center_x, center_y = x + (w / 2.0), y + (h / 2.0)

            if not track:
                track = Track(
                    video_id=video_id,
                    track_id=item.track_id,
                    object_type=item.object_type or "person",
                    start_time=item.timestamp,
                    end_time=item.timestamp,
                    first_seen_frame=item.frame_number,
                    last_seen_frame=item.frame_number,
                    average_confidence=item.confidence or 1.0,
                    metadata_json=item.metadata or {}
                )
                db.add(track)
                db.flush()
            else:
                # Update bounds
                if item.timestamp < track.start_time:
                    track.start_time = item.timestamp
                if item.timestamp > track.end_time:
                    track.end_time = item.timestamp
                if item.frame_number < track.first_seen_frame:
                    track.first_seen_frame = item.frame_number
                if item.frame_number > track.last_seen_frame:
                    track.last_seen_frame = item.frame_number

            # 2. Check position idempotency
            existing_pos = db.query(TrackPosition).filter(
                TrackPosition.track_id == track.id,
                TrackPosition.frame_number == item.frame_number
            ).first()

            if not existing_pos:
                pos = TrackPosition(
                    track_id=track.id,
                    timestamp=item.timestamp,
                    frame_number=item.frame_number,
                    x=float(x),
                    y=float(y),
                    width=float(w),
                    height=float(h),
                    center_x=float(center_x),
                    center_y=float(center_y),
                    confidence=float(item.confidence or 1.0),
                    velocity=float(item.velocity or 0.0),
                    metadata_json=item.metadata or {}
                )
                db.add(pos)

            imported_tracks[track.track_id] = track

        db.commit()
        for t in imported_tracks.values():
            db.refresh(t)
        
        logger.info(f"Imported {len(import_data.tracks)} track positions for Video ID {video_id}")
        return list(imported_tracks.values())

    @staticmethod
    def get_video_tracks(db: Session, video_id: int) -> List[Track]:
        return db.query(Track).filter(Track.video_id == video_id).order_by(Track.track_id.asc()).all()

    @staticmethod
    def get_track_by_video_and_track_id(db: Session, video_id: int, track_id: int) -> Optional[Track]:
        return db.query(Track).filter(Track.video_id == video_id, Track.track_id == track_id).first()

    @staticmethod
    def get_track_positions(db: Session, video_id: int, track_id: int) -> List[TrackPosition]:
        track = TrackService.get_track_by_video_and_track_id(db, video_id, track_id)
        if not track:
            return []
        return db.query(TrackPosition).filter(TrackPosition.track_id == track.id).order_by(TrackPosition.frame_number.asc()).all()
