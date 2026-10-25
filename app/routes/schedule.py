"""API routes for scheduling (Contract Section 11)."""

from datetime import date
from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.auth import require_passcode
from app.db import get_db
from app.enums import from_x100
from app.models import Machine, Plot, Request, Slot
from app.routes.common import get_or_create_home_centre, serialize_slot
from app.scheduler.service import run_for_centre

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.post("/run")
def trigger_schedule_run(
    session: Session = Depends(get_db),
    _passcode: str = Depends(require_passcode),
) -> dict[str, Any]:
    home_centre = get_or_create_home_centre(session)
    counts = run_for_centre(session, home_centre.id)
    session.commit()
    return counts


@router.get("")
def get_schedule(
    date: date | None = Query(None),
    machine_id: int | None = Query(None),
    session: Session = Depends(get_db),
    _passcode: str = Depends(require_passcode),
) -> list[dict[str, Any]]:
    query = session.query(Slot).filter(Slot.status.in_(["scheduled", "in_progress", "done"]))
    if date:
        query = query.filter(Slot.service_date == date)
    if machine_id:
        query = query.filter(Slot.machine_id == machine_id)

    slots = query.order_by(Slot.service_date.asc(), Slot.machine_id.asc(), Slot.seq.asc()).all()

    # Group by (machine_id, service_date)
    grouped: dict[tuple[int, date], list[Slot]] = {}
    for s in slots:
        grouped.setdefault((s.machine_id, s.service_date), []).append(s)

    result = []
    for (m_id, s_date), machine_slots in grouped.items():
        machine = session.query(Machine).filter_by(id=m_id).first()
        m_name = machine.name if machine else "Unknown"
        cap = from_x100(machine.capacity_acres_x100) if machine else 0.0

        used_x100 = 0
        serialized_slots = []
        for ms in machine_slots:
            req = session.query(Request).filter_by(id=ms.request_id).first()
            if req:
                used_x100 += req.acres_x100
            serialized_slots.append(serialize_slot(session, ms))

        result.append({
            "machine_id": m_id,
            "machine_name": m_name,
            "date": str(s_date),
            "capacity_acres": cap,
            "used_acres": from_x100(used_x100),
            "slots": serialized_slots,
        })

    return result


@router.get("/will-miss")
def get_will_miss_requests(
    session: Session = Depends(get_db),
    _passcode: str = Depends(require_passcode),
) -> list[dict[str, Any]]:
    misses = (
        session.query(Request)
        .filter_by(status="will_miss")
        .order_by(Request.deadline_date.asc().nullslast(), Request.id.asc())
        .all()
    )

    items = []
    for r in misses:
        plot = session.query(Plot).filter_by(id=r.plot_id).first()
        items.append({
            "request_id": r.id,
            "village": plot.village_name if plot else "",
            "acres": from_x100(r.acres_x100),
            "service_type": r.service_type,
            "deadline_date": str(r.deadline_date) if r.deadline_date else None,
            "status": r.status,
            "reason_code": r.reason_code,
            "reason": r.reason,
            "data_used": r.data_used_json or {},
            "next_action": r.next_action,
            "nearest_alternative": r.nearest_alternative,
            "alternative_distance_km": r.alternative_distance_km,
        })
    return items
