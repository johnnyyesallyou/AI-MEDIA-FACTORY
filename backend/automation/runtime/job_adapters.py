"""Job Adapters - Sprint 48.

Адаптеры для legacy jobs (automation_jobs.py) к v2 contract (BaseJob.execute).
"""
import logging
import inspect
from typing import Any, Dict
from backend.automation.runtime.contracts import BaseJob, ExecutionContext, NodeResult
from backend.automation.jobs.automation_jobs import (
    ResearchJob as LegacyResearchJob,
    DecisionJob as LegacyDecisionJob,
    WritingJob as LegacyWritingJob,
    EvaluatorJob as LegacyEvaluatorJob,
    ImageJob as LegacyImageJob,
    PublishJob as LegacyPublishJob,
)

logger = logging.getLogger(__name__)


async def _maybe_await(result):
    """Sprint 49: async legacy jobs должны await-иться."""
    if inspect.iscoroutine(result) or inspect.isawaitable(result):
        return await result
    return result


class ResearchJobAdapter(BaseJob):
    node_type = "research"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = LegacyResearchJob()
            result = await _maybe_await(job.run(context.channel, execution_id=context.execution_id))
            return result if isinstance(result, NodeResult) else NodeResult.success(result if isinstance(result, dict) else {"result": result})
        except Exception as e:
            logger.error(f"ResearchJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class DecisionJobAdapter(BaseJob):
    node_type = "decision"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = LegacyDecisionJob()
            result = await _maybe_await(job.run(context.channel, execution_id=context.execution_id))
            return result if isinstance(result, NodeResult) else NodeResult.success(result if isinstance(result, dict) else {"result": result})
        except Exception as e:
            logger.error(f"DecisionJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class WritingJobAdapter(BaseJob):
    node_type = "writing"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = LegacyWritingJob()
            result = await _maybe_await(job.run(context.channel, execution_id=context.execution_id))
            return result if isinstance(result, NodeResult) else NodeResult.success(result if isinstance(result, dict) else {"result": result})
        except Exception as e:
            logger.error(f"WritingJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class EvaluatorJobAdapter(BaseJob):
    node_type = "evaluation"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = LegacyEvaluatorJob()
            result = await _maybe_await(job.run(context.channel, execution_id=context.execution_id))
            return result if isinstance(result, NodeResult) else NodeResult.success(result if isinstance(result, dict) else {"result": result})
        except Exception as e:
            logger.error(f"EvaluatorJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class ImageJobAdapter(BaseJob):
    node_type = "image"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = LegacyImageJob()
            result = await _maybe_await(job.run(context.channel, execution_id=context.execution_id))
            return result if isinstance(result, NodeResult) else NodeResult.success(result if isinstance(result, dict) else {"result": result})
        except Exception as e:
            logger.error(f"ImageJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class PublishJobAdapter(BaseJob):
    node_type = "publish"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = LegacyPublishJob()
            result = await _maybe_await(job.run(context.channel, execution_id=context.execution_id))
            return result if isinstance(result, NodeResult) else NodeResult.success(result if isinstance(result, dict) else {"result": result})
        except Exception as e:
            logger.error(f"PublishJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))