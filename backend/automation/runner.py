import asyncio
import logging
from datetime import datetime

from .jobs import (
    ResearchJob,
    DecisionJob,
    WritingJob,
    EvaluatorJob,
    PublishJob,
    RevisionJob,
    ReEvaluationJob,
    MonitoringJob,
)
from .workflow_engine_v2 import WorkflowEngineV2
from .runtime import WorkflowRuntime
from core.database import SessionLocal
from core.models.workflow_orm import WorkflowORM


logger = logging.getLogger(__name__)


class AutomationRunner:

    def __init__(self):

        logger.info(
            "AutomationRunner initialized"
        )

        self.stage_map = {
            "research": ResearchJob,
            "decision": DecisionJob,
            "writing": WritingJob,
            "evaluation": EvaluatorJob,
            "revision": RevisionJob,
            "re_evaluation": ReEvaluationJob,
            "publish": PublishJob,
        }
        
        # Маппинг node_type (из workflow definition) на Job classes
        # Поддерживает разные названия: "writing" или "brief", "evaluator" или "evaluation"
        self.node_type_to_job = {
            "research": ResearchJob,
            "decision": DecisionJob,
            "writing": WritingJob,
            "brief": WritingJob,  # alias для writing
            "evaluation": EvaluatorJob,
            "evaluator": EvaluatorJob,  # alias для evaluation
            "publish": PublishJob,
            "publisher": PublishJob,  # alias для publish
            # Future: "fact_checker": FactCheckJob, "image": ImageJob, etc.
        }



    async def retry_stage(self, channel, stage_name: str, execution_id: str) -> dict:
        """Повторяет один конкретный этап пайплайна для канала."""
        if stage_name not in self.stage_map:
            return {"status": "failed", "error": f"Unknown stage: {stage_name}"}

        job_class = self.stage_map[stage_name]
        job = job_class()

        logger.info(
            "Retrying stage=%s channel=%s execution_id=%s",
            stage_name,
            getattr(channel, "name", None),
            execution_id
        )

        try:
            import inspect
            if inspect.iscoroutinefunction(job.run):
                job_result = await job.run(channel=channel, execution_id=execution_id)
            else:
                job_result = await asyncio.to_thread(job.run, channel=channel, execution_id=execution_id)
            return job_result
        except Exception as e:
            logger.exception("Retry failed %s", stage_name)
            return {"status": "failed", "error": str(e)}

    async def run_now(self, channel=None, workflow_id: str = None) -> dict:
        """
        Sprint 8.4.1: Запускает pipeline для канала.
        Если workflow_id указан — делегирует WorkflowRuntime (универсальный исполнитель графов).
        Если не указан — fallback на hardcoded список (обратная совместимость).
        """
        execution_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        if channel:
            execution_id = f"{execution_id}-{channel.id}"

        logger.info("Automation started execution_id=%s channel=%s",
                    execution_id, getattr(channel, "name", None))

        result = {
            "execution_id": execution_id,
            "channel": {
                "id": getattr(channel, "id", None),
                "name": getattr(channel, "name", None),
                "platform": getattr(channel, "platform", None)
            } if channel else None
        }

        # Sprint 8.4.1: если есть workflow_id — делегируем WorkflowRuntime
        if workflow_id:
            logger.info("Using WorkflowRuntime for workflow %s", workflow_id)
            runtime = WorkflowRuntime()
            runtime_result = await runtime.execute(
                workflow_id=workflow_id,
                channel=channel,
                execution_id=execution_id
            )

            result["workflow_id"] = workflow_id
            result["workflow_name"] = runtime_result.workflow_name
            result["status"] = runtime_result.status
            if runtime_result.error:
                result["error"] = runtime_result.error

            for node_id, node_result in runtime_result.node_results.items():
                result[node_id] = {
                    "status": node_result.status.value,
                    "output": node_result.output,
                    "error": node_result.error,
                    "metrics": node_result.metrics
                }
            return result

        # Fallback: старый hardcoded список (для каналов без workflow_id)
        logger.info("No workflow_id provided, using hardcoded job list")
        jobs = [
            ("research", ResearchJob()),
            ("decision", DecisionJob()),
            ("writing", WritingJob()),
            ("evaluation", EvaluatorJob()),
            ("revision", RevisionJob()),
            ("re_evaluation", ReEvaluationJob()),
            ("publish", PublishJob()),
        ]

        for name, job in jobs:
            logger.info("Starting job=%s channel=%s", name, getattr(channel, "name", None))
            try:
                import inspect
                if inspect.iscoroutinefunction(job.run):
                    job_result = await job.run(channel=channel, execution_id=execution_id)
                else:
                    job_result = await asyncio.to_thread(job.run, channel=channel, execution_id=execution_id)
                result[name] = job_result
                logger.info("Job %s completed: %s", name, job_result.get("status", "unknown"))
            except Exception as e:
                logger.exception("Job %s failed", name)
                result[name] = {"status": "failed", "error": str(e)}
                result["status"] = "failed"
                break

        return result

