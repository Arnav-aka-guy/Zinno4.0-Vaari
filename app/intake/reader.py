"""RegisterReader interface, MockRegisterReader, and reader factory (Step 02)."""

from dataclasses import dataclass, field
from datetime import date
import json
from pathlib import Path
from typing import Any, Protocol
from app.intake.validate import FAILING_CONFIDENCE_CAP, validate_row


class ReaderUnavailable(Exception):
    """Raised when the register reader fails, times out, is disabled, or receives empty input."""


@dataclass
class RowDraft:
    row: int
    fields: dict[str, Any]
    confidence: dict[str, float] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)


@dataclass
class RegisterDraft:
    rows: list[RowDraft]
    reader: str
    prompt_version: str
    latency_ms: int


class RegisterReader(Protocol):
    def read(self, image: bytes, media_type: str = "image/jpeg") -> RegisterDraft:
        ...


FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "tests"
    / "fixtures"
    / "mock_register_draft.json"
)


def _current_today() -> date:
    """Read today via app.clock.today() if available, else fallback for standalone mode."""
    try:
        from app import clock
        return clock.today()
    except Exception:
        return date(2026, 10, 25)


class MockRegisterReader:
    """Deterministic mock reader returning the 6-row fixture from tests/fixtures/mock_register_draft.json."""

    def __init__(self, fixture_path: Path | None = None, today_override: date | None = None):
        self.fixture_path = fixture_path or FIXTURE_PATH
        self.today_override = today_override

    def read(self, image: bytes, media_type: str = "image/jpeg") -> RegisterDraft:
        if not image or len(image) == 0:
            raise ReaderUnavailable("Uploaded register image is empty.")

        if not self.fixture_path.exists():
            raise ReaderUnavailable(f"Mock fixture not found at {self.fixture_path}")

        raw_data = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        ref_today = self.today_override or _current_today()

        # If clock.today() in a test is more than 25 days away from the fixture's Oct 2026 dates,
        # anchor fixture validation to 2026-10-25 unless explicitly validating against ref_today.
        fixture_anchor = date(2026, 10, 25)
        val_today = ref_today if abs((ref_today - fixture_anchor).days) <= 25 else fixture_anchor

        rows: list[RowDraft] = []
        for item in raw_data.get("rows", []):
            row_no = int(item["row"])
            raw_fields = dict(item.get("fields") or {})
            conf: dict[str, float] = {
                k: float(v) for k, v in (item.get("confidence") or {}).items()
            }
            clean_fields, issues = validate_row(raw_fields, val_today, confidence=conf)

            # Ensure all core fields have a confidence entry
            for k in ("phone", "name", "village", "acres", "service_type", "harvest_date"):
                conf.setdefault(k, 0.9 if clean_fields.get(k) is not None else FAILING_CONFIDENCE_CAP)

            rows.append(
                RowDraft(
                    row=row_no,
                    fields=clean_fields,
                    confidence=conf,
                    issues=issues,
                )
            )

        return RegisterDraft(
            rows=rows,
            reader=raw_data.get("reader", "mock"),
            prompt_version=raw_data.get("prompt_version", "v1"),
            latency_ms=int(raw_data.get("latency_ms", 40)),
        )


def get_reader(settings: Any = None) -> RegisterReader:
    """Return the reader chosen by VAARI_READER ('mock' or 'hosted')."""
    if settings is None:
        from app.config import settings as app_settings
        settings = app_settings

    reader_choice = getattr(settings, "reader", "mock").strip().lower()
    if reader_choice == "mock":
        return MockRegisterReader()
    if reader_choice == "hosted":
        from app.intake.hosted import HostedVisionReader
        return HostedVisionReader(settings=settings)
    raise ReaderUnavailable(f"Unknown reader configured: '{reader_choice}'")
