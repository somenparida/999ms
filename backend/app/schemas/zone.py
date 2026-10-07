from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field

class ZoneCreate(BaseModel):
    video_id: int
    name: str
    zone_type: Optional[str] = "restricted"
    coordinates: List[List[float]] = Field(..., description="List of [x, y] vertex coordinates")
    enabled: Optional[bool] = True
    metadata: Optional[Dict[str, Any]] = None

class ZoneResponse(BaseModel):
    id: int
    video_id: int
    name: str
    zone_type: str
    coordinates: List[List[float]]
    enabled: bool
    metadata: Optional[Dict[str, Any]] = Field(default=None, validation_alias="metadata_json", serialization_alias="metadata")

    model_config = ConfigDict(from_attributes=True)
