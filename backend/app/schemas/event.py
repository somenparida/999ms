from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field

class EventUpdateStatus(BaseModel):
    status: str = Field(..., description="detected, reviewed, confirmed, dismissed")
    notes: Optional[str] = None

class EventResponse(BaseModel):
    id: int
    video_id: int
    track_id: int
    behaviour_id: Optional[int] = None
    event_type: str
    severity: str  # low, medium, high, critical
    start_time: float
    end_time: float
    confidence: float
    reason: Optional[str] = None
    status: str  # detected, reviewed, confirmed, dismissed
    metadata: Optional[Dict[str, Any]] = Field(default=None, validation_alias="metadata_json", serialization_alias="metadata")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
