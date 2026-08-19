"""Prometheus Metrics Endpoint - Sprint 40.

Exposes /metrics в Prometheus text format.
Метрики:
  - amf_jobs_total (counter)
  - amf_jobs_errors_total (counter)
  - amf_posts_published_total (counter)
  - amf_job_duration_seconds (histogram)
  - amf_channels_active (gauge)
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response
import time

router = APIRouter()

# Counters
JOBS_TOTAL = Counter(
    'amf_jobs_total',
    'Total jobs executed',
    ['job_name', 'status']
)

POSTS_PUBLISHED = Counter(
    'amf_posts_published_total',
    'Total posts published',
    ['platform', 'channel']
)

ERRORS_TOTAL = Counter(
    'amf_errors_total',
    'Total errors',
    ['component', 'error_type']
)

# Histograms
JOB_DURATION = Histogram(
    'amf_job_duration_seconds',
    'Job execution duration',
    ['job_name'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

# Gauges
CHANNELS_ACTIVE = Gauge(
    'amf_channels_active',
    'Number of active channels'
)

POSTS_IN_QUEUE = Gauge(
    'amf_posts_in_queue',
    'Number of posts waiting for publication'
)


class PrometheusMetrics:
    """Centralized metrics collection."""
    
    @staticmethod
    def record_job(job_name: str, status: str, duration: float):
        JOBS_TOTAL.labels(job_name=job_name, status=status).inc()
        JOB_DURATION.labels(job_name=job_name).observe(duration)
    
    @staticmethod
    def record_post_published(platform: str, channel: str):
        POSTS_PUBLISHED.labels(platform=platform, channel=channel).inc()
    
    @staticmethod
    def record_error(component: str, error_type: str):
        ERRORS_TOTAL.labels(component=component, error_type=error_type).inc()
    
    @staticmethod
    def set_channels_active(count: int):
        CHANNELS_ACTIVE.set(count)
    
    @staticmethod
    def set_posts_in_queue(count: int):
        POSTS_IN_QUEUE.set(count)


@router.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@router.post("/metrics/heartbeat")
def metrics_heartbeat(job_name: str = "manual_job", status: str = "success"):
    """Записывает метрики ВНУТРИ серверного процесса (demo/debug)."""
    import random
    PrometheusMetrics.record_job(job_name, status, random.uniform(0.2, 2.0))
    PrometheusMetrics.record_post_published("telegram", "demo_channel")
    PrometheusMetrics.set_channels_active(3)
    PrometheusMetrics.set_posts_in_queue(5)
    return {"ok": True, "job": job_name, "status": status}
