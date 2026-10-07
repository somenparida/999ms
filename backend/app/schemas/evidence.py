from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field

class EvidenceResponse(BaseModel):
    id: int
    event_id: int
    evidence_type: str  # frame, image, video_clip, trajectory, bounding_box
    file_path: Optional[str] = None
    timestamp: float
    frame_number: int
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None, validation_alias="metadata_json", serialization_alias="metadata")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
