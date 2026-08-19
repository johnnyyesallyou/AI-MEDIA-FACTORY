"""System Metrics API - Sprint 43.

Проксирует инфраструктурные метрики из Prometheus + health в Dashboard.
GET /api/metrics/system
"""
import logging

import requests
from fastapi import APIRouter

from core.health_unified import UnifiedHealthService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])

health_service = UnifiedHealthService()


def _prom_query(expr: str):
    """Выполняет instant query к Prometheus (с fallback на localhost)."""
    for base in ("http://prometheus:9090", "http://localhost:9090"):
        try:
            r = requests.get(f"{base}/api/v1/query", params={"query": expr}, timeout=5)
            if r.status_code == 200:
                return r.json().get("data", {}).get("result", [])
        except Exception:
            continue
    return []


def _scalar(result, default=0.0):
    if result:
        try:
            return float(result[0]["value"][1])
        except (KeyError, IndexError, ValueError, TypeError):
            pass
    return default


@router.get("/system")
def get_system_metrics():
    """Системные метрики для Dashboard (секция SYSTEM)."""
    jobs_rate = _prom_query("sum(rate(amf_jobs_total[5m]))")
    jobs_by_status = _prom_query("sum(rate(amf_jobs_total[5m])) by (status)")
    posts_rate = _prom_query("sum(rate(amf_posts_published_total[5m]))")
    p95 = _prom_query(
        "histogram_quantile(0.95, sum(rate(amf_job_duration_seconds_bucket[5m])) by (le))"
    )
    errors_rate = _prom_query("sum(rate(amf_errors_total[5m]))")
    queue = _prom_query("amf_posts_in_queue")
    channels_active = _prom_query("amf_channels_active")

    health = health_service.get_overall_status()

    return {
        "system": {
            "jobs_per_sec": round(_scalar(jobs_rate), 4),
            "jobs_by_status": {
                r["metric"].get("status", "?"): round(float(r["value"][1]), 4)
                for r in jobs_by_status
            },
            "posts_per_sec": round(_scalar(posts_rate), 4),
            "job_duration_p95_sec": round(_scalar(p95), 3),
            "error_rate_per_sec": round(_scalar(errors_rate), 4),
            "posts_in_queue": int(_scalar(queue)),
            "channels_active": int(_scalar(channels_active)),
        },
        "health": {
            "status": health["status"],
            "components": {
                name: comp["status"] for name, comp in health["components"].items()
            },
        },
    }