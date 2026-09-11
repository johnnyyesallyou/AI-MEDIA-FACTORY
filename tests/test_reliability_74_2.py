"""Sprint 74.2: Tests for Circuit Breaker, Channel Pause, Alert-Disable, Self-Healing."""
import sys
import os
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.reliability import (
    BreakerConfig,
    CircuitBreaker,
    CircuitState,
    CircuitOpenError,
    ChannelPausedError,
    RetryPolicy,
    with_retry,
    get_breaker,
    reset_breakers,
    pause_channel,
    channel_paused,
    reset_channel_pauses,
    channel_pauses_snapshot,
)
from backend.core.self_healing import SelfHealingWorker


def _fake_response(status_code: int, headers: dict = None):
    class FakeResponse:
        def __init__(self):
            self.status_code = status_code
            self.headers = headers or {}
            self.url = "https://fake"

        def raise_for_status(self):
            raise requests.HTTPError(f"{status_code}", response=self)

    return FakeResponse()


@pytest.fixture(autouse=True)
def _clean_state():
    reset_breakers()
    reset_channel_pauses()
    yield
    reset_breakers()
    reset_channel_pauses()


def _policy(attempts=3, base_delay=0.01):
    return RetryPolicy("t", max_attempts=attempts, base_delay=base_delay, jitter=0.0)


# ---------------------------------------------------------------------------
# CircuitBreaker unit
# ---------------------------------------------------------------------------

class TestCircuitBreaker:
    def test_starts_closed(self):
        b = CircuitBreaker("test")
        assert b.state == CircuitState.CLOSED
        assert b.is_available()

    def test_opens_after_threshold(self):
        b = CircuitBreaker("test", BreakerConfig(failure_threshold=3))
        for _ in range(3):
            b.record_failure("boom")
        assert b.state == CircuitState.OPEN
        assert not b.is_available()

    def test_success_resets_counter(self):
        b = CircuitBreaker("test", BreakerConfig(failure_threshold=3))
        b.record_failure("e1")
        b.record_failure("e2")
        b.record_success()
        assert b.failure_count == 0
        assert b.state == CircuitState.CLOSED

    def test_half_open_after_recovery_timeout(self):
        b = CircuitBreaker("test", BreakerConfig(failure_threshold=1, recovery_timeout=0.0))
        b.record_failure("boom")
        assert b.state == CircuitState.OPEN
        assert b.is_available()  # timeout=0 → immediately half_open
        assert b.state == CircuitState.HALF_OPEN

    def test_half_open_success_closes(self):
        b = CircuitBreaker("test", BreakerConfig(failure_threshold=1, recovery_timeout=0.0))
        b.record_failure("boom")
        b.is_available()  # → half_open
        b.record_success()
        assert b.state == CircuitState.CLOSED

    def test_half_open_failure_reopens(self):
        b = CircuitBreaker("test", BreakerConfig(failure_threshold=1, recovery_timeout=0.0))
        b.record_failure("boom")
        b.is_available()  # → half_open, consumes probe
        assert not b.is_available()  # probe limit
        b.record_failure("probe failed")
        assert b.state == CircuitState.OPEN
        assert b.total_opens == 2

    def test_get_breaker_registry(self):
        b1 = get_breaker("telegram")
        assert get_breaker("telegram") is b1
        b1.record_failure("x")


# ---------------------------------------------------------------------------
# with_retry integration
# ---------------------------------------------------------------------------

class TestWithRetryBreakerIntegration:
    async def test_breaker_blocks_calls_when_open(self):
        breaker = get_breaker("telegram")
        for _ in range(5):
            breaker.record_failure("boom")

        calls = {"n": 0}

        async def fn():
            calls["n"] += 1
            return "ok"

        with pytest.raises(CircuitOpenError):
            await with_retry(fn, policy=_policy(), platform="telegram")
        assert calls["n"] == 0  # API never touched

    async def test_success_records_breaker_success(self):
        async def fn():
            return "ok"

        result = await with_retry(fn, policy=_policy(), platform="telegram")
        assert result == "ok"
        assert get_breaker("telegram").state == CircuitState.CLOSED
        assert get_breaker("telegram").success_count == 1

    async def test_transient_failures_count_toward_open(self):
        async def always_transient():
            raise requests.ConnectionError("down")

        for _ in range(2):  # 2 runs × 2 attempts = 4 failures
            with pytest.raises(requests.ConnectionError):
                await with_retry(
                    always_transient,
                    policy=RetryPolicy("t", max_attempts=2, base_delay=0.01, jitter=0.0),
                    platform="telegram",
                )
        # threshold 5 → ещё closed
        assert get_breaker("telegram").state == CircuitState.CLOSED

        with pytest.raises(requests.ConnectionError):
            await with_retry(
                always_transient,
                policy=RetryPolicy("t", max_attempts=1, base_delay=0.01, jitter=0.0),
                platform="telegram",
            )
        # 5-й подряд failure → open
        assert get_breaker("telegram").state == CircuitState.OPEN

        with pytest.raises(CircuitOpenError):
            await with_retry(always_transient, policy=_policy(), platform="telegram")


