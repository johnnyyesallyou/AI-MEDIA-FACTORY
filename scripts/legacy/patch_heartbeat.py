import pathlib

p = pathlib.Path("/app/backend/app/api/v1/metrics.py")
c = p.read_text(encoding="utf-8")

if "heartbeat" not in c:
    c += '''

@router.post("/metrics/heartbeat")
def metrics_heartbeat(job_name: str = "manual_job", status: str = "success"):
    """Записывает метрики ВНУТРИ серверного процесса (demo/debug)."""
    import random
    PrometheusMetrics.record_job(job_name, status, random.uniform(0.2, 2.0))
    PrometheusMetrics.record_post_published("telegram", "demo_channel")
    PrometheusMetrics.set_channels_active(3)
    PrometheusMetrics.set_posts_in_queue(5)
    return {"ok": True, "job": job_name, "status": status}
'''
    p.write_text(c, encoding="utf-8")
    print("✅ heartbeat endpoint added")
else:
    print("ℹ️ already exists")