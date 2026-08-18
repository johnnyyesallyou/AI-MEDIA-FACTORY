import sys
import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.api.v1.router import api_v1_router
from backend.app.api.v1.health import router as health_router
from backend.automation.scheduler import automation_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 AI Media Factory Dashboard starting...", flush=True)
    
    # Безопасный асинхронный запуск планировщика в фоне
    asyncio.create_task(automation_scheduler.start())
    print("🚀 Automation scheduler task created in background", flush=True)

    yield
    print("👋 Shutting down...", flush=True)

app = FastAPI(
    title="AI Media Factory Dashboard API",
    description="API и интерфейс для управления AI Media Factory",
    version="1.0.0 Beta",
    lifespan=lifespan
)


# Sprint 11: Serving generated assets
import os
os.makedirs("/app/assets", exist_ok=True)
app.mount("/assets", StaticFiles(directory="/app/assets"), name="assets")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Безопасное монтирование статики (с проверкой существования папок)
static_dir = "backend/static"
templates_dir = "backend/templates"

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=templates_dir)
app.include_router(api_v1_router)
app.include_router(health_router, prefix="/api/v1")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health")
def health():
    return {"status": "ok", "service": "backend"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
