"""Sprint 74.1: Tests for Reliability Core (retry policies) and Dead-Letter Queue."""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.reliability import (
    RetryPolicy,
    RETRY_POLICIES,
    get_policy,
    with_retry,
    retry_async,
    VKError,
    reset_breakers,
)
from core.error_taxonomy import ErrorType


@pytest.fixture(autouse=True)
def _clean_breakers():
    """Sprint 74.2: сброс circuit breaker между тестами (независимость тестов)."""
    reset_breakers()
    yield
    reset_breakers()


def _fake_response(status_code: int, headers: dict = None):
    """Минимальный мок requests.Response для классификации ошибок."""
    class FakeResponse:
        def __init__(self):
            self.status_code = status_code
            self.headers = headers or {}
            self.url = "https://fake"

        def raise_for_status(self):
            raise requests.HTTPError(f"{status_code}", response=self)

    return FakeResponse()


class TestRetryPolicy:
    def test_delay_exponential(self):
        p = RetryPolicy("t", base_delay=1.0, backoff_factor=2.0, max_delay=60.0, jitter=0.0)
        assert p.delay_for(0) == 1.0
        assert p.delay_for(1) == 2.0
        assert p.delay_for(2) == 4.0
        assert p.delay_for(10) == 60.0  # capped

    def test_retry_after_overrides_backoff(self):
        p = RetryPolicy("t", base_delay=1.0, max_delay=60.0)
        assert p.delay_for(0, retry_after=17) == 17.0
        assert p.delay_for(0, retry_after=999) == 60.0  # capped

    def test_should_retry(self):
        p = RetryPolicy("t", retry_on=(ErrorType.TRANSIENT, ErrorType.NETWORK))
        assert p.should_retry(ErrorType.TRANSIENT)
        assert p.should_retry(ErrorType.NETWORK)
        assert not p.should_retry(ErrorType.PERMANENT)
        assert not p.should_retry(ErrorType.CONFIGURATION)

    def test_policies_exist(self):
        assert "telegram" in RETRY_POLICIES
        assert "vk" in RETRY_POLICIES
        assert get_policy("unknown") is RETRY_POLICIES["external_api"]


class TestWithRetry:
    async def test_success_after_transient_failures(self):
        calls = {"n": 0}

        async def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise requests.ConnectionError("temp down")
            return "ok"

        result = await with_retry(
            flaky, policy=RetryPolicy("t", max_attempts=5, base_delay=0.01, jitter=0.0)
        )
        assert result == "ok"
        assert calls["n"] == 3

    async def test_no_retry_on_permanent(self):
        calls = {"n": 0}

        async def bad_request():
            calls["n"] += 1
            raise requests.HTTPError(response=_fake_response(400))

        with pytest.raises(requests.HTTPError):
            await with_retry(bad_request, policy=RetryPolicy("t", max_attempts=5, base_delay=0.01))

        assert calls["n"] == 1  # fail fast, no retry

    async def test_no_retry_on_configuration(self):
        calls = {"n": 0}

        async def unauthorized():
            calls["n"] += 1
            raise requests.HTTPError(response=_fake_response(401))

        with pytest.raises(requests.HTTPError):
            await with_retry(unauthorized, policy=RetryPolicy("t", max_attempts=5, base_delay=0.01))

        assert calls["n"] == 1

    async def test_max_attempts_exhausted(self):
        calls = {"n": 0}

        async def always_503():
            calls["n"] += 1
            raise requests.HTTPError(response=_fake_response(503))

        with pytest.raises(requests.HTTPError):
            await with_retry(
                always_503,
                policy=RetryPolicy("t", max_attempts=3, base_delay=0.01, jitter=0.0),
            )

        assert calls["n"] == 3

    async def test_retry_after_429_respected(self):
        sleeps = []

        async def fake_sleep(seconds):
            sleeps.append(seconds)

        async def rate_limited():
            raise requests.HTTPError(response=_fake_response(429, headers={"Retry-After": "7"}))

        with pytest.raises(requests.HTTPError):
            await with_retry(
                rate_limited,
                policy=RetryPolicy("t", max_attempts=2, base_delay=1.0, jitter=0.0),
                sleep=fake_sleep,
            )

        assert sleeps == [7.0]

    async def test_on_final_failure_callback(self):
        fired = []

        async def fail():
            raise requests.ConnectionError("down")

        with pytest.raises(requests.ConnectionError):
            await with_retry(
                fail,
                policy=RetryPolicy("t", max_attempts=2, base_delay=0.01),
                on_final_failure=lambda e: fired.append(e),
            )

        assert len(fired) == 1

    async def test_vk_transient_retried(self):
        calls = {"n": 0}

        async def vk_flood():
            calls["n"] += 1
            raise VKError(9, "Flood control")

        with pytest.raises(VKError):
            await with_retry(
                vk_flood,
                policy=RetryPolicy("t", max_attempts=3, base_delay=0.01),
            )

        assert calls["n"] == 3  # flood → retried

    async def test_vk_auth_not_retried(self):
        calls = {"n": 0}

        async def vk_auth():
            calls["n"] += 1
            raise VKError(5, "User authorization failed")

        with pytest.raises(VKError):
            await with_retry(
                vk_auth,
                policy=RetryPolicy("t", max_attempts=3, base_delay=0.01),
            )

        assert calls["n"] == 1  # configuration → fail fast

    async def test_retry_async_decorator(self):
        calls = {"n": 0}

        @retry_async("external_api")
        async def flaky():
            calls["n"] += 1
            if calls["n"] < 2:
                raise requests.Timeout("slow")
            return 42

        assert await flaky() == 42
        assert calls["n"] == 2


