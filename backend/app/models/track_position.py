from sqlalchemy import Column, Integer, Float, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class TrackPosition(Base):
    __tablename__ = "track_positions"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(Float, nullable=False)
    frame_number = Column(Integer, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    center_x = Column(Float, nullable=False)
    center_y = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    velocity = Column(Float, nullable=True, default=0.0)
    metadata_json = Column("metadata", JSON, nullable=True, default=dict)

    __table_args__ = (
        UniqueConstraint("track_id", "frame_number", name="uq_track_frame"),
    )

    track = relationship("Track", back_populates="positions")
