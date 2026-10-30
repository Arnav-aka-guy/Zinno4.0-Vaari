"""Configuration and environment variables for Vaari."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
ROOT_DIR = Path(__file__).parent.parent.resolve()
load_dotenv(ROOT_DIR / ".env")


VALID_ENVS = ("development", "production")


class Settings:
    @property
    def env(self) -> str:
        """VAARI_ENV: 'development' (default) or 'production'."""
        return os.environ.get("VAARI_ENV", "development").strip().lower() or "development"

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def allow_hosted_reader_in_production(self) -> bool:
        """Explicit override needed before the hosted reader may run in production."""
        return os.environ.get("VAARI_ALLOW_HOSTED_READER_IN_PRODUCTION", "false").strip().lower() in (
            "true",
            "1",
        )

    @property
    def secret_key(self) -> str:
        """VAARI_SECRET_KEY signs login sessions. Required in production."""
        return os.environ.get("VAARI_SECRET_KEY", "").strip()

    @property
    def session_hours(self) -> float:
        return float(os.environ.get("VAARI_SESSION_HOURS", "12"))

    @property
    def auth_mode(self) -> str:
        """'passcode' in development (shared passcode and accounts both work), 'accounts' in production."""
        return "accounts" if self.is_production else "passcode"

    @property
    def demo_passcode(self) -> str:
        return os.environ.get("VAARI_DEMO_PASSCODE", "change-me")

    @property
    def db_path(self) -> str:
        return os.environ.get("VAARI_DB_PATH", "data/vaari.sqlite")

    @property
    def data_dir(self) -> str:
        return os.environ.get("VAARI_DATA_DIR", "data")

    @property
    def tz(self) -> str:
        return os.environ.get("VAARI_TZ", "Asia/Kolkata")

    @property
    def today(self) -> str | None:
        val = os.environ.get("VAARI_TODAY", "").strip()
        return val if val else None

    @property
    def window_days(self) -> int:
        return int(os.environ.get("VAARI_WINDOW_DAYS", "20"))

    @property
    def max_radius_km(self) -> float:
        return float(os.environ.get("VAARI_MAX_RADIUS_KM", "25"))

    @property
    def road_factor(self) -> float:
        return float(os.environ.get("VAARI_ROAD_FACTOR", "1.3"))

    @property
    def max_photo_mb(self) -> float:
        return float(os.environ.get("VAARI_MAX_PHOTO_MB", "8"))

    @property
    def too_fast_min_per_acre(self) -> int:
        return int(os.environ.get("VAARI_TOO_FAST_MIN_PER_ACRE", "25"))

    @property
    def seed_phones(self) -> list[str]:
        raw = os.environ.get("VAARI_SEED_PHONES", "").strip()
        if not raw:
            return []
        return [p.strip() for p in raw.split(",") if p.strip()]

    @property
    def demo_plot_lat(self) -> float:
        return float(os.environ.get("VAARI_DEMO_PLOT_LAT", str(self.centre_lat)))

    @property
    def demo_plot_lon(self) -> float:
        return float(os.environ.get("VAARI_DEMO_PLOT_LON", str(self.centre_lon)))

    @property
    def centre_lat(self) -> float:
        return float(os.environ.get("VAARI_CENTRE_LAT", "30.7333"))

    @property
    def centre_lon(self) -> float:
        return float(os.environ.get("VAARI_CENTRE_LON", "76.7794"))

    @property
    def centre_name(self) -> str:
        return os.environ.get("VAARI_CENTRE_NAME", "Kisan Seva Kendra Nabha")

    @property
    def centre_phone(self) -> str:
        return os.environ.get("VAARI_CENTRE_PHONE", "9876543210")

    @property
    def public_base_url(self) -> str:
        return os.environ.get("VAARI_PUBLIC_BASE_URL", "").rstrip("/")

    @property
    def reader(self) -> str:
        return os.environ.get("VAARI_READER", "mock")

    @property
    def allow_hosted_reader(self) -> bool:
        return os.environ.get("VAARI_ALLOW_HOSTED_READER", "false").lower() in ("true", "1")

    @property
    def vision_provider(self) -> str:
        return os.environ.get("VAARI_VISION_PROVIDER", "gemini")

    @property
    def vision_model(self) -> str:
        return os.environ.get("VAARI_VISION_MODEL", "")

    @property
    def reader_timeout_s(self) -> int:
        return int(os.environ.get("VAARI_READER_TIMEOUT_S", "20"))


settings = Settings()
