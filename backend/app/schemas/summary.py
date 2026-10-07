from pydantic import BaseModel

class VideoSummaryResponse(BaseModel):
    people_detected: int
    unique_tracks: int
    normal_events: int
    abnormal_events: int
    high_risk_events: int
    average_confidence: float
    duration: float
