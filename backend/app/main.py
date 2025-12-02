from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import integration, pipelines
from app.core.config import get_settings
from app.db.session import init_db

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.include_router(pipelines.router, prefix=settings.api_prefix)
app.include_router(integration.router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def health_check():
    return {"status": "ok", "app": settings.app_name}
