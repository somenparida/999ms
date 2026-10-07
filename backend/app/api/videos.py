from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.video import VideoResponse
from app.schemas.timeline import TimelineItemResponse
from app.schemas.summary import VideoSummaryResponse
from app.services.video_service import VideoService
from app.services.summary_service import SummaryService

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.post("/upload", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing in uploaded file.")
    try:
        return await VideoService.create_video(db, file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload video: {str(e)}")

@router.get("", response_model=List[VideoResponse])
def list_videos(db: Session = Depends(get_db)):
    return VideoService.get_all_videos(db)

@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = VideoService.get_video_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found.")
    return video

@router.delete("/{video_id}", status_code=status.HTTP_200_OK)
def delete_video(video_id: int, db: Session = Depends(get_db)):
    success = VideoService.delete_video(db, video_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found.")
    return {"message": f"Video {video_id} deleted successfully."}

@router.get("/{video_id}/timeline", response_model=List[TimelineItemResponse])
def get_video_timeline(video_id: int, db: Session = Depends(get_db)):
    video = VideoService.get_video_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found.")
    return SummaryService.get_timeline(db, video_id)

@router.get("/{video_id}/summary", response_model=VideoSummaryResponse)
def get_video_summary(video_id: int, db: Session = Depends(get_db)):
    video = VideoService.get_video_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found.")
    return SummaryService.get_summary(db, video_id)
