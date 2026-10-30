"""Turning a reader's JSON answer into a validated draft (shared by gemini_demo and custom).

Both remote readers must answer with the same JSON::

    {"rows": [{"row": 1, "fields": {...}, "confidence": {...}}]}

Every value is then checked by ``validate_row``; a cell that fails has its
confidence capped at 0.3, so the confirmation screen highlights it.
"""

import json
import re
from datetime import date
from typing import Any

from app.intake.reader import CORE_FIELDS, RegisterDraft, RowDraft
from app.intake.validate import FAILING_CONFIDENCE_CAP, validate_row


def parse_rows(raw_text: str) -> list[dict[str, Any]]:
    """Parse JSON text and check it has a 'rows' list of objects with 'fields'. Raises ValueError."""
    if not raw_text or not isinstance(raw_text, str):
        raise ValueError("Empty response from the reader.")
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    data = json.loads(cleaned)
    if not isinstance(data, dict) or "rows" not in data or not isinstance(data["rows"], list):
        raise ValueError("JSON does not match schema: missing 'rows' list.")

    rows = data["rows"]
    for item in rows:
        if not isinstance(item, dict) or "fields" not in item or not isinstance(item["fields"], dict):
            raise ValueError("Each row in 'rows' must be an object containing 'fields'.")
    return rows


def build_draft(
    raw_rows: list[dict[str, Any]],
    today: date,
    reader: str,
    prompt_version: str,
    latency_ms: int,
) -> RegisterDraft:
    rows: list[RowDraft] = []
    for idx, item in enumerate(raw_rows, start=1):
        row_no = int(item.get("row") or idx)
        raw_fields = dict(item.get("fields") or {})
        raw_conf = {
            k: float(v)
            for k, v in (item.get("confidence") or {}).items()
            if v is not None
        }
        clean_fields, issues = validate_row(raw_fields, today, confidence=raw_conf)
        for k in CORE_FIELDS:
            raw_conf.setdefault(k, 0.85 if clean_fields.get(k) is not None else FAILING_CONFIDENCE_CAP)
        rows.append(RowDraft(row=row_no, fields=clean_fields, confidence=raw_conf, issues=issues))
    return RegisterDraft(rows=rows, reader=reader, prompt_version=prompt_version, latency_ms=latency_ms)
