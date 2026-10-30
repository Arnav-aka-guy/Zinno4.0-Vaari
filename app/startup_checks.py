"""Startup safety checks.

In production mode (VAARI_ENV=production) the app refuses to start when a
setting is unsafe. Every problem is listed in plain words so the person
deploying can fix them all in one go.
"""

from typing import Any

from app.config import VALID_ENVS

DEFAULT_PASSCODES = {"change-me", "changeme", "password", "vaari"}
MIN_PASSCODE_LEN = 16


class UnsafeConfigError(RuntimeError):
    """Raised at startup when production settings are unsafe."""

    def __init__(self, problems: list[str]):
        self.problems = problems
        lines = ["Vaari refused to start: unsafe settings for production mode."]
        lines += [f"  - {p}" for p in problems]
        super().__init__("\n".join(lines))


def _hosted_reader_requested(s: Any) -> bool:
    reader = str(getattr(s, "reader", "mock")).strip().lower()
    return bool(getattr(s, "allow_hosted_reader", False)) or reader not in ("mock", "")


def config_problems(s: Any) -> list[str]:
    """Return a list of problems with the settings. Empty means safe to start."""
    problems: list[str] = []
    env = str(getattr(s, "env", "development"))
    if env not in VALID_ENVS:
        problems.append(f"VAARI_ENV must be one of {', '.join(VALID_ENVS)} (got '{env}').")
        return problems
    if env != "production":
        return problems

    passcode = (getattr(s, "demo_passcode", "") or "").strip()
    if not passcode:
        problems.append("VAARI_DEMO_PASSCODE is empty.")
    elif passcode.lower() in DEFAULT_PASSCODES:
        problems.append("VAARI_DEMO_PASSCODE is still a default value.")
    elif len(passcode) < MIN_PASSCODE_LEN:
        problems.append(
            f"VAARI_DEMO_PASSCODE is {len(passcode)} characters; production needs at least {MIN_PASSCODE_LEN}."
        )

    if _hosted_reader_requested(s) and not getattr(s, "allow_hosted_reader_in_production", False):
        problems.append(
            "The hosted register reader is enabled (VAARI_READER or VAARI_ALLOW_HOSTED_READER). "
            "It sends register images to a third party and is for demonstration only. "
            "Turn it off, or set VAARI_ALLOW_HOSTED_READER_IN_PRODUCTION=true to override on purpose."
        )
    return problems


def enforce_startup_checks(s: Any) -> None:
    """Raise UnsafeConfigError if the settings are unsafe for the current mode."""
    problems = config_problems(s)
    if problems:
        raise UnsafeConfigError(problems)
