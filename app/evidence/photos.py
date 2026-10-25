"""Photo upload processing, size limits, magic bytes and SHA-256 validation."""

import hashlib
from pathlib import Path
from fastapi import UploadFile
from app.config import settings
from app.errors import VaariError


async def process_photo(
    slot_id: int,
    kind: str,
    file: UploadFile | None,
) -> tuple[str | None, str | None, int | None]:
    """Validate photo size, magic bytes, compute SHA-256 and save to data/photos/.

    Returns (photo_path, photo_sha256, photo_bytes).
    """
    if file is None:
        return None, None, None

    max_bytes = int(settings.max_photo_mb * 1024 * 1024)
    # Read max_bytes + 1 to detect oversize without loading unbounded file
    raw = await file.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise VaariError(
            error_code="PAYLOAD_TOO_LARGE",
            message=f"Photo exceeds {settings.max_photo_mb} MB limit.",
            http_status=413,
            details={"max_mb": settings.max_photo_mb},
        )

    if len(raw) == 0:
        raise VaariError(
            error_code="VALIDATION_ERROR",
            message="Uploaded file is empty.",
            http_status=422,
            details={"field": "photo"},
        )

    # Magic bytes check
    ext = None
    if raw.startswith(b"\xff\xd8\xff"):
        ext = "jpg"
    elif raw.startswith(b"\x89PNG\r\n\x1a\n"):
        ext = "png"
    elif raw.startswith(b"RIFF") and len(raw) >= 12 and raw[8:12] == b"WEBP":
        ext = "webp"
    else:
        raise VaariError(
            error_code="VALIDATION_ERROR",
            message="Uploaded file is not a valid JPEG, PNG or WebP image.",
            http_status=422,
            details={"field": "photo"},
        )

    sha = hashlib.sha256(raw).hexdigest()
    filename = f"{slot_id}_{kind}_{sha[:12]}.{ext}"

    photo_dir = Path(settings.data_dir) / "photos"
    photo_dir.mkdir(parents=True, exist_ok=True)
    target_path = photo_dir / filename
    target_path.write_bytes(raw)

    return f"data/photos/{filename}", sha, len(raw)
