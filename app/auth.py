"""Authentication dependencies for Vaari."""

from fastapi import Header
from app.config import settings
from app.errors import VaariError
from app.models import Slot


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


def verify_slot_auth(
    slot: Slot,
    x_vaari_slot_token: str | None = None,
    x_vaari_passcode: str | None = None,
) -> str:
    """Verify auth for a specific slot: passcode or matching slot token."""
    if x_vaari_passcode and x_vaari_passcode == settings.demo_passcode:
        return "operator"
    if x_vaari_slot_token is not None:
        if x_vaari_slot_token == slot.link_token:
            return "driver"
        raise VaariError(
            error_code="WRONG_SLOT",
            message="The link token does not belong to this slot.",
            http_status=403,
            details={"slot_id": slot.id},
        )
    raise VaariError(
        error_code="UNAUTHORIZED",
        message="Slot token or operator passcode required.",
        http_status=401,
    )
