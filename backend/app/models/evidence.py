from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = Column(String, nullable=False)  # frame, image, video_clip, trajectory, bounding_box
    file_path = Column(String, nullable=True)
    timestamp = Column(Float, nullable=False)
    frame_number = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="evidence_items")
