import sys
import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# ????????? ?????? ??????? ? sys.path, ????? ???????? ??????? ?? 'core'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.api.v1.router import api_v1_router
from backend.app.api.v1 import metrics, health as health_router, system_metrics
from backend.automation.scheduler import automation_scheduler
from core.alerts import start_alerts_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("?? AI Media Factory Dashboard starting...", flush=True)
    
    # Sprint 15: ????????? automation scheduler ? ????
    asyncio.create_task(automation_scheduler.start())

    # Sprint 44: alerts loop
    asyncio.create_task(start_alerts_loop())
    print("?? Automation scheduler task created in background", flush=True)
    
    yield
    print("?? Shutting down...", flush=True)
    
    # Sprint 15: ????????????? scheduler ??? shutdown
    try:
        await automation_scheduler.stop()
        print("? Automation scheduler stopped", flush=True)
    except Exception as e:
        print(f"?? Automation scheduler stop error: {e}", flush=True)


app = FastAPI(
    title="AI Media Factory Dashboard API",
    description="API ? ????????? ??? ?????????? AI Media Factory",
    version="1.0.0 Beta",
    lifespan=lifespan
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
