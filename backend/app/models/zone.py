from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    zone_type = Column(String, nullable=False, default="restricted")  # restricted, monitored
    coordinates = Column(JSON, nullable=False)  # List of points e.g. [[x1, y1], [x2, y2], ...]
    enabled = Column(Boolean, nullable=False, default=True)
    metadata_json = Column("metadata", JSON, nullable=True, default=dict)

    video = relationship("Video", back_populates="zones")
