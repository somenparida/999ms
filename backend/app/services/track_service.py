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
            # Fallbacks for frame_number and confidence
            frame_num = item.frame_number if item.frame_number is not None and item.frame_number > 0 else int(item.timestamp * (video.fps or 30.0))
            conf = item.detection_confidence if item.detection_confidence is not None else (item.confidence or 1.0)

            # 1. Fetch or create Track parent object
            track = db.query(Track).filter(
                Track.video_id == video_id,
                Track.track_id == item.track_id
            ).first()

            # Parse bounding box: handles [x, y, w, h] or [x1, y1, x2, y2]
            bbox = item.bbox
            if len(bbox) >= 4:
                # Check if format is [x1, y1, x2, y2] where x2 > x and y2 > y
                if bbox[2] > bbox[0] and bbox[3] > bbox[1] and bbox[2] > 50 and bbox[3] > 50:
                    x, y = bbox[0], bbox[1]
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                else:
                    x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
            else:
                x, y, w, h = 0.0, 0.0, 100.0, 200.0

            center = item.center
            if center and len(center) >= 2:
                center_x, center_y = center[0], center[1]
            else:
                center_x, center_y = x + (w / 2.0), y + (h / 2.0)

            metadata_dict = item.metadata.copy() if item.metadata else {}
            if item.keypoints:
                metadata_dict["keypoints"] = item.keypoints

            if not track:
                track = Track(
                    video_id=video_id,
                    track_id=item.track_id,
                    object_type=item.object_type or "person",
                    start_time=item.timestamp,
                    end_time=item.timestamp,
                    first_seen_frame=frame_num,
                    last_seen_frame=frame_num,
                    average_confidence=conf,
                    metadata_json=metadata_dict
                )
                db.add(track)
                db.flush()
            else:
                # Update bounds
                if item.timestamp < track.start_time:
                    track.start_time = item.timestamp
                if item.timestamp > track.end_time:
                    track.end_time = item.timestamp
                if frame_num < track.first_seen_frame:
                    track.first_seen_frame = frame_num
                if frame_num > track.last_seen_frame:
                    track.last_seen_frame = frame_num
                if metadata_dict:
                    current_meta = track.metadata_json or {}
                    current_meta.update(metadata_dict)
                    track.metadata_json = current_meta

            # 2. Check position idempotency
            existing_pos = db.query(TrackPosition).filter(
                TrackPosition.track_id == track.id,
                TrackPosition.frame_number == frame_num
            ).first()

            if not existing_pos:
                pos = TrackPosition(
                    track_id=track.id,
                    timestamp=item.timestamp,
                    frame_number=frame_num,
                    x=float(x),
                    y=float(y),
                    width=float(w),
                    height=float(h),
                    center_x=float(center_x),
                    center_y=float(center_y),
                    confidence=float(conf),
                    velocity=float(item.velocity or 0.0),
                    metadata_json=metadata_dict
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
