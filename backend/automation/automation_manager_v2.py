"""
AutomationManager v2 — Unified Orchestration Layer.

Главный сервис платформы для автономной работы с несколькими каналами.

Возможности:
- Channel Isolation (изолированные очереди для каждого канала)
- Workflow Engine (конфигурируемые workflows)
- Policy Engine (retry, rate limits, error handling)
- Queue Manager (Redis-based queues)
- Error Handler (центральное логирование)
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

from sqlalchemy.orm import Session
from core.database import SessionLocal
try:
    from backend.core.error_logger import get_error_logger
except ImportError:
    get_error_logger = None
from core.models.channel_orm import ChannelORM
from core.models.execution_log_orm import ExecutionLogORM

from .runner import AutomationRunner
from .policies import RetryPolicy, RateLimitPolicy, ErrorHandlingPolicy
from .workflow import WorkflowDefinition, WorkflowStage


logger = logging.getLogger(__name__)

# Sprint 66.3: Task timeout (5 minutes)
TASK_TIMEOUT = 600  # seconds



class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class ChannelTask:
    """Задача для конкретного канала."""
    task_id: str
    channel_id: str
    channel_name: str
    workflow: WorkflowDefinition
    status: TaskStatus = TaskStatus.PENDING
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class AutomationManagerV2:
    """
    Unified Orchestration Layer для автономной работы с несколькими каналами.
    
    Замена старого AutomationManager, который был просто wrapper над Runner.
    """
    
    def __init__(self):
        self.runner = AutomationRunner()
        self.channels: Dict[str, ChannelORM] = {}
        self.channel_queues: Dict[str, asyncio.Queue] = {}
        self.active_tasks: Dict[str, ChannelTask] = {}
        self.workers: Dict[str, asyncio.Task] = {}
        
        # Policies
        self.retry_policy = RetryPolicy(max_retries=3, backoff_factor=2.0)
        self.rate_limit_policy = RateLimitPolicy()
        self.error_handling_policy = ErrorHandlingPolicy()
        
        logger.info("AutomationManager v2 initialized")
    
    async def start(self):
        """Запускает AutomationManager и всех workers."""
        logger.info("Starting AutomationManager v2...")
        
        # Загружаем все активные каналы
        await self._load_channels()
        
        # Создаём очереди и workers для каждого канала
        for channel_id, channel in self.channels.items():
            await self._create_channel_queue(channel_id)
            await self._start_channel_worker(channel_id)
        
        logger.info(f"AutomationManager v2 started with {len(self.channels)} channels")
    
    async def stop(self):
        """Останавливает AutomationManager и всех workers."""
        logger.info("Stopping AutomationManager v2...")
        
        # Останавливаем всех workers
        for channel_id, worker_task in self.workers.items():
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass
        
        self.workers.clear()
        self.channel_queues.clear()
        
        logger.info("AutomationManager v2 stopped")
    
    async def _load_channels(self):
        """Загружает все активные каналы из БД."""
        print("🔍 Loading channels from DB...", flush=True)
        db = SessionLocal()
        try:
            channels = db.query(ChannelORM).filter(ChannelORM.is_active == True).all()
            for channel in channels:
                print(f"  ✅ Loaded channel: {channel.name} ({channel.id})", flush=True)
                self.channels[channel.id] = channel
                logger.info(f"Loaded channel: {channel.name} (id={channel.id})")
        finally:
            db.close()
    
    async def _create_channel_queue(self, channel_id: str):
        """Создаёт изолированную очередь для канала."""
        if channel_id not in self.channel_queues:
            self.channel_queues[channel_id] = asyncio.Queue()
            logger.info(f"Created queue for channel {channel_id}")
            print(f"  📦 Created queue for {channel_id[:8]}...", flush=True)
    
    async def _start_channel_worker(self, channel_id: str):
        """Запускает worker для обработки очереди канала."""
        if channel_id not in self.workers:
            print(f"  🚀 Creating asyncio task for {channel_id[:8]}...", flush=True)
            worker_task = asyncio.create_task(self._channel_worker(channel_id))
            self.workers[channel_id] = worker_task
            logger.info(f"Started worker for channel {channel_id}")
            print(f"  ✅ Worker task created for {channel_id[:8]}...", flush=True)
    
    async def _channel_worker(self, channel_id: str):
        """Worker для обработки задач из очереди канала."""
        logger.info(f"Channel worker started for {channel_id}")
        print(f"⚡⚡⚡ CHANNEL WORKER ACTIVE for {channel_id} ⚡⚡⚡", flush=True)
        print(f"   Queue object: {self.channel_queues.get(channel_id)}", flush=True)
        
        while True:
            try:
                print(f"   ⏳ Waiting for task in queue {channel_id[:8]}...", flush=True)
                task: ChannelTask = await self.channel_queues[channel_id].get()
                print(f"   📤 GOT TASK! {task.task_id} for {task.channel_name}", flush=True)
                
                logger.info(f"Processing task {task.task_id} for channel {task.channel_name}")
                
                await self._execute_task(task)
                
                self.channel_queues[channel_id].task_done()
                
            except asyncio.CancelledError:
                logger.info(f"Channel worker cancelled for {channel_id}")
                break
            except Exception as e:
                logger.exception(f"Channel worker error for {channel_id}: {e}")
                await asyncio.sleep(5)  # Backoff before retry
    

    def _record_pipeline_failure(self, task, error_type: str, error_message: str):
        """Sprint 66.5: persist failure via ErrorLogger (signature-adaptive)."""
        try:
            if get_error_logger is None:
                return
            import inspect
            svc = get_error_logger()
            names = [m for m in ("log_failure", "record_failure", "log_error",
                                 "record_error", "log", "record", "save") if hasattr(svc, m)]
            if not names:
                names = [m for m in dir(svc)
                         if not m.startswith("_") and callable(getattr(svc, m))]
            values = {
                "channel_id": getattr(task, "channel_id", None),
                "task_id": getattr(task, "task_id", None),
                "pipeline": getattr(task, "pipeline", None) or "unknown",
                "job": getattr(task, "job_type", None) or "unknown",
                "job_name": getattr(task, "job_type", None) or "unknown",
                "job_type": getattr(task, "job_type", None) or "unknown",
                "error_type": error_type,
                "error_message": str(error_message)[:2000],
                "message": str(error_message)[:2000],
                "error": str(error_message)[:2000],
            }
            for name in names:
                fn = getattr(svc, name)
                try:
                    sig = inspect.signature(fn)
                except (TypeError, ValueError):
                    continue
                params = sig.parameters
                kwargs, ok = {}, True
                for pname, param in params.items():
                    if pname == "self":
                        continue
                    if pname in values:
                        kwargs[pname] = values[pname]
                    elif (param.default is param.empty and param.kind not in
                          (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)):
                        ok = False
                        break
                if not ok:
                    continue
                try:
                    fn(**kwargs)
                    logger.info(f"Pipeline failure recorded via ErrorLogger.{name}()")
                    return
                except TypeError:
                    continue
            logger.warning("No compatible ErrorLogger method found for failure recording")
        except Exception as e:
            logger.warning(f"Failed to record pipeline failure: {e}")

    async def _try_universal_pipeline(self, channel, task):
        """Sprint 69.15: Universal Pipeline для pilot каналов (telegram + sources + archetype).
        Возвращает dict результата или None (fallback на старый workflow)."""
        try:
            # Только telegram каналы с реальным ботом
            if getattr(channel, "platform", None) != "telegram":
                return None
            if not (getattr(channel, "bot_token", None) and getattr(channel, "chat_id", None)):
                return None

            cp = getattr(channel, "content_profile", None) or {}
            if not cp.get("sources"):
                return None

            profile = None
            if getattr(channel, "profile_id", None):
                db = SessionLocal()
                try:
                    profile = db.query(ChannelProfileORM).filter(
                        ChannelProfileORM.id == channel.profile_id
                    ).first()
                finally:
                    db.close()

            if not profile or not getattr(profile, "archetype", None):
                return None

            from backend.engines.strategy_registry import get_strategies
            import backend.engines.register_all  # noqa: F401 — регистрация стратегий
            from backend.engines.universal_pipeline import UniversalContentPipeline
            from core.models.archetypes import Archetype

            try:
                strategies = get_strategies(Archetype(profile.archetype))
            except Exception as e:
                logger.warning(f"get_strategies failed: {e}")
                strategies = None
            # Sprint 69.15: даже если get_strategies возвращает None (fallback в UniversalContentPipeline)
            # UniversalContentPipeline сам создаст дефолтные стратегии через get_strategies внутри
            # Поэтому мы не блокируем запуск — просто логируем warning

            # Пробрасываем данные в profile (как в pipeline.py)
            if not getattr(profile, "content_profile", None):
                profile.content_profile = cp
            if not getattr(profile, "bot_token", None):
                profile.bot_token = channel.bot_token
            if not getattr(profile, "chat_id", None):
                profile.chat_id = channel.chat_id
            if not getattr(profile, "channel_id", None):
                profile.channel_id = channel.id

            logger.info(f"Sprint 69.15: Universal Pipeline for {task.channel_name}")
            print(f"   🚀 Universal Pipeline for {task.channel_name}", flush=True)

            pipeline = UniversalContentPipeline(channel=channel, profile=profile)
            pipe_result = await pipeline.run()

            return {
                "status": "ok",
                "topics": pipe_result.topics_found,
                "generated": pipe_result.posts_generated,
                "published": pipe_result.posts_published,
            }
        except Exception as e:
            logger.error(f"Universal Pipeline failed for {task.channel_name}: {e}")
            return None

    async def _execute_task(self, task: ChannelTask):
        """Sprint 66.3: Executes task with timeout protection."""
        logger.info(f"Executing task {task.task_id} with timeout={TASK_TIMEOUT}s")
        try:
            await asyncio.wait_for(
                self._execute_task_internal(task),
                timeout=TASK_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"Task {task.task_id} timed out after {TASK_TIMEOUT}s")
            task.status = TaskStatus.FAILED
            task.error = f"Timeout after {TASK_TIMEOUT}s"
            self._record_pipeline_failure(task, "timeout", task.error)
            task.finished_at = datetime.utcnow()

    async def _execute_task_internal(self, task: ChannelTask):
        """Выполняет задачу для канала."""
        print(f"🔨🔨🔨 EXECUTE_TASK START for {task.task_id} ({task.channel_name})", flush=True)
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        self.active_tasks[task.task_id] = task
        
        try:
            # Загружаем канал из БД
            db = SessionLocal()
            try:
                channel = db.query(ChannelORM).filter(ChannelORM.id == task.channel_id).first()
                if not channel:
                    raise ValueError(f"Channel {task.channel_id} not found")
                
                # Проверяем rate limits
                if not self.rate_limit_policy.can_run(channel):
                    logger.warning(f"Rate limit exceeded for channel {task.channel_name}")
                    task.status = TaskStatus.FAILED
                    task.error = "Rate limit exceeded"
                    return
                
                # Sprint 69.15: pilot каналы идут через Universal Pipeline
                universal_result = await self._try_universal_pipeline(channel, task)

                if universal_result is not None:
                    result = universal_result
                    print(f"   ✅ Universal Pipeline: {result}", flush=True)
                else:
                    # Выполняем workflow (legacy каналы)
                    logger.info(f"Executing workflow for channel {task.channel_name}")
                    print(f"   🚀 Calling runner.run_now() for {task.task_id}", flush=True)
                    # Sprint 8.4: передаём workflow_id из канала в runner
                    workflow_id = getattr(channel, "workflow_id", None)
                    if workflow_id:
                        logger.info(f"Executing workflow {workflow_id} from channel for {task.channel_name}")
                        result = await self.runner.run_now(channel=channel, workflow_id=workflow_id)
                    else:
                        logger.info(f"Channel has no workflow_id, using default pipeline for {task.channel_name}")
                        result = await self.runner.run_now(channel=channel)
                    print(f"   ✅ runner.run_now() returned: {result.get('status', 'unknown')}", flush=True)
                
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                
                logger.info(f"Task {task.task_id} completed successfully")
                
            finally:
                db.close()
                
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            
            self._record_pipeline_failure(task, "exception", str(e))
            logger.error(f"Task {task.task_id} failed: {e}")
            
            # Retry logic
            if self.retry_policy.should_retry(task.retry_count, task.max_retries):
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                backoff_time = self.retry_policy.get_backoff_time(task.retry_count)
                
                logger.info(f"Retrying task {task.task_id} in {backoff_time}s (attempt {task.retry_count})")
                
                await asyncio.sleep(backoff_time)
                await self._enqueue_task(task)
            else:
                logger.error(f"Task {task.task_id} failed after {task.retry_count} retries")
                self.error_handling_policy.handle_error(task)
        
        finally:
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
    
    async def _enqueue_task(self, task: ChannelTask):
        """Добавляет задачу в очередь канала."""
        if task.channel_id in self.channel_queues:
            print(f"📥 ENQUEUING task {task.task_id} into queue {task.channel_id[:8]}", flush=True)
            print(f"   Queue exists: {task.channel_id in self.channel_queues}", flush=True)
            print(f"   Queue size before: {self.channel_queues[task.channel_id].qsize()}", flush=True)
            await self.channel_queues[task.channel_id].put(task)
            logger.info(f"Enqueued task {task.task_id} for channel {task.channel_name}")
        else:
            logger.error(f"Queue not found for channel {task.channel_id}")
    
    async def run_channel_now(self, channel_id: str) -> Dict[str, Any]:
        """Запускает пайплайн для канала немедленно."""
        if channel_id not in self.channels:
            return {"status": "failed", "error": "Channel not found"}
        
        channel = self.channels[channel_id]
        
        # Создаём задачу
        workflow = WorkflowDefinition.default()  # Default workflow
        task = ChannelTask(
            task_id=str(uuid.uuid4()),
            channel_id=channel.id,
            channel_name=channel.name,
            workflow=workflow
        )
        
        # Добавляем в очередь
        await self._enqueue_task(task)
        
        return {
            "status": "queued",
            "task_id": task.task_id,
            "execution_id": task.execution_id,
            "channel_id": channel.id,
            "channel_name": channel.name
        }
    
    async def run_all_channels_now(self) -> Dict[str, Any]:
        """Запускает пайплайн для всех активных каналов."""
        results = {}
        
        for channel_id in self.channels:
            result = await self.run_channel_now(channel_id)
            results[channel_id] = result
        
        return {
            "status": "queued",
            "total_channels": len(results),
            "results": results
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Возвращает статус AutomationManager."""
        return {
            "running": True,
            "total_channels": len(self.channels),
            "active_tasks": len(self.active_tasks),
            "queues": {
                channel_id: queue.qsize()
                for channel_id, queue in self.channel_queues.items()
            },
            "channels": {
                channel_id: {
                    "name": channel.name,
                    "is_active": channel.is_active
                }
                for channel_id, channel in self.channels.items()
            }
        }


# Global instance
automation_manager_v2 = AutomationManagerV2()