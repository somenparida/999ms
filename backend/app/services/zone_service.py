from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.zone import Zone
from app.schemas.zone import ZoneCreate
from app.core.logging import logger

class ZoneService:
    @staticmethod
    def create_zone(db: Session, zone_data: ZoneCreate) -> Zone:
        zone = Zone(
            video_id=zone_data.video_id,
            name=zone_data.name,
            zone_type=zone_data.zone_type or "restricted",
            coordinates=zone_data.coordinates,
            enabled=zone_data.enabled if zone_data.enabled is not None else True,
            metadata_json=zone_data.metadata or {}
        )
        db.add(zone)
        db.commit()
        db.refresh(zone)
        logger.info(f"Created Zone '{zone.name}' (ID {zone.id}) for Video ID {zone.video_id}")
        return zone

    @staticmethod
    def get_zones_for_video(db: Session, video_id: int) -> List[Zone]:
        return db.query(Zone).filter(Zone.video_id == video_id).all()
