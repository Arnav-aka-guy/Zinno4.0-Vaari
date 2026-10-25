"""Authentication dependencies for Vaari."""

from fastapi import Header
from app.config import settings
from app.errors import VaariError


async def require_passcode(
    x_vaari_passcode: str | None = Header(None, alias="X-Vaari-Passcode"),
) -> str:
    if not x_vaari_passcode or x_vaari_passcode != settings.demo_passcode:
        raise VaariError(
            error_code="UNAUTHORIZED",
            message="Invalid or missing passcode.",
            http_status=401,
        )
    return x_vaari_passcode


async def require_machine_token(
    x_vaari_machine_token: str | None = Header(None, alias="X-Vaari-Machine-Token"),
) -> str:
    if not x_vaari_machine_token:
        raise VaariError(
            error_code="UNAUTHORIZED",
            message="Missing machine token.",
            http_status=401,
        )
    return x_vaari_machine_token


async def require_slot_auth(
    x_vaari_slot_token: str | None = Header(None, alias="X-Vaari-Slot-Token"),
    x_vaari_passcode: str | None = Header(None, alias="X-Vaari-Passcode"),
) -> str:
    """Slot auth: X-Vaari-Slot-Token or operator passcode. Detailed verification in step 06."""
    if x_vaari_passcode and x_vaari_passcode == settings.demo_passcode:
        return "operator"
    if x_vaari_slot_token:
        return x_vaari_slot_token
    raise VaariError(
        error_code="UNAUTHORIZED",
        message="Slot token or operator passcode required.",
        http_status=401,
    )
