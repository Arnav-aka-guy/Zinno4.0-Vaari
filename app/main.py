"""Main FastAPI application for Vaari."""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.db import Base, get_engine
from app.errors import setup_error_handlers
import app.models  # ensure models are registered
from app.routes.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables at startup
    Base.metadata.create_all(bind=get_engine())
    yield


app = FastAPI(title="Vaari Backend", version="0.1", lifespan=lifespan)

# Configure error handlers
setup_error_handlers(app)

# Mount API routers
app.include_router(health_router, prefix="/api")

# Serve frontend build if available (Phase 2)
web_dist = Path(__file__).parent.parent / "web" / "dist"
if web_dist.exists():
    app.mount("/assets", StaticFiles(directory=web_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        if full_path.startswith("api/"):
            pass
        file_path = web_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        index_file = web_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
