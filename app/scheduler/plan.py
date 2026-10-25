"""Pure core scheduling algorithm for Vaari (Contract Section 8).

Pure function: no database, no clock, no network, no randomness.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any


@dataclass(frozen=True)
class RequestIn:
    id: int
    created_at: datetime
    service_type: str
    acres_x100: int
    harvest_date: date | None
    deadline_date: date | None
    lat: float | None = None
    lon: float | None = None


@dataclass(frozen=True)
class MachineIn:
    id: int
    service_types: tuple[str, ...]
    capacity_acres_x100: int
    status: str
    active_from: date | None = None
    active_to: date | None = None


@dataclass(frozen=True)
class CentreIn:
    id: int
    name: str
    lat: float
    lon: float
    is_home: bool
    service_types: tuple[str, ...]


@dataclass(frozen=True)
class ExistingSlot:
    machine_id: int
    service_date: date
    acres_x100: int
    lat: float | None = None
    lon: float | None = None
    request_id: int | None = None


@dataclass(frozen=True)
class Settings:
    max_radius_km: float = 25.0
    road_factor: float = 1.3


@dataclass
class Assignment:
    request_id: int
    machine_id: int
    service_date: date
    seq: int
    est_distance_km: float
    explanation: str


@dataclass
class Miss:
    request_id: int
    reason_code: str
    reason: str
    data_used: dict[str, Any]
    next_action: str | None
    nearest_alternative: str | None
    alternative_distance_km: float | None


@dataclass
class Plan:
    assignments: list[Assignment]
    misses: list[Miss]


def days_inclusive(start: date, end: date) -> Iterator[date]:
    """Yield every date from start to end inclusive."""
    curr = start
    while curr <= end:
        yield curr
        curr += timedelta(days=1)


def plan(
    requests: list[RequestIn],
    machines: list[MachineIn],
    centres: list[CentreIn],
    existing_slots: list[ExistingSlot],
    today: date,
    settings: Settings,
) -> Plan:
    """Deterministic, pure scheduler."""
    raise NotImplementedError("plan() will be implemented in Step 05.")
