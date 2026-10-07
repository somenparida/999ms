from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.analysis_job import AnalysisJob
from app.models.video import Video
from app.core.logging import logger

class AnalysisService:
    @staticmethod
    def start_analysis(db: Session, video_id: int) -> AnalysisJob:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video with ID {video_id} not found")

        # Check existing running job
        job = db.query(AnalysisJob).filter(
            AnalysisJob.video_id == video_id,
            AnalysisJob.status.in_(["queued", "processing"])
        ).first()

        if job:
            return job

        job = AnalysisJob(
            video_id=video_id,
            status="processing",
            progress=10.0,
            current_stage="video_processing",
            started_at=datetime.utcnow(),
            metadata_json={}
        )
        video.status = "processing"
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info(f"Analysis job ID {job.id} started for Video ID {video_id}")
        return job

    @staticmethod
    def get_analysis_status(db: Session, video_id: int) -> Optional[AnalysisJob]:
        return db.query(AnalysisJob).filter(AnalysisJob.video_id == video_id).order_by(AnalysisJob.started_at.desc()).first()

    @staticmethod
    def update_job_progress(db: Session, job_id: int, stage: str, progress: float, status: str = "processing", error: str = None) -> AnalysisJob:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            return None

        job.current_stage = stage
        job.progress = progress
        job.status = status
        if error:
            job.error_message = error
        if status in ["completed", "failed", "cancelled"]:
            job.completed_at = datetime.utcnow()
            if job.video:
                job.video.status = status

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def cancel_analysis(db: Session, video_id: int) -> Optional[AnalysisJob]:
        job = db.query(AnalysisJob).filter(
            AnalysisJob.video_id == video_id,
            AnalysisJob.status.in_(["queued", "processing"])
        ).first()

        if not job:
            return None

        job.status = "cancelled"
        job.completed_at = datetime.utcnow()
        if job.video:
            job.video.status = "uploaded"
        db.commit()
        db.refresh(job)
        logger.info(f"Cancelled Analysis Job ID {job.id} for Video ID {video_id}")
        return job
