"""
API endpoints для AutomationManager v2.

Feature flag: USE_AUTOMATION_V2=true (в .env или docker-compose.yml)
"""
import logging
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/automation-v2",
    tags=["automation-v2"]
)


class ChannelRunRequest(BaseModel):
    channel_id: str


class ChannelRunResponse(BaseModel):
    status: str
    task_id: Optional[str] = None
    execution_id: Optional[str] = None
    channel_id: str
    channel_name: Optional[str] = None
    message: Optional[str] = None


def _check_v2_enabled():
    """Проверяет, включен ли AutomationManager v2."""
    use_v2 = os.getenv("USE_AUTOMATION_V2", "false").lower() == "true"
    if not use_v2:
        raise HTTPException(
            status_code=400,
            detail="AutomationManager v2 is disabled. Set USE_AUTOMATION_V2=true to enable."
        )


@router.get("/status")
async def get_automation_v2_status():
    """Статус AutomationManager v2: каналы, очереди, активные задачи."""
    use_v2 = os.getenv("USE_AUTOMATION_V2", "false").lower() == "true"
    
    if not use_v2:
        return {
            "running": False,
            "use_automation_v2": False,
            "message": "AutomationManager v2 is disabled. Set USE_AUTOMATION_V2=true to enable."
        }
    
    try:
        from backend.automation.automation_manager_v2 import automation_manager_v2
        status = automation_manager_v2.get_status()
        return {
            "running": True,
            "use_automation_v2": True,
            **status
        }
    except Exception as e:
        logger.exception("Failed to get AutomationManager v2 status")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-channel", response_model=ChannelRunResponse)
async def run_channel_now(request: ChannelRunRequest):
    """Запускает пайплайн для канала немедленно (через очередь v2)."""
    _check_v2_enabled()
    
    try:
        from backend.automation.automation_manager_v2 import automation_manager_v2
        result = await automation_manager_v2.run_channel_now(request.channel_id)
        
        return ChannelRunResponse(
            status=result.get("status", "unknown"),
            task_id=result.get("task_id"),
            execution_id=result.get("execution_id"),
            channel_id=request.channel_id,
            channel_name=result.get("channel_name"),
            message=result.get("error") if result.get("status") == "failed" else None
        )
    except Exception as e:
        logger.exception("Failed to run channel %s", request.channel_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-all-channels")
async def run_all_channels_now():
    """Запускает пайплайн для всех активных каналов."""
    _check_v2_enabled()
    
    try:
        from backend.automation.automation_manager_v2 import automation_manager_v2
        return await automation_manager_v2.run_all_channels_now()
    except Exception as e:
        logger.exception("Failed to run all channels")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/{channel_id}")
async def get_channel_queue(channel_id: str):
    """Информация об очереди задач для канала."""
    _check_v2_enabled()
    
    try:
        from backend.automation.automation_manager_v2 import automation_manager_v2
        
        if channel_id not in automation_manager_v2.channel_queues:
            raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")
        
        queue = automation_manager_v2.channel_queues[channel_id]
        channel = automation_manager_v2.channels.get(channel_id)
        
        active_tasks = [
            {
                "task_id": task.task_id,
                "status": task.status.value,
                "execution_id": task.execution_id,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "retry_count": task.retry_count,
                "error": task.error
            }
            for task in automation_manager_v2.active_tasks.values()
            if task.channel_id == channel_id
        ]
        
        return {
            "channel_id": channel_id,
            "channel_name": channel.name if channel else "Unknown",
            "queue_size": queue.qsize(),
            "active_tasks": active_tasks,
            "active_tasks_count": len(active_tasks)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get queue for channel %s", channel_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rate-limit/{channel_id}")
async def get_rate_limit_status(channel_id: str):
    """Rate limit статус для канала."""
    _check_v2_enabled()
    
    try:
        from backend.automation.automation_manager_v2 import automation_manager_v2
        from backend.automation.policies import RateLimitPolicy
        
        if channel_id not in automation_manager_v2.channels:
            raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found")
        
        channel = automation_manager_v2.channels[channel_id]
        rate_limit_policy = RateLimitPolicy()
        quota = rate_limit_policy.get_remaining_quota(channel)
        
        return {
            "channel_id": channel_id,
            "channel_name": channel.name,
            **quota
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get rate limit for channel %s", channel_id)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug-run")
async def debug_run_channel(request: ChannelRunRequest):
    """
    ДИАГНОСТИЧЕСКИЙ endpoint: вызывает runner напрямую, МИНУЯ очередь.
    
    Используется для проверки, работает ли runner через v2 manager.
    """
    import asyncio
    use_v2 = os.getenv("USE_AUTOMATION_V2", "false").lower() == "true"
    if not use_v2:
        raise HTTPException(status_code=400, detail="V2 disabled")
    
    try:
        from backend.automation.automation_manager_v2 import automation_manager_v2
        from backend.automation.runner import AutomationRunner
        from core.database import SessionLocal
        from core.models.channel_orm import ChannelORM
        
        db = SessionLocal()
        try:
            channel = db.query(ChannelORM).filter(ChannelORM.id == request.channel_id).first()
            if not channel:
                raise HTTPException(status_code=404, detail="Channel not found")
            
            print(f"🔬 DEBUG: calling runner.run_now() directly for {channel.name}", flush=True)
            logger.info(f"DEBUG: calling runner.run_now() directly for {channel.name}")
            
            runner = AutomationRunner()
            result = await runner.run_now(channel=channel)
            
            print(f"🔬 DEBUG: runner returned successfully", flush=True)
            logger.info(f"DEBUG: runner returned: {result}")
            
            return {
                "status": "ok",
                "mode": "direct_run (bypassing queue)",
                "channel_id": request.channel_id,
                "channel_name": channel.name,
                "result": result
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"DEBUG run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))