# ---------------------------------------------------------------------------
# Channel-wide pause (rate limiter ↔ retry)
# ---------------------------------------------------------------------------

class TestChannelPause:
    async def test_429_pauses_whole_channel(self):
        sleeps = []

        async def fake_sleep(seconds: float) -> None:
            sleeps.append(seconds)
            await asyncio.sleep(0)  # ����� ��� ������ event loop �� Windows

        async def rate_limited():
            raise requests.HTTPError(
                response=_fake_response(429, {"Retry-After": "30"})
            )

        with pytest.raises(ChannelPausedError):
            await with_retry(
                rate_limited,
                policy=_policy(attempts=2),
                channel_id="ch-429",
                platform="telegram",
                sleep=fake_sleep,
            )

        assert channel_paused("ch-429") > 0
        assert "ch-429" in channel_pauses_snapshot()
        # sleep был вызован ровно один раз с параметром 30.0
        assert sleeps == [30.0]

    async def test_paused_channel_fails_fast(self):
        pause_channel("ch-p", 60)
        assert channel_paused("ch-p") > 0

        calls = {"n": 0}

        async def fn():
            calls["n"] += 1
            return "ok"

        with pytest.raises(ChannelPausedError):
            await with_retry(fn, policy=_policy(), channel_id="ch-p")
        assert calls["n"] == 0  # fail fast, API not touched

    async def test_other_channel_unaffected(self):
        pause_channel("ch-a", 60)

        async def fn():
            return "ok"

        result = await with_retry(fn, policy=_policy(), channel_id="ch-b")
        assert result == "ok"

    async def test_pause_expires(self):
        pause_channel("ch-x", -1)  # already in the past
        assert channel_paused("ch-x") == 0

    async def test_no_pause_without_channel_id(self):
        sleeps = []

        async def fake_sleep(seconds: float) -> None:
            sleeps.append(seconds)
            await asyncio.sleep(0)  # отдаём управление event loop (Windows)

        async def rate_limited():
            raise requests.HTTPError(
                response=_fake_response(429, {"Retry-After": "30"})
            )

        # без channel_id — обычный retry-поток, пауза не ставится
        with pytest.raises(requests.HTTPError):
            await with_retry(
                rate_limited,
                policy=_policy(attempts=2),
                sleep=fake_sleep,
            )
        assert channel_pauses_snapshot() == {}
        # retry уважает Retry-After 30 (без sleep-инъекции тест ждал бы реальные 30с)
        assert 30.0 in sleeps


# ---------------------------------------------------------------------------
# Alert-disable (CONFIGURATION → is_active=False)
# ---------------------------------------------------------------------------

