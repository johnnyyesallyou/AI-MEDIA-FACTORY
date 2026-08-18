"""VK Engagement Tracker - Sprint 36.2.

Собирает метрики engagement из VK API.

Примечание: для group token wall.getById недоступен,
используем wall.get для получения последних постов.
"""
import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime


logger = logging.getLogger(__name__)


class VKEngagementTracker:
    """Сборщик метрик из VK."""

    def __init__(self, access_token: str, group_id: str):
        self.access_token = access_token
        self.group_id = group_id
        self.owner_id = group_id if group_id.startswith("-") else f"-{group_id}"
        self.base_url = "https://api.vk.com/method"
        self.api_version = "5.131"
        self.logger = logging.getLogger(self.__class__.__name__)

    def _call_api(self, method: str, params: Dict) -> Optional[Dict]:
        """Универсальный вызов VK API."""
        try:
            url = f"{self.base_url}/{method}"
            params = dict(params)
            params["access_token"] = self.access_token
            params["v"] = self.api_version

            r = requests.get(url, params=params, timeout=10)
            data = r.json()

            if "response" in data:
                return data["response"]
            elif "error" in data:
                self.logger.warning(f"VK API error: {data['error'].get('error_msg')}")
                return None
            return None
        except Exception as e:
            self.logger.warning(f"VK API call failed: {e}")
            return None

    def get_latest_posts(self, count: int = 5) -> List[Dict]:
        """Получает последние посты группы (доступно с group token)."""
        response = self._call_api("wall.get", {
            "owner_id": self.owner_id,
            "count": count,
            "extended": 0,
        })

        if not response or not response.get("items"):
            return []

        posts = []
        for post in response["items"]:
            metrics = {
                "post_id": f"{post['owner_id']}_{post['id']}",
                "date": post.get("date"),
                "text": post.get("text", "")[:100],
                "likes": post.get("likes", {}).get("count", 0),
                "reposts": post.get("reposts", {}).get("count", 0),
                "comments": post.get("comments", {}).get("count", 0),
                "views": post.get("views", {}).get("count", 0),
            }
            posts.append(metrics)

        return posts

    def get_post_metrics(self, post_id: str) -> Optional[Dict]:
        """Получает метрики для поста (через wall.getById если доступен)."""
        response = self._call_api("wall.getById", {"posts": post_id})

        if not response or not response.get("items"):
            return None

        post = response["items"][0]
        return self._extract_metrics(post)

    def _extract_metrics(self, post: Dict) -> Dict:
        """Извлекает метрики из поста."""
        return {
            "post_id": f"{post['owner_id']}_{post['id']}",
            "date": post.get("date"),
            "text": post.get("text", "")[:100],
            "likes": post.get("likes", {}).get("count", 0),
            "reposts": post.get("reposts", {}).get("count", 0),
            "comments": post.get("comments", {}).get("count", 0),
            "views": post.get("views", {}).get("count", 0),
            "has_attachments": len(post.get("attachments", [])) > 0,
        }

    def get_group_stats(self) -> Optional[Dict]:
        """Получает статистику группы."""
        response = self._call_api("groups.getById", {
            "group_id": self.group_id.lstrip("-"),
            "fields": "members_count,activity,status"
        })

        if not response:
            return None

        # VK API может возвращать разные форматы:
        # Старый: {"groups": [...]}
        # Новый: [...] (прямой список)
        group = None
        if isinstance(response, list) and response:
            group = response[0]
        elif isinstance(response, dict) and response.get("groups"):
            group = response["groups"][0]

        if not group:
            return None

        return {
            "name": group.get("name"),
            "screen_name": group.get("screen_name"),
            "members_count": group.get("members_count"),
            "status": group.get("status"),
        }

    def collect_metrics(self, post_id: str = None) -> Dict:
        """
        Собирает метрики.

        Если post_id не указан - собирает метрики для последних 5 постов.
        """
        metrics = {
            "platform": "vk",
            "group_id": self.group_id,
            "collected_at": datetime.utcnow().isoformat(),
        }

        # Информация о группе
        group_stats = self.get_group_stats()
        if group_stats:
            metrics["group_name"] = group_stats.get("name")
            metrics["members_count"] = group_stats.get("members_count")

        # Метрики постов
        if post_id:
            post_metrics = self.get_post_metrics(post_id)
            if post_metrics:
                metrics["post"] = post_metrics
        else:
            # Собираем метрики для последних постов
            posts = self.get_latest_posts(5)
            metrics["posts"] = posts
            metrics["posts_count"] = len(posts)

        return metrics