from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field

class BehaviourItemImport(BaseModel):
    track_id: int
    behaviour_type: str
    start_time: float
    end_time: float
    confidence: Optional[float] = 1.0
    classification: Optional[str] = "normal"  # normal, abnormal
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BehaviourImportRequest(BaseModel):
    behaviours: List[BehaviourItemImport]

class BehaviourResponse(BaseModel):
    id: int
    video_id: int
    track_id: int
    behaviour_type: str
    start_time: float
    end_time: float
    confidence: float
    classification: str
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None, validation_alias="metadata_json", serialization_alias="metadata")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
