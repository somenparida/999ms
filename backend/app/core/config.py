import os
from typing import List, Union
from pydantic import Field
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings  # type: ignore

class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous Vision & Behaviour Understanding Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./vision_behaviour.db"
    )

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./storage/videos")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./storage/processed")
    EVIDENCE_DIR: str = os.getenv("EVIDENCE_DIR", "./storage/evidence")
    EVENT_CLIPS_DIR: str = os.getenv("EVENT_CLIPS_DIR", "./storage/event_clips")

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    DEBUG: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
