"""API routes for managing plots (Contract Section 11)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app import clock
from app.auth import require_passcode
from app.db import get_db
from app.enums import to_x100
from app.errors import VaariError
from app.models import Farmer, Plot, Village
from app.routes.common import serialize_plot
from app.schemas import PlotIn, PlotOut

router = APIRouter(prefix="/plots", tags=["plots"])


@router.post("", response_model=PlotOut, status_code=status.HTTP_201_CREATED)
def create_plot(
    payload: PlotIn,
    session: Session = Depends(get_db),
    _passcode: str = Depends(require_passcode),
):
    farmer = session.query(Farmer).filter_by(phone=payload.farmer_phone).first()
    if farmer is None:
        farmer = Farmer(
            phone=payload.farmer_phone,
            name=None,
            language="pa",
            consent_service=True,
            consent_evidence=True,
            consent_share=True,
            consent_at=clock.now_utc(),
            consent_simulated=True,
        )
        session.add(farmer)
        session.flush()

    village = session.query(Village).filter_by(name=payload.village).first()
    village_id = village.id if village else None

    if payload.pin_lat is not None and payload.pin_lon is not None:
        location_source = "pin"
        pin_lat, pin_lon = payload.pin_lat, payload.pin_lon
    elif payload.geojson is not None:
        location_source = "polygon"
        pin_lat, pin_lon = None, None
    elif village is not None:
        location_source = "village"
        pin_lat, pin_lon = village.lat, village.lon
    else:
        location_source = "none"
        pin_lat, pin_lon = None, None

    acres_x100 = to_x100(payload.acres)
    plot = Plot(
        farmer_id=farmer.id,
        village_name=payload.village,
        village_id=village_id,
        pin_lat=pin_lat,
        pin_lon=pin_lon,
        geojson=payload.geojson,
        acres_x100=acres_x100,
        centroid_lat=pin_lat,
        centroid_lon=pin_lon,
        location_source=location_source,
    )
    session.add(plot)
    session.commit()

    return serialize_plot(plot)


@router.get("", response_model=list[PlotOut])
def list_plots(
    session: Session = Depends(get_db),
    _passcode: str = Depends(require_passcode),
):
    plots = session.query(Plot).order_by(Plot.id.asc()).all()
    return [serialize_plot(p) for p in plots]


@router.get("/{id}", response_model=PlotOut)
def get_plot(
    id: int,
    session: Session = Depends(get_db),
    _passcode: str = Depends(require_passcode),
):
    plot = session.query(Plot).filter_by(id=id).first()
    if plot is None:
        raise VaariError("NOT_FOUND", "Plot not found.", 404)
    return serialize_plot(plot)
