from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    track_id = Column(Integer, nullable=False, index=True)
    object_type = Column(String, nullable=False, default="person")
    start_time = Column(Float, nullable=False, default=0.0)
    end_time = Column(Float, nullable=False, default=0.0)
    first_seen_frame = Column(Integer, nullable=False, default=0)
    last_seen_frame = Column(Integer, nullable=False, default=0)
    average_confidence = Column(Float, nullable=False, default=1.0)
    metadata_json = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("video_id", "track_id", name="uq_video_track"),
    )

    video = relationship("Video", back_populates="tracks")
    positions = relationship("TrackPosition", back_populates="track", cascade="all, delete-orphan")
    behaviours = relationship("Behaviour", back_populates="track", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="track", cascade="all, delete-orphan")
