import sys
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.api.v1.router import api_v1_router
from backend.automation.scheduler import automation_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 AI Media Factory Dashboard starting...")

    automation_scheduler.start()

    print("🚀 Automation scheduler started from lifespan")

    yield

    print("👋 Stopping scheduler...")

    try:
        await automation_scheduler.stop()
    except Exception as e:
        print(f"Scheduler stop error: {e}")

    print("👋 Shutting down...")


app = FastAPI(
    title="AI Media Factory Dashboard API",
    description="API и интерфейс для управления AI Media Factory",
    version="1.0.0 Beta",
    lifespan=lifespan
)
