"""Workflow Runtime — универсальный исполнитель графов (Sprint 8.4.1)."""
from .contracts import BaseJob, NodeResult, NodeStatus, ExecutionContext
from .job_factory import JobFactory
from .workflow_runtime import WorkflowRuntime, ExecutionResult

# Авто-регистрация всех jobs при первом импорте пакета
from . import register_jobs  # noqa: F401