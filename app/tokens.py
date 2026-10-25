"""Token and service-code generators for Vaari."""

import secrets


def new_token() -> str:
    """Generate a 128-bit URL-safe token (16 bytes)."""
    return secrets.token_urlsafe(16)


def new_service_code() -> str:
    """Generate a 4-digit numeric code as a string (e.g. '0482')."""
    return f"{secrets.randbelow(10000):04d}"
