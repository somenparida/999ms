from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field, AliasChoices

class TrackItemImport(BaseModel):
    track_id: int
    object_type: Optional[str] = Field(
        default="person", validation_alias=AliasChoices("object_type", "class_name")
    )
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    timestamp: float
    frame_number: Optional[int] = 0
    bbox: List[float] = Field(..., description="Bounding box [x, y, w, h] or [x1, y1, x2, y2]")
    center: Optional[List[float]] = None
    confidence: Optional[float] = Field(
        default=1.0, validation_alias=AliasChoices("confidence", "detection_confidence")
    )
    detection_confidence: Optional[float] = None
    velocity: Optional[float] = 0.0
    keypoints: Optional[List[List[float]]] = Field(
        default=None, description="17 COCO pose keypoints [[x, y, conf], ...]"
    )
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="ignore")

class TrackImportRequest(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    tracks: List[TrackItemImport]

    model_config = ConfigDict(extra="ignore")

class TrackPositionResponse(BaseModel):
    id: int
    track_id: int
    timestamp: float
    frame_number: int
    x: float
    y: float
    width: float
    height: float
    center_x: float
    center_y: float
    confidence: float
    velocity: Optional[float] = 0.0
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, validation_alias="metadata_json", serialization_alias="metadata"
    )

    model_config = ConfigDict(from_attributes=True)

class TrackResponse(BaseModel):
    id: int
    video_id: int
    track_id: int
    object_type: str
    start_time: float
    end_time: float
    first_seen_frame: int
    last_seen_frame: int
    average_confidence: float
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, validation_alias="metadata_json", serialization_alias="metadata"
    )
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
