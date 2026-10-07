from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.evidence import EvidenceResponse
from app.services.evidence_service import EvidenceService

router = APIRouter(prefix="/evidence", tags=["Evidence"])

@router.get("/event/{event_id}", response_model=List[EvidenceResponse])
def get_evidence_by_event(event_id: int, db: Session = Depends(get_db)):
    return EvidenceService.get_evidence_for_event(db, event_id)
