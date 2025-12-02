from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import integration, pipelines
from app.core.config import get_settings
from app.core.logger import setup_logger
from app.db.session import init_db

settings = get_settings()

# 初始化日志系统
logger = setup_logger("main")
logger.info(f"Starting {settings.app_name} with log level: {settings.log_level}")

app = FastAPI(title=settings.app_name)
app.include_router(pipelines.router, prefix=settings.api_prefix)
app.include_router(integration.router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup():
    logger.info("Application starting up...")
    init_db()
    logger.info("Database initialized")


@app.get("/")
def health_check():
    logger.debug("Health check endpoint accessed")
    return {"status": "ok", "app": settings.app_name}
