"""Schema set-up. Creates any missing tables (replaced by Alembic in pilot item B6)."""

from app.db import Base, get_engine
import app.models  # noqa: F401  (register every table)


def ensure_schema() -> None:
    Base.metadata.create_all(bind=get_engine())
