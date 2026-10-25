"""Dashboard summary API route (Contract Section 11)."""

from datetime import date, timedelta
from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app import clock
from app.auth import require_passcode
from app.db import get_db
from app.models import Machine, Plot, Request, Slot

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary(
    village: str | None = Query(None),
    date: date | None = Query(None),
    machine_id: int | None = Query(None),
    status: str | None = Query(None),
    session: Session = Depends(get_db),
    _passcode: str = Depends(require_passcode),
) -> dict[str, Any]:
    today = clock.today()

    # Query requests
    req_query = session.query(Request)
    if village:
        req_query = req_query.join(Plot, Request.plot_id == Plot.id).filter(Plot.village_name == village)
    if status:
        req_query = req_query.filter(Request.status == status)

    all_requests = req_query.all()
    total_reqs = len(all_requests)

    needs_info_count = sum(1 for r in all_requests if r.status == "needs_info")
    will_miss_count = sum(1 for r in all_requests if r.status == "will_miss")

    # by_reason
    by_reason: dict[str, int] = {}
    for r in all_requests:
        if r.status == "will_miss" and r.reason_code:
            by_reason[r.reason_code] = by_reason.get(r.reason_code, 0) + 1

    # by_village
    by_village: dict[str, int] = {}
    for r in all_requests:
        p = session.query(Plot).filter_by(id=r.plot_id).first()
        v_name = p.village_name if p else "Unknown"
        by_village[v_name] = by_village.get(v_name, 0) + 1

    # Slots query
    slot_query = session.query(Slot)
    if date:
        slot_query = slot_query.filter(Slot.service_date == date)
    if machine_id:
        slot_query = slot_query.filter(Slot.machine_id == machine_id)
    if village:
        slot_query = slot_query.join(Request, Slot.request_id == Request.id).join(
            Plot, Request.plot_id == Plot.id
        ).filter(Plot.village_name == village)

    all_slots = slot_query.all()
    scheduled_count = sum(1 for s in all_slots if s.status == "scheduled")
    in_progress_count = sum(1 for s in all_slots if s.status == "in_progress")
    completed_count = sum(1 for s in all_slots if s.status == "done")
    needs_review_count = sum(1 for s in all_slots if s.needs_review)

    # capacity_used_pct: scheduled-or-done acres ÷ active machine capacity over 7 days starting today
    active_machines = session.query(Machine).filter_by(status="active").all()
    seven_days = [today + timedelta(days=i) for i in range(7)]

    total_cap_x100 = 0
    for m in active_machines:
        for d in seven_days:
            if (m.active_from is None or d >= m.active_from) and (
                m.active_to is None or d <= m.active_to
            ):
                total_cap_x100 += m.capacity_acres_x100

    seven_day_slots = (
        session.query(Slot)
        .filter(
            Slot.service_date >= today,
            Slot.service_date <= today + timedelta(days=6),
            Slot.status.in_(["scheduled", "in_progress", "done"]),
        )
        .all()
    )

    used_cap_x100 = 0
    for s in seven_day_slots:
        r = session.query(Request).filter_by(id=s.request_id).first()
        if r:
            used_cap_x100 += r.acres_x100

    if total_cap_x100 > 0:
        capacity_used_pct = round(100.0 * used_cap_x100 / total_cap_x100)
    else:
        capacity_used_pct = 0

    return {
        "total": total_reqs,
        "needs_info": needs_info_count,
        "scheduled": scheduled_count,
        "in_progress": in_progress_count,
        "completed": completed_count,
        "will_miss": will_miss_count,
        "needs_review": needs_review_count,
        "capacity_used_pct": capacity_used_pct,
        "by_reason": by_reason,
        "by_village": by_village,
        "today": today.isoformat(),
    }
