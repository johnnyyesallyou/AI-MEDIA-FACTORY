"""Job Adapters - Sprint 48.

Адаптеры для legacy jobs (automation_jobs.py) к v2 contract (BaseJob.execute).
"""
import logging
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


class ResearchJobAdapter(BaseJob):
    """Адаптер для legacy ResearchJob."""
    node_type = "research"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = LegacyResearchJob()
            # Legacy jobs могут иметь разные сигнатуры:
            # - run(channel, context)
            # - __call__(channel)
            # - execute(channel)
            
            if hasattr(job, 'run'):
                result = job.run(context.channel, context)
            elif hasattr(job, 'execute'):
                result = job.execute(context.channel)
            elif callable(job):
                result = job(context.channel)
            else:
                raise AttributeError(f"LegacyResearchJob has no callable method")
            
            # Конвертируем результат в NodeResult
            if isinstance(result, NodeResult):
                return result
            elif isinstance(result, dict):
                return NodeResult.success(result)
            else:
                return NodeResult.success({"result": result})
                
        except Exception as e:
            logger.error(f"ResearchJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class DecisionJobAdapter(BaseJob):
    node_type = "decision"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = LegacyDecisionJob()
            if hasattr(job, 'run'):
                result = job.run(context.channel, context)
            elif callable(job):
                result = job(context.channel)
            else:
                raise AttributeError("LegacyDecisionJob has no callable method")
            
            return NodeResult.success(result) if isinstance(result, dict) else NodeResult.success({"result": result})
        except Exception as e:
            logger.error(f"DecisionJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class WritingJobAdapter(BaseJob):
    node_type = "writing"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = LegacyWritingJob()
            if hasattr(job, 'run'):
                result = job.run(context.channel, context)
            elif callable(job):
                result = job(context.channel)
            else:
                raise AttributeError("LegacyWritingJob has no callable method")
            
            return NodeResult.success(result) if isinstance(result, dict) else NodeResult.success({"result": result})
        except Exception as e:
            logger.error(f"WritingJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class EvaluatorJobAdapter(BaseJob):
    node_type = "evaluation"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = LegacyEvaluatorJob()
            if hasattr(job, 'run'):
                result = job.run(context.channel, context)
            elif callable(job):
                result = job(context.channel)
            else:
                raise AttributeError("LegacyEvaluatorJob has no callable method")
            
            return NodeResult.success(result) if isinstance(result, dict) else NodeResult.success({"result": result})
        except Exception as e:
            logger.error(f"EvaluatorJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class ImageJobAdapter(BaseJob):
    node_type = "image"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = LegacyImageJob()
            if hasattr(job, 'run'):
                result = job.run(context.channel, context)
            elif callable(job):
                result = job(context.channel)
            else:
                raise AttributeError("LegacyImageJob has no callable method")
            
            return NodeResult.success(result) if isinstance(result, dict) else NodeResult.success({"result": result})
        except Exception as e:
            logger.error(f"ImageJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))


class PublishJobAdapter(BaseJob):
    node_type = "publish"
    
    async def execute(self, context: ExecutionContext) -> NodeResult:
        try:
            job = LegacyPublishJob()
            if hasattr(job, 'run'):
                result = job.run(context.channel, context)
            elif callable(job):
                result = job(context.channel)
            else:
                raise AttributeError("LegacyPublishJob has no callable method")
            
            return NodeResult.success(result) if isinstance(result, dict) else NodeResult.success({"result": result})
        except Exception as e:
            logger.error(f"PublishJobAdapter failed: {e}", exc_info=True)
            return NodeResult.failed(str(e))