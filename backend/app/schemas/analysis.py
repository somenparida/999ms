from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field

class AnalysisJobResponse(BaseModel):
    id: int
    video_id: int
    status: str
    progress: float
    current_stage: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None, validation_alias="metadata_json", serialization_alias="metadata")

    model_config = ConfigDict(from_attributes=True)
