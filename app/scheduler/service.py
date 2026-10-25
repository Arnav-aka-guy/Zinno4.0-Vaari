"""Scheduler service layer: orchestrates DB load, pure plan(), and DB persistence."""

from sqlalchemy.orm import Session


def run_for_centre(session: Session, centre_id: int) -> dict[str, int]:
    """Stub for phase 1 step 03; step 05 implements the full scheduler."""
    return {
        "total": 0,
        "needs_info": 0,
        "open": 0,
        "scheduled": 0,
        "done": 0,
        "will_miss": 0,
        "cancelled": 0,
        "ran_in_ms": 0,
    }
