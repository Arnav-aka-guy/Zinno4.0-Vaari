"""Evidence integrity and anomaly checks."""

from sqlalchemy.orm import Session
from app.models import Slot


def run_checks(session: Session, slot: Slot) -> list[str]:
    """Check evidence for flags. Phase 1 returns [] and leaves every position as not_checked.

    Phase 3 implements:
    - position_mismatch
    - too_fast
    - exact_duplicate_photo
    - code_missing
    - code_wrong
    """
    return []
