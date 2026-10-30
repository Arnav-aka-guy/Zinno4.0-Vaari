"""Production mode refuses to start with unsafe settings (pilot item A1)."""

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.startup_checks import UnsafeConfigError, config_problems, enforce_startup_checks

STRONG = "a-strong-passcode-for-tests-2026"


@pytest.fixture
def prod(monkeypatch):
    monkeypatch.setenv("VAARI_ENV", "production")
    monkeypatch.setenv("VAARI_DEMO_PASSCODE", STRONG)
    monkeypatch.setenv("VAARI_READER", "mock")
    monkeypatch.setenv("VAARI_ALLOW_HOSTED_READER", "false")
    monkeypatch.delenv("VAARI_ALLOW_HOSTED_READER_IN_PRODUCTION", raising=False)
    return monkeypatch


def test_development_mode_accepts_default_passcode(monkeypatch):
    monkeypatch.setenv("VAARI_ENV", "development")
    monkeypatch.setenv("VAARI_DEMO_PASSCODE", "change-me")
    assert config_problems(settings) == []


def test_unknown_env_value_is_refused(monkeypatch):
    monkeypatch.setenv("VAARI_ENV", "staging")
    problems = config_problems(settings)
    assert len(problems) == 1 and "VAARI_ENV" in problems[0]


def test_production_with_safe_settings_has_no_problems(prod):
    assert config_problems(settings) == []


@pytest.mark.parametrize(
    "passcode, needle",
    [("", "empty"), ("   ", "empty"), ("change-me", "default"), ("short-pass-15ch", "15 characters")],
)
def test_production_refuses_weak_passcode(prod, passcode, needle):
    prod.setenv("VAARI_DEMO_PASSCODE", passcode)
    problems = config_problems(settings)
    assert any(needle in p for p in problems), problems


def test_production_accepts_passcode_of_exactly_16(prod):
    prod.setenv("VAARI_DEMO_PASSCODE", "x" * 16)
    assert config_problems(settings) == []


@pytest.mark.parametrize(
    "reader, allow", [("hosted", "false"), ("mock", "true"), ("hosted", "true")]
)
def test_production_refuses_hosted_reader_without_override(prod, reader, allow):
    prod.setenv("VAARI_READER", reader)
    prod.setenv("VAARI_ALLOW_HOSTED_READER", allow)
    problems = config_problems(settings)
    assert any("third party" in p for p in problems), problems


def test_production_hosted_reader_with_explicit_override(prod):
    prod.setenv("VAARI_READER", "hosted")
    prod.setenv("VAARI_ALLOW_HOSTED_READER", "true")
    prod.setenv("VAARI_ALLOW_HOSTED_READER_IN_PRODUCTION", "true")
    assert config_problems(settings) == []


def test_all_problems_listed_together(prod):
    prod.setenv("VAARI_DEMO_PASSCODE", "change-me")
    prod.setenv("VAARI_READER", "hosted")
    with pytest.raises(UnsafeConfigError) as exc:
        enforce_startup_checks(settings)
    assert len(exc.value.problems) == 2
    assert "refused to start" in str(exc.value)


def test_app_refuses_to_start_in_production_with_default_passcode(prod, temp_db):
    prod.setenv("VAARI_DEMO_PASSCODE", "change-me")
    with pytest.raises(UnsafeConfigError):
        with TestClient(app):
            pass


def test_app_starts_in_production_with_safe_settings(prod, temp_db):
    with TestClient(app) as c:
        assert c.get("/api/health").status_code == 200
