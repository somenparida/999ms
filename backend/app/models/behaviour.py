from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Behaviour(Base):
    __tablename__ = "behaviours"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False, index=True)
    behaviour_type = Column(String, nullable=False, index=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    classification = Column(String, nullable=False, default="normal")  # normal, abnormal
    reason = Column(String, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    video = relationship("Video", back_populates="behaviours")
    track = relationship("Track", back_populates="behaviours")
    events = relationship("Event", back_populates="behaviour", cascade="all, delete-orphan")
