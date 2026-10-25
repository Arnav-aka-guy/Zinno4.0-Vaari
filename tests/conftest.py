"""Pytest fixtures for Vaari tests."""

import os
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Ensure test passcode and settings
os.environ["VAARI_DEMO_PASSCODE"] = "test-passcode"
os.environ["VAARI_TZ"] = "Asia/Kolkata"

from app.main import app
from app.db import override_db, get_db, Base


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for test isolation."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tf:
        temp_path = tf.name

    db_url = f"sqlite:///{Path(temp_path).as_posix()}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    override_db(engine, SessionFactory)

    def _get_test_db():
        session = SessionFactory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _get_test_db

    yield SessionFactory

    app.dependency_overrides.pop(get_db, None)
    engine.dispose()
    try:
        Path(temp_path).unlink(missing_ok=True)
    except Exception:
        pass


@pytest.fixture
def client(temp_db):
    """TestClient configured with fresh temporary database."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    return {"X-Vaari-Passcode": "test-passcode"}
