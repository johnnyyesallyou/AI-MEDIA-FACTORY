import uuid
from backend.core.rate_limiter import rate_limit_call
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from core.repositories.channel_repository import ChannelRepository
from core.database import get_db, SessionLocal
from backend.automation.runner import AutomationRunner
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from ....automation.automation_models import AutomationSettings
from ....automation.service import automation_service

from backend.automation.scheduler import automation_scheduler
from core.models.execution_log_orm import ExecutionLogORM

router = APIRouter(
    prefix="/automation",
    tags=["automation"]
)

class AutomationStartResponse(BaseModel):
    status: str
    enabled: bool

class AutomationStopResponse(BaseModel):
    status: str
    enabled: bool

class AutomationRunNowResponse(BaseModel):
    status: str
    execution_id: str
    message: str

@router.get("/", response_model=AutomationSettings)
async def get_automation_settings():
    return automation_service.get_settings()

@router.put("/", response_model=AutomationSettings)
async def update_automation_settings(config: AutomationSettings):
    return automation_service.update_settings(config)

@router.post("/start", response_model=AutomationStartResponse)
async def start_automation():
    print("=== START automation ===", flush=True)
    result = automation_service.start()
    print(f"=== START result: {result} ===", flush=True)
    return AutomationStartResponse(status=result["status"], enabled=result["enabled"])

@router.post("/stop", response_model=AutomationStopResponse)
async def stop_automation():
    print("=== STOP automation ===", flush=True)
    result = automation_service.stop()
    print(f"=== STOP result: {result} ===", flush=True)
    return AutomationStopResponse(status=result["status"], enabled=result["enabled"])

@rate_limit_call("automation_run_now", timeout=30.0)
@router.post("/run-now", response_model=AutomationRunNowResponse)
async def run_automation_now(background_tasks: BackgroundTasks):
    execution_id = str(uuid.uuid4())
    
    print("======================================", flush=True)
    print(f"ENTER /automation/run-now (Execution ID: {execution_id})", flush=True)
    
    # Запускаем тяжелый пайплайн в фоне, не блокируя HTTP-ответ
    background_tasks.add_task(automation_service.run_now)
    
    print("Task added to background. EXIT /automation/run-now", flush=True)
    print("======================================", flush=True)
    
    return AutomationRunNowResponse(
        status="started",
        execution_id=execution_id,
        message="Automation pipeline started in background"
    )


# === SCHEDULER STATUS ===

@router.get("/scheduler/status")
async def get_scheduler_status():
    """Возвращает статус планировщика: запущен ли, сколько задач, следующая задача."""
    if not automation_scheduler.scheduler:
        return {
            "running": False,
            "total_jobs": 0,
            "jobs": []
        }
    
    jobs = automation_scheduler.scheduler.get_jobs()
    jobs_info = []
    for job in jobs:
        channel_id = job.id.replace("channel_", "")
        jobs_info.append({
            "channel_id": channel_id,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "name": job.name
        })
    
    # Сортируем по next_run_time (ближайшие первыми)
    jobs_info.sort(key=lambda x: x["next_run_time"] or "9999")
    
    return {
        "running": automation_scheduler.scheduler.running,
        "total_jobs": len(jobs),
        "jobs": jobs_info
    }


# === RETRY STAGE ===

class RetryRequest(BaseModel):
    execution_id: str
    stage: str

class RetryResponse(BaseModel):
    status: str
    new_execution_id: str
    stage: str
    message: str

VALID_STAGES = ["research", "decision", "writing", "evaluation", "revision", "re_evaluation", "publish"]

@router.post("/retry", response_model=RetryResponse)
async def retry_stage(request: RetryRequest, background_tasks: BackgroundTasks):
    """Повторяет один конкретный этап пайплайна для канала из исходного запуска."""
    if request.stage not in VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Valid: {VALID_STAGES}")

    # Находим channel_id из исходного execution_id
    db = SessionLocal()
    try:
        log = db.query(ExecutionLogORM).filter(
            ExecutionLogORM.execution_id == request.execution_id
        ).first()

        if not log:
            raise HTTPException(status_code=404, detail="Execution not found")

        channel_id = log.channel_id
        channel = None
        if channel_id:
            repo = ChannelRepository(db)
            channel = repo.get(channel_id)
    finally:
        db.close()

    new_execution_id = f"retry-{request.execution_id}-{request.stage}"

    async def _do_retry():
        runner = AutomationRunner()
        await runner.retry_stage(channel, request.stage, new_execution_id)

    background_tasks.add_task(_do_retry)

    return RetryResponse(
        status="started",
        new_execution_id=new_execution_id,
        stage=request.stage,
        message=f"Retrying stage '{request.stage}' for execution {request.execution_id}"
    )
