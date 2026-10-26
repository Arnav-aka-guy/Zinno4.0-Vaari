"""Pure evidence anomaly rule functions (Step 04: E1 to E8).

Evidence is a plausibility signal, not proof. Flags ask a person to look;
they never block a job and never penalise anyone.
"""

from collections.abc import Iterable
from datetime import datetime


def too_fast(
    started_at: datetime | None,
    done_at: datetime | None,
    acres: float,
    min_per_acre: float = 25.0,
) -> bool:
    """Return True if the job completed faster than min_per_acre minutes per acre (E5)."""
    if started_at is None or done_at is None or acres <= 0:
        return False
    elapsed_minutes = (done_at - started_at).total_seconds() / 60.0
    return elapsed_minutes < (float(acres) * float(min_per_acre))


def duplicate_photo(sha256: str | None, other_hashes: Iterable[str | None]) -> bool:
    """Return True if sha256 exactly matches any hash in other_hashes (E6, E7)."""
    if not sha256:
        return False
    return any(h == sha256 for h in other_hashes if h)


def code_flags(
    expected_code: str | None,
    entered_code: str | None,
) -> tuple[list[str], bool]:
    """Check the farmer's 4-digit service code (E8).

    Returns (flags, farmer_confirmed):
    - missing entered_code -> (["code_missing"], False)
    - wrong entered_code   -> (["code_wrong"], False)
    - matching code        -> ([], True)
    """
    if entered_code is None or str(entered_code).strip() == "":
        return ["code_missing"], False
    if expected_code is not None and str(entered_code).strip() == str(expected_code).strip():
        return [], True
    return ["code_wrong"], False


def flags_for_position(position_state: str, plausible: bool | None) -> list[str]:
    """Return ['position_mismatch'] when position was checked and is not plausible."""
    if position_state in ("plausible", "mismatch") and plausible is False:
        return ["position_mismatch"]
    return []
