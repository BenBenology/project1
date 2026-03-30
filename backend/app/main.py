"""FastAPI entrypoint for the MVP backend."""

from fastapi import FastAPI

from backend.app.api.routes import health, tasks
from backend.app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Stock Research MVP API",
    version="0.1.0",
    description="Mock API for financial report and article aggregation.",
)

app.include_router(health.router)
app.include_router(tasks.router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    """Expose a simple landing response for quick verification."""
    return {
        "message": "Stock Research MVP API is running.",
        "docs_url": "/docs",
        "environment": settings.app_env,
    }
