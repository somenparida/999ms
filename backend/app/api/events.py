from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.event import EventResponse, EventUpdateStatus
from app.schemas.evidence import EvidenceResponse
from app.services.event_service import EventService
from app.services.evidence_service import EvidenceService

router = APIRouter(tags=["Events & Evidence"])

@router.get("/videos/{video_id}/events", response_model=List[EventResponse])
def get_video_events(video_id: int, db: Session = Depends(get_db)):
    return EventService.get_events_for_video(db, video_id)

@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event ID {event_id} not found.")
    return event

@router.patch("/events/{event_id}", response_model=EventResponse)
def update_event_status(event_id: int, update_data: EventUpdateStatus, db: Session = Depends(get_db)):
    valid_statuses = ["detected", "reviewed", "confirmed", "dismissed"]
    if update_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status '{update_data.status}'. Must be one of {valid_statuses}")
    
    event = EventService.update_event_status(db, event_id, update_data.status)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event ID {event_id} not found.")
    return event

@router.get("/events/{event_id}/evidence", response_model=List[EvidenceResponse])
def get_event_evidence(event_id: int, db: Session = Depends(get_db)):
    event = EventService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event ID {event_id} not found.")
    return EvidenceService.get_evidence_for_event(db, event_id)
