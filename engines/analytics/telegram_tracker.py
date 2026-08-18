"""Telegram Engagement Tracker - Sprint 36.2.

Собирает метрики engagement из Telegram:
- views (через парсинг t.me embed для публичных каналов)
- subscribers (через getChatMemberCount)
- channel info (через getChat)
"""
import logging
import re
import requests
from typing import Dict, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class TelegramEngagementTracker:
    """Сборщик метрик из Telegram."""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_channel_info(self) -> Optional[Dict]:
        """Получает информацию о канале."""
        try:
            url = f"{self.base_url}/getChat"
            r = requests.get(url, params={"chat_id": self.chat_id}, timeout=10)
            data = r.json()

            if data.get("ok"):
                result = data["result"]
                return {
                    "type": result.get("type"),
                    "title": result.get("title"),
                    "username": result.get("username"),
                    "description": result.get("description"),
                }
            return None
        except Exception as e:
            self.logger.warning(f"getChat failed: {e}")
            return None

    def get_member_count(self) -> Optional[int]:
        """Получает количество подписчиков."""
        try:
            url = f"{self.base_url}/getChatMemberCount"
            r = requests.get(url, params={"chat_id": self.chat_id}, timeout=10)
            data = r.json()

            if data.get("ok"):
                return data["result"]
            return None
        except Exception as e:
            self.logger.warning(f"getChatMemberCount failed: {e}")
            return None

    def get_message_metrics(self, message_id: int) -> Optional[Dict]:
        """
        Получает метрики для конкретного сообщения.

        Telegram Bot API ограничения:
        - Для каналов: нет прямого доступа к views/forwards
        - Для публичных каналов: можно парсить t.me/channel/message_id?embed=1
        - Для приватных: метрики недоступны
        """
        channel_info = self.get_channel_info()
        if not channel_info:
            return None

        username = channel_info.get("username")
        if not username:
            return {
                "views": None,
                "forwards": None,
                "reactions": None,
                "note": "Private channel - no public metrics available"
            }

        try:
            url = f"https://t.me/{username}/{message_id}?embed=1"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            r = requests.get(url, headers=headers, timeout=10)

            if r.status_code == 200:
                views_match = re.search(r'(\d+(?:\.\d+)?[KMB]?) views?', r.text, re.I)
                views = None
                if views_match:
                    views_str = views_match.group(1)
                    multiplier = 1
                    if 'K' in views_str:
                        multiplier = 1000
                        views_str = views_str.replace('K', '')
                    elif 'M' in views_str:
                        multiplier = 1000000
                        views_str = views_str.replace('M', '')
                    elif 'B' in views_str:
                        multiplier = 1000000000
                        views_str = views_str.replace('B', '')
                    views = int(float(views_str) * multiplier)

                return {
                    "views": views,
                    "forwards": None,
                    "reactions": None,
                    "public_url": f"https://t.me/{username}/{message_id}"
                }
            return None
        except Exception as e:
            self.logger.warning(f"Failed to parse t.me: {e}")
            return None

    def collect_metrics(self, message_id: int) -> Dict:
        """Собирает все доступные метрики для поста."""
        metrics = {
            "platform": "telegram",
            "channel_id": self.chat_id,
            "message_id": message_id,
            "collected_at": datetime.utcnow().isoformat(),
        }

        channel_info = self.get_channel_info()
        if channel_info:
            metrics["channel_type"] = channel_info.get("type")
            metrics["channel_title"] = channel_info.get("title")

        member_count = self.get_member_count()
        if member_count:
            metrics["subscribers"] = member_count

        message_metrics = self.get_message_metrics(message_id)
        if message_metrics:
            metrics.update(message_metrics)

        return metrics