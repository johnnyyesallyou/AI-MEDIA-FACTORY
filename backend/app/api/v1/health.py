"""Health Endpoints - Sprint 41.

Unified health API для Dashboard и внешних мониторингов.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from core.health_unified import UnifiedHealthService


router = APIRouter(prefix="/api/health", tags=["health"])

health_service = UnifiedHealthService()


@router.get("")
def get_health_full():
    """Полный статус всех компонентов."""
    return health_service.get_overall_status()


@router.get("/database")
def get_health_database():
    """Статус базы данных."""
    return health_service.check_database()


@router.get("/sources")
def get_health_sources():
    """Статус источников контента."""
    return health_service.check_sources()


@router.get("/publishers")
def get_health_publishers():
    """Статус publishers (Telegram, VK)."""
    return health_service.check_publishers()


@router.get("/automation")
def get_health_automation():
    """Статус automation (scheduler, channels)."""
    return health_service.check_automation()


@router.get("/metrics")
def get_health_metrics():
    """Статус metrics endpoint."""
    return health_service.check_metrics()


@router.get("/summary")
def get_health_summary():
    """Краткое summary для Dashboard (одной строкой)."""
    status = health_service.get_overall_status()
    return {
        "status": status["status"],
        "components_ok": status["summary"]["ok"],
        "components_degraded": status["summary"]["degraded"],
        "components_error": status["summary"]["error"],
    }