"""API routes for slot lifecycle and evidence capture (Contract Section 11)."""

from datetime import date
from typing import Any
from fastapi import APIRouter, Depends, File, Form, Header, Query, UploadFile
from sqlalchemy.orm import Session
from app import clock
from app.auth import verify_slot_auth
from app.config import settings
from app.db import get_db
from app.errors import VaariError
from app.evidence.lifecycle import done_slot, not_served_slot, start_slot
from app.models import Machine, Slot
from app.routes.common import serialize_slot
from app.schemas import EvidenceDetail, NotServedIn, SlotEvidenceOut, SlotOut

router = APIRouter(prefix="/slots", tags=["slots"])


@router.get("", response_model=list[SlotOut])
def list_slots(
    date: date | None = Query(None),
    machine_id: int | None = Query(None),
    x_vaari_passcode: str | None = Header(None, alias="X-Vaari-Passcode"),
    x_vaari_machine_token: str | None = Header(None, alias="X-Vaari-Machine-Token"),
    session: Session = Depends(get_db),
):
    # Auth: passcode (operator) or machine token (driver for that machine)
    machine_for_token = None
    if x_vaari_machine_token:
        machine_for_token = (
            session.query(Machine).filter_by(link_token=x_vaari_machine_token).first()
        )
        if not machine_for_token:
            raise VaariError("UNAUTHORIZED", "Invalid machine token.", 401)
    elif not x_vaari_passcode or x_vaari_passcode != settings.demo_passcode:
        raise VaariError("UNAUTHORIZED", "Passcode or machine token required.", 401)

    query = session.query(Slot)
    if machine_for_token:
        query = query.filter(Slot.machine_id == machine_for_token.id)
    elif machine_id:
        query = query.filter(Slot.machine_id == machine_id)

    if date:
        query = query.filter(Slot.service_date == date)

    slots = query.order_by(Slot.service_date.asc(), Slot.seq.asc()).all()
    return [serialize_slot(session, s, include_link_token=True) for s in slots]


@router.post("/{id}/start", response_model=SlotEvidenceOut)
async def start_slot_endpoint(
    id: int,
    photo: UploadFile | None = File(None),
    lat: float | None = Form(None),
    lon: float | None = Form(None),
    accuracy_m: float | None = Form(None),
    x_vaari_slot_token: str | None = Header(None, alias="X-Vaari-Slot-Token"),
    x_vaari_passcode: str | None = Header(None, alias="X-Vaari-Passcode"),
    session: Session = Depends(get_db),
):
    slot = session.query(Slot).filter_by(id=id).first()
    if slot is None:
        raise VaariError("NOT_FOUND", "Slot not found.", 404)

    # 1. Auth check
    verify_slot_auth(slot, x_vaari_slot_token, x_vaari_passcode)

    # 2. Lifecycle start
    ev, pos_state = await start_slot(
        session=session,
        slot=slot,
        photo=photo,
        lat=lat,
        lon=lon,
        accuracy_m=accuracy_m,
    )
    session.commit()

    return SlotEvidenceOut(
        slot_id=slot.id,
        status=slot.status,
        evidence=EvidenceDetail(
            kind=ev.kind,
            lat=ev.lat,
            lon=ev.lon,
            accuracy_m=ev.accuracy_m,
            distance_to_plot_m=ev.distance_to_plot_m,
            plausible=ev.plausible,
            position_state=pos_state,
            photo="present" if ev.photo_path else "none",
            timestamp=clock.iso_z(ev.server_time),
        ),
        flags=slot.flags_json or [],
        needs_review=slot.needs_review,
        record_url=None,
    )


@router.post("/{id}/done", response_model=SlotEvidenceOut)
async def done_slot_endpoint(
    id: int,
    photo: UploadFile | None = File(None),
    lat: float | None = Form(None),
    lon: float | None = Form(None),
    accuracy_m: float | None = Form(None),
    service_code: str | None = Form(None),
    x_vaari_slot_token: str | None = Header(None, alias="X-Vaari-Slot-Token"),
    x_vaari_passcode: str | None = Header(None, alias="X-Vaari-Passcode"),
    session: Session = Depends(get_db),
):
    slot = session.query(Slot).filter_by(id=id).first()
    if slot is None:
        raise VaariError("NOT_FOUND", "Slot not found.", 404)

    # 1. Auth check
    verify_slot_auth(slot, x_vaari_slot_token, x_vaari_passcode)

    # 2. Lifecycle done
    ev, record, pos_state = await done_slot(
        session=session,
        slot=slot,
        photo=photo,
        lat=lat,
        lon=lon,
        accuracy_m=accuracy_m,
        service_code=service_code,
    )
    session.commit()

    base_url = settings.public_base_url
    record_url = f"{base_url}/record/{record.token}" if base_url else f"/record/{record.token}"

    return SlotEvidenceOut(
        slot_id=slot.id,
        status=slot.status,
        evidence=EvidenceDetail(
            kind=ev.kind,
            lat=ev.lat,
            lon=ev.lon,
            accuracy_m=ev.accuracy_m,
            distance_to_plot_m=ev.distance_to_plot_m,
            plausible=ev.plausible,
            position_state=pos_state,
            photo="present" if ev.photo_path else "none",
            timestamp=clock.iso_z(ev.server_time),
        ),
        flags=slot.flags_json or [],
        needs_review=slot.needs_review,
        record_url=record_url,
    )


@router.post("/{id}/not-served", response_model=SlotOut)
def not_served_slot_endpoint(
    id: int,
    payload: NotServedIn,
    x_vaari_slot_token: str | None = Header(None, alias="X-Vaari-Slot-Token"),
    x_vaari_passcode: str | None = Header(None, alias="X-Vaari-Passcode"),
    session: Session = Depends(get_db),
):
    slot = session.query(Slot).filter_by(id=id).first()
    if slot is None:
        raise VaariError("NOT_FOUND", "Slot not found.", 404)

    verify_slot_auth(slot, x_vaari_slot_token, x_vaari_passcode)

    slot = not_served_slot(
        session=session,
        slot=slot,
        reason=payload.reason.value,
        note=payload.note,
    )
    session.commit()

    return serialize_slot(session, slot, include_link_token=True)
