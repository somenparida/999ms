from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.zone import ZoneCreate, ZoneResponse
from app.services.zone_service import ZoneService

router = APIRouter(tags=["Zones"])

@router.post("/zones", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(zone_data: ZoneCreate, db: Session = Depends(get_db)):
    try:
        return ZoneService.create_zone(db, zone_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create zone: {str(e)}")

@router.get("/videos/{video_id}/zones", response_model=List[ZoneResponse])
def get_video_zones(video_id: int, db: Session = Depends(get_db)):
    return ZoneService.get_zones_for_video(db, video_id)