@pytest.fixture()
def channel_db():
    """In-memory SQLite с channels + pipeline_failures."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    from core.database import Base
    from core.models.channel_orm import ChannelORM
    from core.models.pipeline_failure_orm import PipelineFailure
    Base.metadata.create_all(
        bind=engine, tables=[ChannelORM.__table__, PipelineFailure.__table__]
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    ch = ChannelORM(
        id="ch-conf", name="Test Channel", platform="telegram",
        bot_token="123:abc", chat_id="@test", is_active=True,
    )
    session.add(ch)
    session.commit()

    # Подменяем фабрику БД в reliability (_alert_disable_channel)
    import core.database as db_mod
    orig_sessionlocal = db_mod.SessionLocal
    db_mod.SessionLocal = Session
    yield session
    db_mod.SessionLocal = orig_sessionlocal
    session.close()


class TestAlertDisable:
    async def test_configuration_error_disables_channel(self, channel_db):
        from core.models.channel_orm import ChannelORM
        from core.models.pipeline_failure_orm import PipelineFailure

        async def unauthorized():
            raise requests.HTTPError(response=_fake_response(401))

        with pytest.raises(requests.HTTPError):
            await with_retry(
                unauthorized, policy=_policy(attempts=3),
                channel_id="ch-conf", platform="telegram",
            )

        ch = channel_db.query(ChannelORM).filter(ChannelORM.id == "ch-conf").first()
        channel_db.refresh(ch)
        assert ch.is_active is False

        failures = channel_db.query(PipelineFailure).filter(
            PipelineFailure.error_code == "alert_disable"
        ).all()
        assert len(failures) == 1
        assert "auto-disabled" in failures[0].error_message

    async def test_no_disable_without_channel_id(self, channel_db):
        from core.models.channel_orm import ChannelORM

        async def unauthorized():
            raise requests.HTTPError(response=_fake_response(401))

        with pytest.raises(requests.HTTPError):
            await with_retry(unauthorized, policy=_policy(attempts=3))

        ch = channel_db.query(ChannelORM).filter(ChannelORM.id == "ch-conf").first()
        assert ch.is_active is True


# ---------------------------------------------------------------------------
# Self-Healing Worker (DLQ republish)
# ---------------------------------------------------------------------------

@pytest.fixture()
def dlq_env():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    from core.database import Base
    from core.models.pipeline_failure_orm import PipelineFailure
    Base.metadata.create_all(bind=engine, tables=[PipelineFailure.__table__])
    Session = sessionmaker(bind=engine)
    session = Session()
    from backend.core.dead_letter import DeadLetterQueue
    yield DeadLetterQueue(session), session
    session.close()


class TestSelfHealingWorker:
    async def test_requeues_and_resolves(self, dlq_env, monkeypatch):
        dlq, session = dlq_env
        failure = dlq.enqueue(
            channel_id="ch-1", pipeline="publishing", job="publish_telegram",
            error_message="timeout", error_type="timeout",
            content_payload={
                "platform": "telegram", "chat_id": "@test",
                "text": "hello", "bot_token": "123:abc",
            },
            retry_delay_seconds=0,
        )

        worker = SelfHealingWorker(db=session)

        async def fake_send_message(self, text, **kwargs):
            return {"success": True, "message_id": 42}

        from backend.engines.telegram_publisher import TelegramPublisher
        monkeypatch.setattr(TelegramPublisher, "send_message", fake_send_message)

        summary = await worker.run_once()
        assert summary["success"] == 1
        refreshed = session.query(type(failure)).filter_by(id=failure.id).first()
        assert refreshed.resolved is True
        assert worker.last_run_summary["processed"] == 1

    async def test_failure_increments_attempt(self, dlq_env, monkeypatch):
        dlq, session = dlq_env
        failure = dlq.enqueue(
            channel_id="ch-1", pipeline="publishing", job="publish_telegram",
            error_message="timeout", error_type="timeout",
            content_payload={
                "platform": "telegram", "chat_id": "@test",
                "text": "hello", "bot_token": "123:abc",
            },
            retry_delay_seconds=0,
            attempts=0,  # чистый cчётчик self-healing: попыток ещё не было
        )

        worker = SelfHealingWorker(db=session)

        async def failing_send(self, text, **kwargs):
            return {"success": False, "error": "still down"}

        from backend.engines.telegram_publisher import TelegramPublisher
        monkeypatch.setattr(TelegramPublisher, "send_message", failing_send)

        summary = await worker.run_once()
        assert summary["retry"] == 1
        refreshed = session.query(type(failure)).filter_by(id=failure.id).first()
        assert refreshed.resolved is False
        assert refreshed.attempt == 1
        assert refreshed.retry_at > datetime.utcnow()

    async def test_skips_when_breaker_open(self, dlq_env):
        dlq, session = dlq_env
        dlq.enqueue(
            channel_id="ch-1", pipeline="publishing", job="publish_telegram",
            error_message="timeout", error_type="timeout",
            content_payload={"platform": "telegram", "chat_id": "@x", "text": "t"},
            retry_delay_seconds=0,
        )
        breaker = get_breaker("telegram")
        for _ in range(5):
            breaker.record_failure("boom")

        worker = SelfHealingWorker(db=session)
        summary = await worker.run_once()
        assert summary["skip"] == 1
        assert summary["success"] == 0

    async def test_skips_paused_channel(self, dlq_env):
        dlq, session = dlq_env
        dlq.enqueue(
            channel_id="ch-pause", pipeline="publishing", job="publish_telegram",
            error_message="timeout", error_type="timeout",
            content_payload={"platform": "telegram", "chat_id": "@x", "text": "t"},
            retry_delay_seconds=0,
        )
        pause_channel("ch-pause", 300)

        worker = SelfHealingWorker(db=session)
        summary = await worker.run_once()
        assert summary["skip"] == 1

    async def test_not_due_skipped(self, dlq_env):
        dlq, session = dlq_env
        dlq.enqueue(
            channel_id="ch-1", pipeline="publishing", job="publish_telegram",
            error_message="later", error_type="timeout",
            content_payload={"platform": "telegram", "chat_id": "@x", "text": "t"},
            retry_delay_seconds=3600,
        )
        worker = SelfHealingWorker(db=session)
        summary = await worker.run_once()
        assert summary["processed"] == 0
