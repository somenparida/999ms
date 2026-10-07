from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class VideoBase(BaseModel):
    filename: str
    original_filename: str

class VideoCreate(VideoBase):
    file_path: str
    duration: Optional[float] = 0.0
    fps: Optional[float] = 0.0
    width: Optional[int] = 0
    height: Optional[int] = 0
    total_frames: Optional[int] = 0

class VideoResponse(VideoBase):
    id: int
    file_path: str
    duration: Optional[float] = 0.0
    fps: Optional[float] = 0.0
    width: Optional[int] = 0
    height: Optional[int] = 0
    total_frames: Optional[int] = 0
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
