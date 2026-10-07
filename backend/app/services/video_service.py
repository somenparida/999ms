import os
import shutil
import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.video import Video
from app.core.config import settings
from app.core.logging import logger

class VideoService:
    @staticmethod
    def get_all_videos(db: Session) -> List[Video]:
        return db.query(Video).order_by(Video.id.desc()).all()

    @staticmethod
    def get_video_by_id(db: Session, video_id: int) -> Optional[Video]:
        return db.query(Video).filter(Video.id == video_id).first()

    @staticmethod
    async def create_video(db: Session, file: UploadFile) -> Video:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)
        logger.info(f"Video uploaded: {file.filename} saved to {file_path} ({file_size} bytes)")

        # Create video DB record
        video = Video(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            duration=120.0,  # Default fallback duration
            fps=30.0,
            width=1920,
            height=1080,
            total_frames=3600,
            status="uploaded"
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        return video

    @staticmethod
    def delete_video(db: Session, video_id: int) -> bool:
        video = VideoService.get_video_by_id(db, video_id)
        if not video:
            return False
        
        # Delete file if exists
        if os.path.exists(video.file_path):
            try:
                os.remove(video.file_path)
            except Exception as e:
                logger.error(f"Failed to remove file {video.file_path}: {e}")

        db.delete(video)
        db.commit()
        logger.info(f"Video ID {video_id} deleted successfully.")
        return True
