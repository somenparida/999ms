from typing import Optional, Any, Dict
from pydantic import BaseModel

class TimelineItemResponse(BaseModel):
    timestamp: float
    track_id: int
    type: str
    classification: str  # normal, abnormal
    event_id: Optional[int] = None
    severity: Optional[str] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
