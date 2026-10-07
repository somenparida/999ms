from datetime import datetime
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, ConfigDict, Field, AliasChoices

class BehaviourItemImport(BaseModel):
    track_id: int
    behaviour_type: str = Field(..., validation_alias=AliasChoices("behaviour_type", "activity"))
    start_time: float = Field(..., validation_alias=AliasChoices("start_time", "timestamp"))
    end_time: Optional[float] = None
    confidence: Optional[float] = 1.0
    classification: str = Field(default="normal", validation_alias=AliasChoices("classification", "status"))
    severity: Optional[str] = None
    reason: Optional[Union[str, List[str]]] = None
    previous_activity: Optional[str] = None
    duration: Optional[float] = 0.0
    transition: Optional[Dict[str, Any]] = None
    event: Optional[Dict[str, Any]] = None
    keypoints: Optional[List[List[float]]] = None
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
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, validation_alias="metadata_json", serialization_alias="metadata"
    )
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
