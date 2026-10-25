"""Health check route."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app import clock
from app.config import settings
from app.db import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def get_health(session: Session = Depends(get_db)):
    db_status = "connected"
    try:
        session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return {
        "status": "ok",
        "database": db_status,
        "reader": "not_built",
        "satellite": "disabled",
        "messaging": "screen+wa_link",
        "today": clock.today().isoformat(),
        "demo_clock": bool(settings.today),
        "version": "0.1",
    }
