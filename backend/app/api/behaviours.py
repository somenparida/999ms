from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.behaviour import BehaviourImportRequest, BehaviourResponse
from app.services.behaviour_service import BehaviourService

router = APIRouter(prefix="/videos", tags=["Behaviours (Member 2 Integration)"])

@router.post("/{video_id}/behaviours/import", response_model=List[BehaviourResponse], status_code=status.HTTP_201_CREATED)
def import_behaviours(video_id: int, import_data: BehaviourImportRequest, db: Session = Depends(get_db)):
    try:
        return BehaviourService.import_behaviours(db, video_id, import_data)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to import behaviours: {str(e)}")

@router.get("/{video_id}/behaviours", response_model=List[BehaviourResponse])
def get_video_behaviours(video_id: int, db: Session = Depends(get_db)):
    return BehaviourService.get_behaviours_for_video(db, video_id)
