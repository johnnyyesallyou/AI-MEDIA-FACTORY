import sys
import os
import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Setup structured logging early
from backend.app.core.logging_config import setup_logging, get_logger

setup_logging(
    log_dir=os.getenv("LOG_DIR", "logs"),
    console_level=logging.INFO,
    file_level=logging.DEBUG,
    enable_json=os.getenv("JSON_LOGGING", "true").lower() == "true"
)

logger = get_logger(__name__)

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.api.v1.router import api_v1_router
from backend.app.api.v1 import metrics, health as health_router, system_metrics
from backend.automation.scheduler import automation_scheduler
from backend.automation.runtime.jobs_registry import register_all_jobs
from core.alerts import start_alerts_loop
from engines.content_optimization.feedback_loop import start_feedback_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events"""
    logger.info("🚀 AI Media Factory Dashboard starting...")
    
    # Skip background tasks in test mode
    if os.getenv("APP_ENV") != "test":
        # Sprint 15: Start automation scheduler asynchronously
        asyncio.create_task(automation_scheduler.start())

        # Sprint 44: alerts loop
        asyncio.create_task(start_alerts_loop())

        # Sprint 45: feedback loop
        asyncio.create_task(start_feedback_loop(interval_hours=6))
        
        logger.info("✅ Automation scheduler task created in background")
    else:
        logger.info("ℹ️ Test mode: skipping background tasks")
    
    yield
    
    logger.info("👋 Shutting down...")
    
    # Sprint 15: Gracefully stop scheduler on shutdown
    if os.getenv("APP_ENV") != "test":
        try:
            await automation_scheduler.stop()
            logger.info("✅ Automation scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Automation scheduler stop error: {e}", exc_info=True)


app = FastAPI(
    title="AI Media Factory Dashboard API",
    description="API и интерфейс для управления AI Media Factory",
    version="1.0.0 Beta",
    lifespan=lifespan if os.getenv("APP_ENV") != "test" else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")
app.include_router(api_v1_router)
app.include_router(metrics.router)
app.include_router(health_router.router)
app.include_router(system_metrics.router)

# Sprint 11: Serving generated assets
os.makedirs("/app/assets", exist_ok=True)
app.mount("/assets", StaticFiles(directory="/app/assets"), name="assets")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    logger.info("Starting server on 0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
