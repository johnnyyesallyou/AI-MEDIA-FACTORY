"""
Sprint 8.4.1 — Workflow Runtime: единый контракт для всех движков.

Архитектура (как Temporal / Airflow / Prefect / n8n):

    Workflow Designer  -> Workflow Definition (БД, граф nodes+edges)
    Workflow Runtime   -> исполняет граф, НЕ ЗНАЕТ про конкретные движки
    Job Factory        -> node_type -> Job class
    Jobs               -> реализуют BaseJob: execute(context) -> NodeResult

Runtime знает только одно: Job.execute(context).
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class NodeStatus(str, Enum):
    """State machine ноды: pending -> running -> success/failed/skipped."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class NodeResult:
    """Результат выполнения одной ноды."""
    status: NodeStatus
    output: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.status in (NodeStatus.SUCCESS, NodeStatus.SKIPPED)

    @classmethod
    def success(cls, output: Dict[str, Any] = None, metrics: Dict[str, Any] = None) -> "NodeResult":
        return cls(status=NodeStatus.SUCCESS, output=output or {}, metrics=metrics or {})

    @classmethod
    def failed(cls, error: str, metrics: Dict[str, Any] = None) -> "NodeResult":
        return cls(status=NodeStatus.FAILED, error=error, metrics=metrics or {})

    @classmethod
    def skipped(cls, reason: str = "") -> "NodeResult":
        return cls(status=NodeStatus.SKIPPED, error=reason or None)


@dataclass
class ExecutionContext:
    """
    Контекст, передаваемый в каждый Job.

    Несёт всё, что нужно движку:
    - channel (источники, стиль, credentials)
    - node_config (параметры из Designer: model, temperature, max_topics...)
    - previous_outputs (данные от предыдущих нод графа)
    """
    channel: Any
    execution_id: str
    node_id: str
    node_type: str
    node_config: Dict[str, Any] = field(default_factory=dict)
    previous_outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def output_of(self, node_id: str) -> Dict[str, Any]:
        """Output конкретной предыдущей ноды (или {})."""
        return self.previous_outputs.get(node_id, {})

    def first_output(self, node_types_prefix: str = "") -> Dict[str, Any]:
        """Первый доступный output (fallback для простых случаев)."""
        for node_id, out in self.previous_outputs.items():
            if not node_types_prefix or node_id.startswith(node_types_prefix):
                return out
        return {}


class BaseJob(ABC):
    """
    Единый контракт ВСЕХ движков платформы.

    ResearchJob, WritingJob, PublishJob, FactCheckJob, ImageJob...
    все наследуются от BaseJob и реализуют execute(context).

    Runtime НЕ знает про конкретные движки — он вызывает execute().
    """

    #: тип ноды, который реализует job (research, writing, publish...)
    node_type: str = "base"

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> NodeResult:
        """Выполняет работу ноды. Возвращает NodeResult с output для следующих нод."""
        ...

    # ------------------------------------------------------------------
    # Обратная совместимость (Sprint <= 8.3): legacy-вызовы run(channel, execution_id)
    # ------------------------------------------------------------------
    async def run(self, channel=None, execution_id: str = "", **kwargs) -> dict:
        """
        Legacy-адаптер: старая сигнатура -> новый контракт.
        Позволяет не ломать retry_stage(), debug-run и старые вызовы.
        """
        context = ExecutionContext(
            channel=channel,
            execution_id=execution_id,
            node_id=kwargs.get("node_id") or self.node_type,
            node_type=self.node_type,
            node_config=kwargs.get("node_config") or {},
            previous_outputs=kwargs.get("previous_outputs") or {},
        )
        result = await self.execute(context)
        return {
            "status": result.status.value,
            "output": result.output,
            "metrics": result.metrics,
            "error": result.error,
        }