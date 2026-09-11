"""Sprint 73.4: Tests for Pipeline Dashboard API (health/alerts/trends)."""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base, get_db
from core.models.pipeline_run_metrics_orm import PipelineRunMetrics
from backend.app.api.v1.pipeline_metrics import router


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # единое соединение: create_all и сессии видят одну БД
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine, tables=[PipelineRunMetrics.__table__])

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), TestingSession


def _seed(session, ch_id="ch1", name="Канал 1", **kw):
    defaults = dict(
        channel_id=ch_id,
        channel_name=name,
        execution_id=f"20260909-120000-{ch_id[:8]}",
        research_ms=100,
        writing_ms=9000,
        media_ms=100,
        publishing_ms=200,
        total_ms=10000,
        topics_found=10,
        topics_generated=10,
        topics_published=8,
        errors_count=0,
        success="true",
        llm_calls=10,
        llm_errors=0,
        llm_latency_ms=800000,  # ~80s/вызов — baseline
        tokens_in=1000,
        tokens_out=2000,
        llm_model="llama3.1:8b",
        created_at=datetime.utcnow(),
    )
    defaults.update(kw)
    m = PipelineRunMetrics(**defaults)
    session.add(m)
    session.commit()
    session.refresh(m)
    return m


class TestHealthOverview:
    def test_healthy_channel(self, client):
        tc, Session = client
        s = Session()
        _seed(s)
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/health/overview")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 1
        ch = data["channels"][0]
        assert ch["status"] == "healthy"
        assert ch["success_rate"] == 100.0
        assert ch["total_ms"]["p50"] == 10000
        assert ch["total_ms"]["p95"] == 10000
        assert ch["llm"]["llm_avg_latency_ms"] == 80000
        assert ch["llm"]["tokens_out"] == 2000

    def test_failing_channel_is_critical(self, client):
        tc, Session = client
        s = Session()
        _seed(s, success="false", errors_count=5)
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/health/overview")
        assert r.json()["channels"][0]["status"] == "critical"

    def test_window_filters_old_runs(self, client):
        tc, Session = client
        s = Session()
        _seed(s, created_at=datetime.utcnow() - timedelta(hours=48))
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/health/overview?window_hours=24")
        assert r.json()["count"] == 0


class TestAlerts:
    def test_no_alerts_for_healthy(self, client):
        tc, Session = client
        s = Session()
        _seed(s)
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/alerts")
        types = [a["type"] for a in r.json()["alerts"]]
        assert "run_failure" not in types
        assert "timeout" not in types
        assert "llm_degradation" not in types

    def test_run_failure_alert(self, client):
        tc, Session = client
        s = Session()
        _seed(s, success="false", errors_count=3)
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/alerts")
        alerts = [a for a in r.json()["alerts"] if a["type"] == "run_failure"]
        assert len(alerts) == 1
        assert alerts[0]["severity"] == "critical"
        assert alerts[0]["value"]["failed_runs"] == 1

    def test_timeout_alert(self, client):
        tc, Session = client
        s = Session()
        _seed(s, total_ms=2_000_000)  # > 1800s
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/alerts")
        alerts = [a for a in r.json()["alerts"] if a["type"] == "timeout"]
        assert len(alerts) == 1
        assert alerts[0]["severity"] == "critical"

    def test_llm_degradation_alert(self, client):
        tc, Session = client
        s = Session()
        # 200s/вызов > baseline 80s * 2
        _seed(s, llm_latency_ms=2_000_000)
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/alerts")
        alerts = [a for a in r.json()["alerts"] if a["type"] == "llm_degradation"]
        assert len(alerts) == 1
        assert alerts[0]["severity"] == "warning"

    def test_llm_errors_alert(self, client):
        tc, Session = client
        s = Session()
        _seed(s, llm_errors=2)
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/alerts")
        alerts = [a for a in r.json()["alerts"] if a["type"] == "llm_degradation"]
        assert len(alerts) == 1
        assert alerts[0]["value"]["llm_errors"] == 2

    def test_stale_channel_alert(self, client):
        tc, Session = client
        s = Session()
        # прогон был 48ч назад — за окно 24ч канал stale
        _seed(s, created_at=datetime.utcnow() - timedelta(hours=48))
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/alerts")
        alerts = [a for a in r.json()["alerts"] if a["type"] == "stale_channel"]
        assert len(alerts) == 1
        assert alerts[0]["channel_id"] == "ch1"

    def test_critical_sorted_first(self, client):
        tc, Session = client
        s = Session()
        _seed(s, success="false", llm_errors=1)
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/alerts")
        alerts = r.json()["alerts"]
        severities = [a["severity"] for a in alerts]
        assert severities == sorted(severities, key=lambda s: {"critical": 0, "warning": 1}[s])


class TestTrends:
    def test_hourly_buckets(self, client):
        tc, Session = client
        s = Session()
        # Фиксируем минуту = 50, чтобы now и now-30min гарантированно
        # попали в один час (иначе флейк на границе часа: минута < 30).
        now = datetime.utcnow().replace(minute=50, second=0, microsecond=0)
        _seed(s, topics_published=5)
        _seed(s, topics_published=3, created_at=now - timedelta(minutes=30))
        _seed(s, topics_published=1, created_at=now - timedelta(hours=3))
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/trends?hours=24")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 2  # два разных часа
        # последний час: 2 прогона, 8 публикаций
        latest = data["trends"][-1]
        assert latest["runs"] == 2
        assert latest["published"] == 8
        assert latest["avg_total_ms"] == 10000

    def test_empty_trends(self, client):
        tc, _ = client
        r = tc.get("/api/v1/metrics/pipeline/trends?hours=1")
        assert r.json()["count"] == 0


class TestSummaryLLM:
    def test_summary_includes_llm_block(self, client):
        tc, Session = client
        s = Session()
        _seed(s)
        _seed(s, execution_id="exec-2")
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/summary/all")
        assert r.status_code == 200
        ch = r.json()["channels"][0]
        assert ch["llm"]["llm_calls"] == 20
        assert ch["llm"]["llm_avg_latency_ms"] == 80000
        assert ch["llm"]["tokens_out"] == 4000


class TestRouteOrdering:
    def test_channel_route_still_works(self, client):
        """/{channel_id} не должен перехватить /alerts и /trends, но должен работать сам."""
        tc, Session = client
        s = Session()
        _seed(s)
        s.close()
        r = tc.get("/api/v1/metrics/pipeline/ch1")
        assert r.status_code == 200
        assert r.json()["count"] == 1
        r = tc.get("/api/v1/metrics/pipeline/alerts")
        assert r.status_code == 200
        r = tc.get("/api/v1/metrics/pipeline/trends")
        assert r.status_code == 200


if __name__ == "__main__":
    raise SystemExit("Run with pytest")
