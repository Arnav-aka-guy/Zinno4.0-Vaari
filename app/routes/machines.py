"""API routes for managing machines (Contract Section 11)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.auth import require_passcode
from app.db import get_db
from app.enums import MachineStatus, to_x100
from app.errors import VaariError
from app.event_log import log_event
from app.models import Machine, Request, Slot
from app.routes.common import get_or_create_home_centre, serialize_machine
from app.schemas import MachineIn, MachinePatch, MachineOut
from app.scheduler.service import run_for_centre
from app.tokens import new_token

router = APIRouter(prefix="/machines", tags=["machines"])


@router.post("", response_model=MachineOut, status_code=status.HTTP_201_CREATED)
def create_machine(
    payload: MachineIn,
    session: Session = Depends(get_db),
    _passcode: str = Depends(require_passcode),
):
    home_centre = get_or_create_home_centre(session)

    machine = Machine(
        centre_id=home_centre.id,
        name=payload.name,
        type=payload.type,
        service_types=[st.value for st in payload.service_types],
        capacity_acres_x100=to_x100(payload.capacity_acres_per_day),
        implement_width_m=payload.implement_width_m,
        active_from=payload.active_from,
        active_to=payload.active_to,
        status="active",
        link_token=new_token(),
    )
    session.add(machine)
    session.flush()

    log_event(
        session=session,
        actor="operator",
        entity="machine",
        entity_id=machine.id,
        event="created",
        payload={"name": machine.name},
    )
    session.commit()

    return serialize_machine(machine)


@router.get("", response_model=list[MachineOut])
def list_machines(
    session: Session = Depends(get_db),
    _passcode: str = Depends(require_passcode),
):
    machines = session.query(Machine).order_by(Machine.id.asc()).all()
    return [serialize_machine(m) for m in machines]


@router.patch("/{id}", response_model=MachineOut)
def patch_machine(
    id: int,
    payload: MachinePatch,
    session: Session = Depends(get_db),
    _passcode: str = Depends(require_passcode),
):
    machine = session.query(Machine).filter_by(id=id).first()
    if machine is None:
        raise VaariError("NOT_FOUND", "Machine not found.", 404)

    if payload.name is not None:
        machine.name = payload.name
    if payload.type is not None:
        machine.type = payload.type
    if payload.service_types is not None:
        machine.service_types = [st.value for st in payload.service_types]
    if payload.capacity_acres_per_day is not None:
        machine.capacity_acres_x100 = to_x100(payload.capacity_acres_per_day)
    if payload.implement_width_m is not None:
        machine.implement_width_m = payload.implement_width_m
    if payload.active_from is not None:
        machine.active_from = payload.active_from
    if payload.active_to is not None:
        machine.active_to = payload.active_to

    status_changed_to_inactive = False
    if payload.status is not None:
        if payload.status == MachineStatus.INACTIVE and machine.status != "inactive":
            status_changed_to_inactive = True
        machine.status = payload.status.value

    session.flush()

    if status_changed_to_inactive:
        # Cancel that machine's slots that have not started
        unstarted_slots = (
            session.query(Slot)
            .filter_by(machine_id=machine.id, status="scheduled")
            .all()
        )
        for s in unstarted_slots:
            s.status = "cancelled"
            req = session.query(Request).filter_by(id=s.request_id).first()
            if req and req.status not in ("done", "cancelled"):
                req.status = "open"
        session.flush()

        home_centre = get_or_create_home_centre(session)
        run_for_centre(session, home_centre.id)

    log_event(
        session=session,
        actor="operator",
        entity="machine",
        entity_id=machine.id,
        event="patched",
        payload=payload.model_dump(exclude_unset=True),
    )
    session.commit()

    return serialize_machine(machine)
