import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import logger
from app.db.base import Base
from app.db.session import engine
import app.models  # Ensure models are loaded for table creation

from app.api.health import router as health_router
from app.api.videos import router as videos_router
from app.api.tracks import router as tracks_router
from app.api.behaviours import router as behaviours_router
from app.api.events import router as events_router
from app.api.evidence import router as evidence_router
from app.api.analysis import router as analysis_router
from app.api.zones import router as zones_router

def create_application() -> FastAPI:
    # Ensure storage directories exist
    for dir_path in [settings.UPLOAD_DIR, settings.OUTPUT_DIR, settings.EVIDENCE_DIR, settings.EVENT_CLIPS_DIR]:
        os.makedirs(dir_path, exist_ok=True)

    # Initialize DB tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        description="""
# HNX26PSI07 — Autonomous Vision & Behaviour Understanding Backend

Backend & Integration Layer (Member 3) connecting:
- Member 1: Object Detection & Tracking
- Member 2: Behaviour Analysis & Anomaly Detection
- Member 3: Backend, PostgreSQL, Integration Layer, Event Engine & Evidence
- Member 4: Frontend Dashboard & Interactive Visualization
"""
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check at root /health
    app.include_router(health_router)

    # Include API v1 routers
    app.include_router(videos_router, prefix=settings.API_V1_STR)
    app.include_router(tracks_router, prefix=settings.API_V1_STR)
    app.include_router(behaviours_router, prefix=settings.API_V1_STR)
    app.include_router(events_router, prefix=settings.API_V1_STR)
    app.include_router(evidence_router, prefix=settings.API_V1_STR)
    app.include_router(analysis_router, prefix=settings.API_V1_STR)
    app.include_router(zones_router, prefix=settings.API_V1_STR)

    # Mount static storage endpoint
    if os.path.exists("./storage"):
        app.mount("/storage", StaticFiles(directory="./storage"), name="storage")

    return app

app = create_application()
