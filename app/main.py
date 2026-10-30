"""Main FastAPI application for Vaari."""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.routing import Match, Route

from app.config import settings
from app.db import Base, get_engine, get_session_factory
from app.errors import setup_error_handlers
import app.models  # ensure models are registered
from app.routes.common import get_or_create_home_centre
from app.routes.dashboard import router as dashboard_router
from app.routes.driver import router as driver_router
from app.routes.health import router as health_router
from app.routes.intake import router as intake_router
from app.routes.machines import router as machines_router
from app.routes.plots import router as plots_router
from app.routes.records import router as records_router
from app.routes.requests import router as requests_router
from app.routes.schedule import router as schedule_router
from app.routes.slots import router as slots_router
from app.startup_checks import enforce_startup_checks


@asynccontextmanager
async def lifespan(app: FastAPI):
    enforce_startup_checks(settings)
    Base.metadata.create_all(bind=get_engine())
    session_factory = get_session_factory()
    with session_factory() as session:
        get_or_create_home_centre(session)
        session.commit()
    yield


app = FastAPI(title="Vaari Backend", version="0.1", lifespan=lifespan)

setup_error_handlers(app)

app.include_router(health_router, prefix="/api")
app.include_router(requests_router, prefix="/api")
app.include_router(machines_router, prefix="/api")
app.include_router(plots_router, prefix="/api")
app.include_router(schedule_router, prefix="/api")
app.include_router(slots_router, prefix="/api")
app.include_router(driver_router, prefix="/api")
app.include_router(records_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(intake_router, prefix="/api")

web_dist = Path(__file__).parent.parent / "web" / "dist"


class NonApiRoute(Route):
    def matches(self, scope):
        if scope["type"] == "http" and (
            scope["path"] == "/api" or scope["path"].startswith("/api/")
        ):
            return Match.NONE, {}
        return super().matches(scope)


async def spa_fallback(request: Request):
    full_path = request.path_params.get("full_path", "")
    file_path = web_dist / full_path
    if full_path and file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    index_file = web_dist / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    raise StarletteHTTPException(
        status_code=404,
        detail="Frontend not built. Run 'python tasks.py build-web'.",
    )


app.router.routes.append(
    NonApiRoute("/{full_path:path}", endpoint=spa_fallback, methods=["GET", "HEAD"])
)
if (web_dist / "assets").exists():
    app.mount("/assets", StaticFiles(directory=web_dist / "assets"), name="assets")
