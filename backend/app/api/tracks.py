from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.track import TrackImportRequest, TrackResponse, TrackPositionResponse
from app.services.track_service import TrackService

router = APIRouter(prefix="/videos", tags=["Tracks (Member 1 Integration)"])

@router.post("/{video_id}/tracks/import", response_model=List[TrackResponse], status_code=status.HTTP_201_CREATED)
def import_tracks(video_id: int, import_data: TrackImportRequest, db: Session = Depends(get_db)):
    try:
        return TrackService.import_tracks(db, video_id, import_data)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to import tracks: {str(e)}")

@router.get("/{video_id}/tracks", response_model=List[TrackResponse])
def get_video_tracks(video_id: int, db: Session = Depends(get_db)):
    return TrackService.get_video_tracks(db, video_id)

@router.get("/{video_id}/tracks/{track_id}", response_model=TrackResponse)
def get_track(video_id: int, track_id: int, db: Session = Depends(get_db)):
    track = TrackService.get_track_by_video_and_track_id(db, video_id, track_id)
    if not track:
        raise HTTPException(status_code=404, detail=f"Track ID {track_id} for Video {video_id} not found.")
    return track

@router.get("/{video_id}/tracks/{track_id}/positions", response_model=List[TrackPositionResponse])
def get_track_positions(video_id: int, track_id: int, db: Session = Depends(get_db)):
    track = TrackService.get_track_by_video_and_track_id(db, video_id, track_id)
    if not track:
        raise HTTPException(status_code=404, detail=f"Track ID {track_id} for Video {video_id} not found.")
    return TrackService.get_track_positions(db, video_id, track_id)
