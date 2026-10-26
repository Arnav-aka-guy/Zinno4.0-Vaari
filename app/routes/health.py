"""Health check route."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app import clock
from app.config import settings
from app.db import get_db
from app.routes.intake import get_reader_status_for_health

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
        "reader": get_reader_status_for_health(),
        "satellite": "disabled",
        "messaging": "screen+wa_link",
        "today": clock.today().isoformat(),
        "demo_clock": bool(settings.today),
        "version": "0.1",
    }
