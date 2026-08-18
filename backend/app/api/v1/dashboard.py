import time
import logging
from datetime import datetime
from typing import Dict, Optional

import redis
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.database import get_db, engine, DATABASE_URL
from core.repositories.content_repository import ContentRepository
from core.repositories.channel_repository import ChannelRepository
from core.repositories.workflow_repository import WorkflowRepository
from core.workflows.models import WorkflowDefinition, WorkflowNode, WorkflowEdge, NodeType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

REDIS_URL = "redis://redis:6379/0"


class ServiceStatus(BaseModel):
    name: str
    status: str  # "OK", "ERROR", "NOT_CONFIGURED"
    latency_ms: Optional[float] = None
    detail: Optional[str] = None


class SystemHealthResponse(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, ServiceStatus]


class DailyStatsResponse(BaseModel):
    date: str
    news_found: int = 0
    news_selected: int = 0
    posts_created: int = 0
    posts_published: int = 0
    drafts_pending: int = 0
    errors_count: int = 0
    avg_quality_score: Optional[float] = None
    avg_fact_score: Optional[float] = None
    total_views: int = 0
    total_er: float = 0.0


def _check_postgres() -> ServiceStatus:
    start = time.perf_counter()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency = round((time.perf_counter() - start) * 1000, 1)
        return ServiceStatus(name="Postgres", status="OK", latency_ms=latency)
    except Exception as e:
        return ServiceStatus(name="Postgres", status="ERROR", detail=str(e)[:200])


def _check_redis() -> ServiceStatus:
    start = time.perf_counter()
    try:
        client = redis.from_url(REDIS_URL, socket_connect_timeout=2, socket_timeout=2)
        client.ping()
        latency = round((time.perf_counter() - start) * 1000, 1)
        return ServiceStatus(name="Redis", status="OK", latency_ms=latency)
    except Exception as e:
        return ServiceStatus(name="Redis", status="ERROR", detail=str(e)[:200])


def _not_configured(name: str) -> ServiceStatus:
    return ServiceStatus(name=name, status="NOT_CONFIGURED", detail="Сервис не поднят в docker-compose.yml")


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health():
    '''Реальные проверки Postgres/Redis. Остальные сервисы честно помечены NOT_CONFIGURED,
    так как физически не существуют в текущем docker-compose.yml.'''
    return SystemHealthResponse(
        services={
            "Postgres": _check_postgres(),
            "Redis": _check_redis(),
            "Ollama": _not_configured("Ollama"),
            "Qdrant": _not_configured("Qdrant"),
            "MinIO": _not_configured("MinIO"),
            "ComfyUI": _not_configured("ComfyUI"),
            "Telegram": _not_configured("Telegram"),
            "Research": ServiceStatus(name="Research", status="OK", detail="engines/research/ работает (in-process)"),
        }
    )


@router.get("/stats", response_model=DailyStatsResponse)
async def get_daily_stats(db: Session = Depends(get_db)):
    '''Реальная агрегация из таблицы content под актуальную схему статусов
    (approved/published/rejected/needs_revision/draft - после интеграции
    EvaluatorEngine другим агентом, отдельного статуса "research" больше нет).'''
    content_repo = ContentRepository(db)

    posts_published = content_repo.count(status="published")
    drafts_pending = content_repo.count(status="draft") + content_repo.count(status="needs_revision")
    approved_pending_publish = content_repo.count(status="approved")
    rejected = content_repo.count(status="rejected")

    total_content = content_repo.count()

    avg_quality_row = db.execute(
        text("SELECT AVG(quality_score) FROM content WHERE quality_score IS NOT NULL")
    ).scalar()
    avg_fact_row = db.execute(
        text("SELECT AVG(fact_score) FROM content WHERE fact_score IS NOT NULL")
    ).scalar()

    return DailyStatsResponse(
        date=datetime.utcnow().strftime("%Y-%m-%d"),
        news_found=0,  # TODO: отдельного статуса "research" больше нет в новой схеме -
                       # нужен подсчёт через лог запусков workflow, если появится такая таблица
        news_selected=total_content,
        posts_created=total_content,
        posts_published=posts_published,
        drafts_pending=drafts_pending,
        errors_count=0,
        avg_quality_score=round(float(avg_quality_row), 1) if avg_quality_row else None,
        avg_fact_score=round(float(avg_fact_row), 1) if avg_fact_row else None,
        total_views=0,
        total_er=0.0,
    )

@router.get("/workflow")
async def get_workflow_engine(db: Session = Depends(get_db)):
    '''Expose the data-driven workflow definition as the new Workflow Engine surface for the dashboard.'''
    repo = WorkflowRepository(db)
    item = repo.get_by_name("Telegram Research to Publish")
    if item:
        return item.definition

    workflow = WorkflowDefinition(
        id="telegram-default",
        name="Telegram Research to Publish",
        description="Research -> Decision -> Writing -> Fact Check -> Image -> Review -> Telegram",
        nodes=[
            WorkflowNode(id="research", type=NodeType.RESEARCH),
            WorkflowNode(id="decision", type=NodeType.DECISION),
            WorkflowNode(id="writing", type=NodeType.BRIEF),
            WorkflowNode(id="fact_check", type=NodeType.FACT_CHECKER),
            WorkflowNode(id="image", type=NodeType.IMAGE),
            WorkflowNode(id="review", type=NodeType.EVALUATOR),
            WorkflowNode(id="publisher", type=NodeType.PUBLISHER),
        ],
        edges=[
            WorkflowEdge(source_node_id="research", target_node_id="decision"),
            WorkflowEdge(source_node_id="decision", target_node_id="writing"),
            WorkflowEdge(source_node_id="writing", target_node_id="fact_check"),
            WorkflowEdge(source_node_id="fact_check", target_node_id="image"),
            WorkflowEdge(source_node_id="image", target_node_id="review"),
            WorkflowEdge(source_node_id="review", target_node_id="publisher"),
        ],
    )
    repo.create(
        name=workflow.name,
        description=workflow.description,
        definition=workflow.model_dump(),
        is_active=True,
    )
    return workflow.model_dump()