class TestVKErrorClassification:
    def test_code_map(self):
        assert VKError(9, "flood").error_type == ErrorType.TRANSIENT
        assert VKError(6, "too many").error_type == ErrorType.TRANSIENT
        assert VKError(5, "auth").error_type == ErrorType.CONFIGURATION
        assert VKError(100, "params").error_type == ErrorType.PERMANENT
        assert VKError(999, "?").error_type == ErrorType.UNKNOWN


# ---------------------------------------------------------------------------
# Dead-Letter Queue (isolated in-memory SQLite)
# ---------------------------------------------------------------------------

@pytest.fixture()
def dlq():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    from core.database import Base
    from core.models.pipeline_failure_orm import PipelineFailure  # регистрирует таблицу
    Base.metadata.create_all(bind=engine, tables=[PipelineFailure.__table__])
    Session = sessionmaker(bind=engine)
    from backend.core.dead_letter import DeadLetterQueue
    queue = DeadLetterQueue(Session())
    yield queue
    queue.close()


class TestDeadLetterQueue:
    def test_enqueue_and_list(self, dlq):
        failure = dlq.enqueue(
            channel_id="ch-1",
            pipeline="publishing",
            job="publish_telegram",
            error_message="max attempts exhausted",
            content_payload={"text": "hello", "chat_id": "@test"},
            retry_delay_seconds=0,
        )
        assert failure.id is not None
        assert failure.resolved is False

        items = dlq.list()
        assert len(items) == 1
        assert items[0].context["content"]["text"] == "hello"

    def test_due_for_retry(self, dlq):
        dlq.enqueue(
            channel_id="ch-1", pipeline="publishing", job="publish_telegram",
            error_message="timeout", error_type="timeout", retry_delay_seconds=0,
        )
        dlq.enqueue(
            channel_id="ch-2", pipeline="publishing", job="publish_telegram",
            error_message="later", error_type="publish_error", retry_delay_seconds=3600,
        )
        due = dlq.due_for_retry()
        assert len(due) == 1
        assert due[0].channel_id == "ch-1"

    def test_requeue_and_resolve(self, dlq):
        failure = dlq.enqueue(
            channel_id="ch-1", pipeline="publishing", job="publish_vk",
            error_message="rate limit", error_type="rate_limit", retry_delay_seconds=3600,
        )
        requeued = dlq.requeue(failure.id)
        assert requeued.retry_at is not None
        assert requeued.retry_at <= datetime.utcnow()
        assert requeued.attempt == 0

        resolved = dlq.mark_resolved(failure.id, resolution="retry_success")
        assert resolved.resolved is True
        assert dlq.list(unresolved_only=True) == []

    def test_stats(self, dlq):
        dlq.enqueue(
            channel_id="ch-1", pipeline="publishing", job="publish_telegram",
            error_message="e1", error_type="timeout", retry_delay_seconds=0,
        )
        dlq.enqueue(
            channel_id="ch-1", pipeline="publishing", job="publish_telegram",
            error_message="e2", error_type="timeout", retry_delay_seconds=0,
        )
        stats = dlq.stats()
        assert stats["total"] == 2
        assert stats["unresolved"] == 2
        assert stats["by_type"]["timeout"] == 2
        assert stats["by_channel"]["ch-1"] == 2
