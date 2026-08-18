"""
Workflow Runtime — универсальный исполнитель графов (Sprint 8.4.1).

Архитектура (как Temporal / Airflow / Prefect / n8n):
    Workflow Designer  -> Workflow Definition (БД, граф nodes+edges)
    Workflow Runtime   -> исполняет граф, НЕ ЗНАЕТ про конкретные движки
    Job Factory        -> node_type -> Job class
    Jobs               -> реализуют BaseJob: execute(context) -> NodeResult

Runtime знает только одно: Job.execute(context).
Добавить новый движок = новый Job класс + регистрация в фабрике.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

from .contracts import NodeResult, NodeStatus, ExecutionContext, BaseJob
from .job_factory import JobFactory
from core.database import SessionLocal
from core.models.workflow_orm import WorkflowORM

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Результат выполнения всего workflow."""
    execution_id: str
    workflow_id: str
    workflow_name: str
    status: str  # "completed" | "failed" | "partial"
    node_results: Dict[str, NodeResult] = field(default_factory=dict)
    error: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "status": self.status,
            "nodes": {
                nid: {"status": r.status.value, "output": r.output, "error": r.error}
                for nid, r in self.node_results.items()
            },
            "error": self.error,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }


class WorkflowRuntime:
    """
    Универсальный исполнитель графов.
    Не знает про конкретные jobs — использует JobFactory и BaseJob.execute().
    """

    def __init__(self):
        self._log_writer = None  # можно подменить для тестов

    async def execute(
        self,
        workflow_id: str,
        channel: Any,
        execution_id: str,
    ) -> ExecutionResult:
        """
        Главная точка входа. Читает граф из БД, исполняет по уровням.
        """
        logger.info("WorkflowRuntime.execute: workflow=%s execution=%s", workflow_id, execution_id)

        # 1. Загрузить workflow из БД
        workflow_orm = self._load_workflow(workflow_id)
        if not workflow_orm:
            return ExecutionResult(
                execution_id=execution_id,
                workflow_id=workflow_id,
                workflow_name="",
                status="failed",
                error=f"Workflow {workflow_id} not found",
            )

        definition = workflow_orm.definition or {}
        nodes = definition.get("nodes", [])
        edges = definition.get("edges", [])

        if not nodes:
            return ExecutionResult(
                execution_id=execution_id,
                workflow_id=workflow_id,
                workflow_name=workflow_orm.name,
                status="failed",
                error="Workflow has no nodes",
            )

        # 2. Построить уровни (топологическая сортировка по слоям)
        try:
            levels = self._build_levels(nodes, edges)
        except ValueError as e:
            return ExecutionResult(
                execution_id=execution_id,
                workflow_id=workflow_id,
                workflow_name=workflow_orm.name,
                status="failed",
                error=str(e),
            )

        logger.info("Workflow '%s' has %d levels: %s",
                    workflow_orm.name, len(levels),
                    [[n["id"] for n in lvl] for lvl in levels])

        # 3. Исполнить по уровням (внутри уровня — параллельно)
        result = ExecutionResult(
            execution_id=execution_id,
            workflow_id=workflow_id,
            workflow_name=workflow_orm.name,
            status="completed",
        )

        # Контекст: outputs накапливаются между уровнями
        previous_outputs: Dict[str, Dict[str, Any]] = {}

        for level_idx, level_nodes in enumerate(levels):
            logger.info("  Level %d: executing %d nodes in parallel: %s",
                       level_idx, len(level_nodes),
                       [n["id"] for n in level_nodes])

            tasks = [
                self._execute_node(node, channel, execution_id, previous_outputs)
                for node in level_nodes
            ]
            level_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Обработать результаты уровня
            level_failed = False
            for node, res in zip(level_nodes, level_results):
                node_id = node["id"]
                if isinstance(res, Exception):
                    logger.error("Node %s raised exception: %s", node_id, res)
                    result.node_results[node_id] = NodeResult.failed(str(res))
                    level_failed = True
                elif isinstance(res, NodeResult):
                    result.node_results[node_id] = res
                    if res.ok:
                        # Успех — сохраняем output для следующих уровней
                        previous_outputs[node_id] = res.output
                        logger.info("    ✅ %s -> %s (output keys: %s)",
                                   node_id, res.status.value, list(res.output.keys())[:5])
                    else:
                        level_failed = True
                        logger.error("    ❌ %s -> %s: %s",
                                    node_id, res.status.value, res.error)
                else:
                    logger.warning("    ⚠️  %s returned unexpected: %s", node_id, res)
                    result.node_results[node_id] = NodeResult.failed(f"Unexpected result type: {type(res)}")
                    level_failed = True

            if level_failed:
                result.status = "failed"
                result.error = f"Level {level_idx} had failed nodes"
                logger.warning("Stopping execution: level %d had failures", level_idx)
                break

        result.finished_at = datetime.utcnow()
        logger.info("WorkflowRuntime finished: status=%s, %d nodes executed",
                   result.status, len(result.node_results))
        return result

    def _load_workflow(self, workflow_id: str) -> Optional[WorkflowORM]:
        db = SessionLocal()
        try:
            return db.query(WorkflowORM).filter(WorkflowORM.id == workflow_id).first()
        finally:
            db.close()

    def _build_levels(self, nodes: List[Dict], edges: List[Dict]) -> List[List[Dict]]:
        """
        Топологическая сортировка по слоям.
        Каждый слой — это ноды, которые можно исполнять параллельно.

        Пример:
          A → B → C
          A → D → C
        Уровни: [[A], [B, D], [C]]
        """
        nodes_by_id = {n["id"]: n for n in nodes}
        in_degree = {n["id"]: 0 for n in nodes}
        adjacency: Dict[str, List[str]] = {n["id"]: [] for n in nodes}

        for edge in edges:
            src, tgt = edge["source_node_id"], edge["target_node_id"]
            if src not in nodes_by_id or tgt not in nodes_by_id:
                raise ValueError(f"Edge references unknown node: {src} -> {tgt}")
            adjacency[src].append(tgt)
            in_degree[tgt] += 1

        # BFS по слоям
        queue = [nid for nid, d in in_degree.items() if d == 0]
        levels: List[List[Dict]] = []
        visited_count = 0

        while queue:
            # Текущий слой — все ноды в queue
            current_level = [nodes_by_id[nid] for nid in queue]
            levels.append(current_level)
            visited_count += len(queue)

            next_queue = []
            for nid in queue:
                for neighbor in adjacency[nid]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_queue.append(neighbor)
            queue = next_queue

        if visited_count != len(nodes):
            raise ValueError(f"Graph has a cycle (visited {visited_count} of {len(nodes)} nodes)")

        return levels

    async def _execute_node(
        self,
        node: Dict[str, Any],
        channel: Any,
        execution_id: str,
        previous_outputs: Dict[str, Dict[str, Any]],
    ) -> NodeResult:
        """Выполняет одну ноду через JobFactory."""
        node_id = node["id"]
        node_type = node.get("type", "unknown")
        node_config = node.get("config") or {}

        # Записать в execution_logs: started
        self._log_execution(execution_id, node_id, "started")

        # Создать job через фабрику
        job = JobFactory.create(node_type)
        if job is None:
            error = f"Unknown node_type: {node_type}"
            logger.error(error)
            self._log_execution(execution_id, node_id, "failed", error)
            return NodeResult.failed(error)

        # Построить контекст
        context = ExecutionContext(
            channel=channel,
            execution_id=execution_id,
            node_id=node_id,
            node_type=node_type,
            node_config=node_config,
            previous_outputs=dict(previous_outputs),  # копия на момент старта
        )

        # Выполнить
        try:
            result = await job.execute(context)
            self._log_execution(execution_id, node_id, result.status.value)
            return result
        except Exception as e:
            logger.exception("Node %s raised exception: %s", node_id, e)
            error_msg = f"{type(e).__name__}: {e}"
            self._log_execution(execution_id, node_id, "failed", error_msg)
            return NodeResult.failed(error_msg)

    def _log_execution(self, execution_id: str, stage: str, status: str, error: str = None):
        """Запись в execution_logs (одна запись на старт/конец ноды)."""
        try:
            from core.models.execution_log_orm import ExecutionLogORM
            db = SessionLocal()
            try:
                log_entry = ExecutionLogORM(
                    execution_id=execution_id,
                    stage=stage,
                    status=status,
                )
                db.add(log_entry)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.warning("Failed to write execution log: %s", e)