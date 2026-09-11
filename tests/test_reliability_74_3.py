"""Sprint 74.3: Tests for Channel Pause production integration.

Покрывают хелперы сопоставления UUID канала -> ключ паузы и проверку
каналов на паузе до запуска пайплайна (automation/scheduler).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from types import SimpleNamespace

from backend.core.reliability import (
    channel_pause_key,
    channel_paused_for,
    pause_channel,
    channel_paused,
    reset_channel_pauses,
)


@pytest.fixture(autouse=True)
def _clean_pauses():
    reset_channel_pauses()
    yield
    reset_channel_pauses()


def _channel(**kwargs):
    """Минимальный объект, имитирующий ChannelORM для юнит-тестов."""
    defaults = dict(
        id="ch-uuid", name="Test Channel", platform="telegram",
        chat_id="@test_chan", vk_group_id="123",
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


class TestChannelPauseKey:
    def test_telegram_uses_chat_id(self):
        ch = _channel(platform="telegram", chat_id="@news", vk_group_id="999")
        assert channel_pause_key(ch) == "@news"

    def test_telegram_default_when_platform_unknown(self):
        ch = _channel(platform="", chat_id="@x")
        assert channel_pause_key(ch) == "@x"

    def test_vk_normalizes_group_id(self):
        ch = _channel(platform="vk", chat_id=None, vk_group_id="123")
        assert channel_pause_key(ch) == "-123"  # группа → отрицательный owner_id

    def test_vk_strips_club_prefix(self):
        ch = _channel(platform="vk", chat_id=None, vk_group_id="club456")
        assert channel_pause_key(ch) == "-456"

    def test_vk_keeps_existing_minus(self):
        ch = _channel(platform="vk", chat_id=None, vk_group_id="-123")
        assert channel_pause_key(ch) == "-123"

    def test_missing_key_returns_none(self):
        ch = _channel(platform="telegram", chat_id=None)
        assert channel_pause_key(ch) is None


class TestChannelPausedFor:
    def test_no_pause_is_zero(self):
        ch = _channel(chat_id="@news")
        assert channel_paused_for(ch) == 0.0

    def test_telegram_paused_detected_by_chat_id(self):
        ch = _channel(chat_id="@news")
        pause_channel("@news", 60)
        assert channel_paused_for(ch) > 0

    def test_vk_paused_detected_by_group_id(self):
        ch = _channel(platform="vk", vk_group_id="123")
        pause_channel("-123", 120)
        assert channel_paused_for(ch) > 0

    def test_expired_pause_not_flagged(self):
        ch = _channel(chat_id="@news")
        pause_channel("@news", -1)  # уже в прошлом
        assert channel_paused_for(ch) == 0.0

    def test_pause_for_other_channel_unaffected(self):
        ch = _channel(chat_id="@news")
        pause_channel("@other", 60)
        assert channel_paused_for(ch) == 0.0

    def test_missing_key_not_flagged(self):
        ch = _channel(chat_id=None)
        pause_channel("@news", 60)
        assert channel_paused_for(ch) == 0.0