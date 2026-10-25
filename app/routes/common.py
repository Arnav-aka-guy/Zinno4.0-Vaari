"""Common route helpers and model serializers."""

from sqlalchemy.orm import Session
from app import clock
from app.config import settings
from app.enums import from_x100
from app.models import Centre, Farmer, Machine, Plot, Request, Slot
from app.schemas import (
    ExplanationBrief,
    FarmerBrief,
    MachineOut,
    PlotOut,
    RequestOut,
    SlotBrief,
)


def get_or_create_home_centre(session: Session) -> Centre:
    """Ensure exactly one home centre exists, creating it from settings if needed."""
    centre = session.query(Centre).filter_by(is_home=True).first()
    if centre is None:
        centre = Centre(
            name=settings.centre_name,
            phone=settings.centre_phone,
            lat=settings.centre_lat,
            lon=settings.centre_lon,
            is_home=True,
            service_types=["super_seeder", "happy_seeder", "baler", "mulcher"],
        )
        session.add(centre)
        session.flush()
    return centre


def serialize_request(session: Session, req: Request) -> RequestOut:
    farmer = session.query(Farmer).filter_by(id=req.farmer_id).first()
    plot = session.query(Plot).filter_by(id=req.plot_id).first()
    slot = session.query(Slot).filter_by(request_id=req.id).filter(Slot.status != "cancelled").first()

    slot_brief = None
    if slot is not None:
        machine = session.query(Machine).filter_by(id=slot.machine_id).first()
        machine_name = machine.name if machine else "Unknown"
        slot_brief = SlotBrief(
            id=slot.id,
            machine_id=slot.machine_id,
            machine_name=machine_name,
            service_date=slot.service_date,
            seq=slot.seq,
            status=slot.status,
        )

    badges = []
    if req.source == "seed":
        badges.append("seeded request")
    if farmer and farmer.consent_simulated:
        badges.append("consent simulated")

    return RequestOut(
        id=req.id,
        status=req.status,
        source=req.source,
        farmer=FarmerBrief(name=farmer.name if farmer else None, phone=farmer.phone if farmer else ""),
        village=plot.village_name if plot else "",
        acres=from_x100(req.acres_x100),
        service_type=req.service_type,
        harvest_date=req.harvest_date,
        sow_by=req.sow_by,
        deadline_date=req.deadline_date,
        explanation=ExplanationBrief(
            reason_code=req.reason_code,
            reason=req.reason,
            data_used=req.data_used_json or {},
            next_action=req.next_action,
            nearest_alternative=req.nearest_alternative,
            alternative_distance_km=req.alternative_distance_km,
        ),
        slot=slot_brief,
        badges=badges,
        created_at=clock.iso_z(req.created_at),
    )


def serialize_machine(machine: Machine) -> MachineOut:
    return MachineOut(
        id=machine.id,
        name=machine.name,
        type=machine.type,
        service_types=machine.service_types or [],
        capacity_acres_per_day=from_x100(machine.capacity_acres_x100),
        status=machine.status,
        active_from=machine.active_from,
        active_to=machine.active_to,
        driver_path=f"/driver/{machine.link_token}",
    )


def serialize_plot(plot: Plot) -> PlotOut:
    return PlotOut(
        id=plot.id,
        farmer_id=plot.farmer_id,
        village_name=plot.village_name,
        acres=from_x100(plot.acres_x100),
        pin_lat=plot.pin_lat,
        pin_lon=plot.pin_lon,
        centroid_lat=plot.centroid_lat,
        centroid_lon=plot.centroid_lon,
        location_source=plot.location_source,
        geojson=plot.geojson,
    )
