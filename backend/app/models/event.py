from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False, index=True)
    behaviour_id = Column(Integer, ForeignKey("behaviours.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    severity = Column(String, nullable=False, default="medium")  # low, medium, high, critical
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    reason = Column(String, nullable=True)
    status = Column(String, nullable=False, default="detected")  # detected, reviewed, confirmed, dismissed
    metadata_json = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    video = relationship("Video", back_populates="events")
    track = relationship("Track", back_populates="events")
    behaviour = relationship("Behaviour", back_populates="events")
    evidence_items = relationship("Evidence", back_populates="event", cascade="all, delete-orphan")
