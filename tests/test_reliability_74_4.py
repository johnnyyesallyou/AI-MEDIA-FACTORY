"""Sprint 74.4: Tests for Health Checks + DLQ auto-enqueue + manual pause API."""
import sys
import os
import asyncio
from datetime import datetime
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import requests
from unittest.mock import patch, AsyncMock, MagicMock

from backend.core.reliability import (
    pause_channel,
    channel_paused,
    reset_channel_pauses,
    channel_pause_key,
    channel_paused_for,
)
from backend.core.health import check_telegram, check_vk, check_all


@pytest.fixture(autouse=True)
def _clean_pauses():
    reset_channel_pauses()
    yield
    reset_channel_pauses()


class TestHealthCheckTelegram:
    @pytest.mark.asyncio
    async def test_telegram_ok(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True, "result": {"id": 123}}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(
                return_value=AsyncMock(
                    get=AsyncMock(return_value=mock_resp)
                )
            )
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await check_telegram("fake_token")

        assert result["status"] == "ok"
        assert "latency_ms" in result

    @pytest.mark.asyncio
    async def test_telegram_error(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.json.return_value = {"ok": False, "description": "Unauthorized"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(
                return_value=AsyncMock(
                    get=AsyncMock(return_value=mock_resp)
                )
            )
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await check_telegram("bad_token")

        assert result["status"] == "error"


class TestHealthCheckVK:
    @pytest.mark.asyncio
    async def test_vk_ok(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": [{"id": 123}]}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(
                return_value=AsyncMock(
                    post=AsyncMock(return_value=mock_resp)
                )
            )
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await check_vk("fake_token", "123")

        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_vk_error(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"error": {"error_code": 5, "error_msg": "Auth failed"}}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(
                return_value=AsyncMock(
                    post=AsyncMock(return_value=mock_resp)
                )
            )
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await check_vk("bad_token", "123")

        assert result["status"] == "error"


class TestHealthCheckAll:
    @pytest.mark.asyncio
    async def test_no_credentials_returns_unknown(self):
        result = await check_all(None)
        assert result["status"] == "unknown"

    @pytest.mark.asyncio
    async def test_all_ok(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True, "result": {"id": 123}}
        mock_vk_resp = MagicMock()
        mock_vk_resp.json.return_value = {"response": [{"id": 1}]}

        with patch("httpx.AsyncClient") as mock_client:
            mock_ctx = AsyncMock()
            mock_ctx.get = AsyncMock(return_value=mock_resp)
            mock_ctx.post = AsyncMock(return_value=mock_vk_resp)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_ctx)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await check_all({
                "telegram": {"bot_token": "t"},
                "vk": {"access_token": "v", "group_id": "1"},
            })

        assert result["status"] == "ok"
        assert result["platforms"]["telegram"]["status"] == "ok"
        assert result["platforms"]["vk"]["status"] == "ok"


class TestManualPauseAPI:
    def test_pause_and_resume(self):
        from fastapi.testclient import TestClient
        from backend.app.api.v1.reliability import router

        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        # Pause
        resp = client.post("/reliability/channels/@test/pause?seconds=60")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["paused_for_seconds"] == 60.0
        assert body["remaining_seconds"] > 0

        # Check status
        resp = client.get("/reliability/channels/@test/pause")
        assert resp.status_code == 200
        body = resp.json()
        assert body["paused"] is True
        assert body["remaining_seconds"] > 0

        # Resume
        resp = client.post("/reliability/channels/@test/resume")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["remaining_seconds"] == 0.0

        # Check status after resume
        resp = client.get("/reliability/channels/@test/pause")
        body = resp.json()
        assert body["paused"] is False


class TestDLQAutoEnqueue:
    @pytest.mark.asyncio
    async def test_telegram_enqueue_on_failure(self):
        """При исчерпании retry telegram publisher вызывает dlq.enqueue."""
        with patch("backend.engines.telegram_publisher.TelegramPublisher._post") as mock_post, \
             patch("backend.core.dead_letter.get_dlq") as mock_get_dlq:

            mock_post.side_effect = requests.HTTPError("429 Too Many Requests")
            mock_dlq = MagicMock()
            mock_failure = MagicMock()
            mock_failure.id = "fail-123"
            mock_failure.retry_at = datetime.utcnow()
            mock_dlq.enqueue.return_value = mock_failure
            mock_dlq.close = MagicMock()
            mock_get_dlq.return_value = mock_dlq

            publisher = __import__(
                "backend.engines.telegram_publisher",
                fromlist=["TelegramPublisher"],
            ).TelegramPublisher("fake_token", "@test")

            result = await publisher.send_message("hello")

            assert result["success"] is False
            mock_dlq.enqueue.assert_called_once()
            call_kwargs = mock_dlq.enqueue.call_args[1]
            assert call_kwargs["channel_id"] == "@test"
            assert call_kwargs["content_payload"]["platform"] == "telegram"
            assert call_kwargs["content_payload"]["text"] == "hello"

    @pytest.mark.asyncio
    async def test_vk_enqueue_on_failure(self):
        """При исчерпании retry VK publisher вызывает dlq.enqueue."""
        with patch("backend.engines.vk_publisher.with_retry") as mock_retry, \
             patch("backend.core.dead_letter.get_dlq") as mock_get_dlq:

            from backend.core.reliability import VKError
            mock_retry.side_effect = VKError(6, "Too many requests")
            mock_dlq = MagicMock()
            mock_failure = MagicMock()
            mock_failure.id = "fail-vk-1"
            mock_failure.retry_at = datetime.utcnow()
            mock_dlq.enqueue.return_value = mock_failure
            mock_dlq.close = MagicMock()
            mock_get_dlq.return_value = mock_dlq

            from backend.engines.vk_publisher import publish_to_vk
            result = await publish_to_vk(
                {"title": "T", "content": "C"},
                "-123",
                "fake_token",
            )

            assert result is None
            mock_dlq.enqueue.assert_called_once()
            call_kwargs = mock_dlq.enqueue.call_args[1]
            assert call_kwargs["channel_id"] == "-123"
            assert call_kwargs["content_payload"]["platform"] == "vk"


class TestChannelPauseForKey:
    def test_pause_by_chat_id(self):
        pause_channel("@news", 60)
        ch = SimpleNamespace(chat_id="@news", platform="telegram", vk_group_id=None)
        assert channel_paused_for(ch) > 0

    def test_pause_by_vk_group(self):
        pause_channel("-123", 120)
        ch = SimpleNamespace(chat_id=None, platform="vk", vk_group_id="123")
        assert channel_paused_for(ch) > 0

    def test_pause_expires(self):
        pause_channel("@news", -1)
        ch = SimpleNamespace(chat_id="@news", platform="telegram", vk_group_id=None)
        assert channel_paused_for(ch) == 0.0
