from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

    return {
        "status": "ok",
        "service": "Autonomous Vision & Behaviour Understanding Backend",
        "database": db_status
    }
