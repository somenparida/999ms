from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String, nullable=False, default="queued")  # queued, processing, completed, failed, cancelled
    progress = Column(Float, nullable=False, default=0.0)
    current_stage = Column(String, nullable=False, default="queued")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True, default=dict)

    video = relationship("Video", back_populates="analysis_jobs")
