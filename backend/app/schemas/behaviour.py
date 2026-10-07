from datetime import datetime
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, model_validator

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
    keypoints: Optional[List[Any]] = None
    bbox: Optional[List[float]] = None
    frame_number: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    @model_validator(mode='before')
    @classmethod
    def preprocess_item(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Member 2 wraps behaviour in a nested "behavior" dict inside a track frame object
            if "behavior" in data and isinstance(data["behavior"], dict):
                beh = data["behavior"].copy()
                # Copy outer track fields if missing in inner behavior
                if "track_id" not in beh and "track_id" in data:
                    beh["track_id"] = data["track_id"]
                if "timestamp" not in beh and "timestamp" in data:
                    beh["timestamp"] = data["timestamp"]
                if "bbox" in data and "bbox" not in beh:
                    beh["bbox"] = data["bbox"]
                if "keypoints" in data and "keypoints" not in beh:
                    beh["keypoints"] = data["keypoints"]
                if "frame_number" in data and "frame_number" not in beh:
                    beh["frame_number"] = data["frame_number"]
                return beh
        return data

class BehaviourImportRequest(BaseModel):
    behaviours: List[BehaviourItemImport]

    @model_validator(mode='before')
    @classmethod
    def preprocess_request(cls, data: Any) -> Any:
        if isinstance(data, list):
            return {"behaviours": data}
        elif isinstance(data, dict):
            if "behaviours" in data:
                return data
            elif "tracks" in data and isinstance(data["tracks"], list):
                return {"behaviours": data["tracks"]}
        return data

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
