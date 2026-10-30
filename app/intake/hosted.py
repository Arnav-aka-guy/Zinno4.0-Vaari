"""HostedVisionReader implementing RegisterReader (Step 03).

PRIVACY GATE: Refuses to run unless VAARI_ALLOW_HOSTED_READER is "true".
No real register page may ever be sent to a hosted model.
"""

import base64
from datetime import date
import json
import os
import re
import time
from typing import Any, Callable
import httpx

from app.intake.prompt import (
    PROMPT_VERSION,
    REGISTER_EXTRACTION_PROMPT,
    RETRY_JSON_MESSAGE,
)
from app.intake.reader import ReaderUnavailable, RegisterDraft, RowDraft
from app.intake.validate import FAILING_CONFIDENCE_CAP, validate_row


def _parse_and_check_schema(raw_text: str) -> list[dict[str, Any]]:
    """Parse JSON string and verify it contains a valid 'rows' list of dicts."""
    if not raw_text or not isinstance(raw_text, str):
        raise ValueError("Empty response from vision model.")
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


def _get_today() -> date:
    try:
        from app import clock
        return clock.today()
    except Exception:
        return date(2026, 10, 25)


class HostedVisionReader:
    """Vision model reader supporting Gemini and Anthropic behind VAARI_ALLOW_HOSTED_READER."""

    def __init__(
        self,
        settings: Any = None,
        client_callable: Callable[[bytes, str, str, float], str] | None = None,
        today_override: date | None = None,
    ):
        if settings is None:
            from app.config import settings as app_settings
            settings = app_settings
        self.settings = settings
        self.client_callable = client_callable
        self.today_override = today_override

    def _check_privacy_gate(self) -> None:
        allow_attr = getattr(self.settings, "allow_hosted_reader", False)
        env_raw = os.environ.get("VAARI_ALLOW_HOSTED_READER", "").strip().lower()
        is_allowed = (allow_attr is True) or (env_raw == "true")
        if not is_allowed:
            raise ReaderUnavailable(
                "Hosted vision reader is disabled. Set VAARI_ALLOW_HOSTED_READER=true "
                "only when testing with synthetic register pages."
            )

    def read(self, image: bytes, media_type: str = "image/jpeg") -> RegisterDraft:
        self._check_privacy_gate()

        if not image or len(image) == 0:
            raise ReaderUnavailable("Uploaded register image is empty.")

        timeout_s = float(getattr(self.settings, "reader_timeout_s", 20))
        t0 = time.perf_counter()

        prompt = REGISTER_EXTRACTION_PROMPT
        raw_rows: list[dict[str, Any]] | None = None
        last_error: Exception | None = None

        # Try once, and if JSON fails to parse or breaks schema, retry ONCE with RETRY_JSON_MESSAGE
        for attempt in range(2):
            current_prompt = (
                prompt if attempt == 0 else f"{prompt}\n\n{RETRY_JSON_MESSAGE}"
            )
            try:
                if self.client_callable is not None:
                    raw_text = self.client_callable(image, media_type, current_prompt, timeout_s)
                else:
                    raw_text = self._invoke_provider(image, media_type, current_prompt, timeout_s)
            except ReaderUnavailable:
                raise
            except (TimeoutError, httpx.TimeoutException) as exc:
                raise ReaderUnavailable(f"Vision provider timed out after {timeout_s}s: {exc}") from exc
            except Exception as exc:
                raise ReaderUnavailable(f"Vision provider call failed: {exc}") from exc

            try:
                raw_rows = _parse_and_check_schema(raw_text)
                break
            except Exception as parse_exc:
                last_error = parse_exc

        if raw_rows is None:
            raise ReaderUnavailable(
                f"Vision model returned invalid JSON after retry: {last_error}"
            )

        val_today = self.today_override or _get_today()
        validated_rows: list[RowDraft] = []
        for idx, item in enumerate(raw_rows, start=1):
            row_no = int(item.get("row") or idx)
            raw_fields = dict(item.get("fields") or {})
            raw_conf = {
                k: float(v)
                for k, v in (item.get("confidence") or {}).items()
                if v is not None
            }
            clean_fields, issues = validate_row(raw_fields, val_today, confidence=raw_conf)
            for k in ("phone", "name", "village", "acres", "service_type", "harvest_date"):
                raw_conf.setdefault(
                    k, 0.85 if clean_fields.get(k) is not None else FAILING_CONFIDENCE_CAP
                )
            validated_rows.append(
                RowDraft(
                    row=row_no,
                    fields=clean_fields,
                    confidence=raw_conf,
                    issues=issues,
                )
            )

        latency_ms = max(1, int((time.perf_counter() - t0) * 1000))
        return RegisterDraft(
            rows=validated_rows,
            reader="hosted",
            prompt_version=PROMPT_VERSION,
            latency_ms=latency_ms,
        )

    def _invoke_provider(
        self,
        image: bytes,
        media_type: str,
        prompt: str,
        timeout_s: float,
    ) -> str:
        provider = getattr(self.settings, "vision_provider", "gemini").strip().lower()
        model = getattr(self.settings, "vision_model", "").strip()

        if provider == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()
            if not api_key:
                raise ReaderUnavailable("GEMINI_API_KEY is not set.")
            model_name = model or "gemini-3.5-flash-lite"
            if not model_name.startswith("gemini-") and not model_name.startswith("models/"):
                model_name = f"gemini-{model_name}"

            # Use google-genai SDK if installed, else direct REST via httpx
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(
                    api_key=api_key,
                    http_options=types.HttpOptions(timeout=int(timeout_s * 1000)),
                )
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Part.from_bytes(data=image, mime_type=media_type),
                        prompt,
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                    ),
                )
                return response.text or ""
            except ImportError:
                b64_img = base64.b64encode(image).decode("ascii")
                url = (
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{model_name}:generateContent?key={api_key}"
                )
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt},
                                {"inline_data": {"mime_type": media_type, "data": b64_img}},
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.1,
                        "responseMimeType": "application/json",
                    },
                }
                with httpx.Client(timeout=timeout_s) as http_client:
                    resp = http_client.post(url, json=payload)
                    if resp.status_code != 200:
                        raise ReaderUnavailable(f"Gemini HTTP {resp.status_code}: {resp.text[:200]}")
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]

        if provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
            if not api_key:
                raise ReaderUnavailable("ANTHROPIC_API_KEY is not set.")
            model_name = model or "claude-3-5-sonnet-latest"
            b64_img = base64.b64encode(image).decode("ascii")

            try:
                import anthropic

                client = anthropic.Anthropic(api_key=api_key, timeout=timeout_s)
                msg = client.messages.create(
                    model=model_name,
                    max_tokens=2048,
                    temperature=0.1,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": b64_img,
                                    },
                                },
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ],
                )
                return msg.content[0].text
            except ImportError:
                url = "https://api.anthropic.com/v1/messages"
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                }
                payload = {
                    "model": model_name,
                    "max_tokens": 2048,
                    "temperature": 0.1,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": b64_img,
                                    },
                                },
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ],
                }
                with httpx.Client(timeout=timeout_s) as http_client:
                    resp = http_client.post(url, headers=headers, json=payload)
                    if resp.status_code != 200:
                        raise ReaderUnavailable(
                            f"Anthropic HTTP {resp.status_code}: {resp.text[:200]}"
                        )
                    data = resp.json()
                    return data["content"][0]["text"]

        raise ReaderUnavailable(f"Unsupported vision provider: '{provider}'")
