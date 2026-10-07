from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.analysis import AnalysisJobResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/videos", tags=["Analysis Jobs"])

@router.post("/{video_id}/analyze", response_model=AnalysisJobResponse, status_code=status.HTTP_200_OK)
def start_analysis(video_id: int, db: Session = Depends(get_db)):
    try:
        return AnalysisService.start_analysis(db, video_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis job: {str(e)}")

@router.get("/{video_id}/analysis", response_model=AnalysisJobResponse)
def get_analysis_status(video_id: int, db: Session = Depends(get_db)):
    job = AnalysisService.get_analysis_status(db, video_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"No analysis job found for Video ID {video_id}.")
    return job

@router.post("/{video_id}/analysis/cancel", response_model=AnalysisJobResponse)
def cancel_analysis(video_id: int, db: Session = Depends(get_db)):
    job = AnalysisService.cancel_analysis(db, video_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"No active analysis job to cancel for Video ID {video_id}.")
    return job
