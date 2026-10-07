from typing import List
from sqlalchemy.orm import Session
from app.models.evidence import Evidence
from app.models.event import Event
from app.core.logging import logger

class EvidenceService:
    @staticmethod
    def get_evidence_for_event(db: Session, event_id: int) -> List[Evidence]:
        return db.query(Evidence).filter(Evidence.event_id == event_id).order_by(Evidence.id.asc()).all()

    @staticmethod
    def add_evidence(db: Session, event_id: int, evidence_type: str, file_path: str, timestamp: float, frame_number: int, description: str, metadata: dict) -> Evidence:
        evidence = Evidence(
            event_id=event_id,
            evidence_type=evidence_type,
            file_path=file_path,
            timestamp=timestamp,
            frame_number=frame_number,
            description=description,
            metadata_json=metadata or {}
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        logger.info(f"Added Evidence ID {evidence.id} ({evidence_type}) to Event ID {event_id}")
        return evidence
