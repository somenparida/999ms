from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    duration = Column(Float, nullable=True, default=0.0)
    fps = Column(Float, nullable=True, default=0.0)
    width = Column(Integer, nullable=True, default=0)
    height = Column(Integer, nullable=True, default=0)
    total_frames = Column(Integer, nullable=True, default=0)
    status = Column(String, nullable=False, default="uploaded")  # uploaded, queued, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tracks = relationship("Track", back_populates="video", cascade="all, delete-orphan")
    behaviours = relationship("Behaviour", back_populates="video", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="video", cascade="all, delete-orphan")
    analysis_jobs = relationship("AnalysisJob", back_populates="video", cascade="all, delete-orphan")
    zones = relationship("Zone", back_populates="video", cascade="all, delete-orphan")
