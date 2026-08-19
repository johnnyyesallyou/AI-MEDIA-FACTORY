"""Engagement Collection Job - Sprint 36.3.

Периодический сбор метрик engagement для опубликованных постов.

Pipeline:
  1. Находит все published posts (Telegram/VK)
  2. Для каждого канала создаёт соответствующий tracker
  3. Собирает метрики для каждого поста
  4. Записывает через AnalyticsEngine.record_post_metric()

Запуск: каждые 6 часов (через scheduler)
"""
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from core.monitoring import monitor_job
from engines.analytics_engine import AnalyticsEngine
from engines.analytics import TelegramEngagementTracker, VKEngagementTracker


logger = logging.getLogger(__name__)


class EngagementCollectionJob:
    """Периодический сбор метрик engagement."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.analytics = AnalyticsEngine()

    @monitor_job("EngagementCollectionJob")
    def run(
        self,
        channel_id: Optional[str] = None,
        limit: int = 100,
        hours_back: int = 72,
    ) -> Dict[str, Any]:
        """
        Собирает метрики для опубликованных постов.

        Args:
            channel_id: Ограничить сбор конкретным каналом
            limit: Максимум постов для обработки
            hours_back: Рассматривать посты за последние N часов

        Returns:
            Статистика сбора метрик
        """
        self.logger.info(
            f"EngagementCollectionJob started "
            f"(channel={channel_id}, limit={limit}, hours_back={hours_back})"
        )

        db = SessionLocal()
        try:
            # 1. Находим published posts
            posts = self._find_published_posts(db, channel_id, limit, hours_back)
            self.logger.info(f"Found {len(posts)} published posts")

            if not posts:
                return {
                    "status": "ok",
                    "processed": 0,
                    "message": "No published posts to process"
                }

            # 2. Группируем по каналу
            posts_by_channel = self._group_by_channel(posts)

            # 3. Обрабатываем каждый канал
            stats = {
                "status": "ok",
                "processed": 0,
                "success": 0,
                "failed": 0,
                "by_platform": {},
                "by_channel": {},
            }

            for ch_id, channel_posts in posts_by_channel.items():
                channel = db.query(ChannelORM).filter(
                    ChannelORM.id == ch_id
                ).first()

                if not channel:
                    self.logger.warning(f"Channel {ch_id} not found")
                    continue

                result = self._process_channel(channel, channel_posts)
                stats["processed"] += result["processed"]
                stats["success"] += result["success"]
                stats["failed"] += result["failed"]
                stats["by_platform"][channel.platform] = (
                    stats["by_platform"].get(channel.platform, 0) + result["success"]
                )
                stats["by_channel"][channel.name] = result

            return stats

        except Exception as e:
            self.logger.exception(f"EngagementCollectionJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()

    def _find_published_posts(
        self,
        db,
        channel_id: Optional[str],
        limit: int,
        hours_back: int,
    ) -> List[ContentORM]:
        """Находит опубликованные посты."""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours_back)

        query = db.query(ContentORM).filter(
            ContentORM.status == "published",
            ContentORM.published_at >= cutoff,
        )

        if channel_id:
            query = query.filter(ContentORM.channel_id == channel_id)

        return query.order_by(ContentORM.published_at.desc()).limit(limit).all()

    def _group_by_channel(self, posts: List[ContentORM]) -> Dict[str, List[ContentORM]]:
        """Группирует посты по channel_id."""
        groups = {}
        for post in posts:
            ch_id = post.channel_id
            if ch_id not in groups:
                groups[ch_id] = []
            groups[ch_id].append(post)
        return groups

    def _process_channel(
        self,
        channel: ChannelORM,
        posts: List[ContentORM],
    ) -> Dict[str, Any]:
        """Обрабатывает все посты одного канала."""
        result = {"processed": 0, "success": 0, "failed": 0, "posts": []}

        # Создаём tracker для платформы
        tracker = self._create_tracker(channel)
        if not tracker:
            self.logger.warning(
                f"Could not create tracker for {channel.name} ({channel.platform})"
            )
            return result

        # Обрабатываем каждый пост
        for post in posts:
            try:
                success = self._process_post(tracker, channel, post)
                result["processed"] += 1
                if success:
                    result["success"] += 1
                else:
                    result["failed"] += 1
            except Exception as e:
                self.logger.error(f"Error processing post {post.id}: {e}")
                result["processed"] += 1
                result["failed"] += 1

        return result

    def _create_tracker(self, channel: ChannelORM):
        """Создаёт engagement tracker для канала."""
        if channel.platform == "telegram":
            if not channel.bot_token or not channel.chat_id:
                return None
            return TelegramEngagementTracker(channel.bot_token, channel.chat_id)

        elif channel.platform == "vk":
            if not channel.vk_access_token or not channel.vk_group_id:
                return None
            return VKEngagementTracker(channel.vk_access_token, channel.vk_group_id)

        return None

    def _process_post(
        self,
        tracker,
        channel: ChannelORM,
        post: ContentORM,
    ) -> bool:
        """Обрабатывает один пост: собирает метрики и записывает их."""
        metrics = None

        if channel.platform == "telegram":
            if not post.telegram_message_id:
                self.logger.debug(f"Post {post.id} has no telegram_message_id")
                return False
            metrics = tracker.collect_metrics(int(post.telegram_message_id))

        elif channel.platform == "vk":
            # Пробуем извлечь post_id из source_url
            post_id = self._extract_vk_post_id(post.source_url)
            if post_id:
                metrics = tracker.collect_metrics(post_id)
            else:
                # Для VK с group token собираем только group stats
                # и записываем "общие" метрики канала
                metrics = tracker.collect_metrics()
                # В этом случае записываем только subscribers/имя группы
                metrics = {
                    "platform": "vk",
                    "group_name": metrics.get("group_name"),
                    "members_count": metrics.get("members_count"),
                    "note": "Individual post metrics unavailable with group token",
                }

        if not metrics:
            return False

        # Записываем метрики через AnalyticsEngine
        try:
            self.analytics.record_post_metric(
                content_id=str(post.id),
                channel_id=str(post.channel_id),
                platform=channel.platform,
                views=metrics.get("views") or 0,
                likes=metrics.get("likes") or 0,
                shares=metrics.get("reposts") or metrics.get("forwards") or 0,
                comments=metrics.get("comments") or 0,
                link_clicks=0,
                button_clicks={},
                extra_metadata={
                    "subscribers": metrics.get("subscribers") or metrics.get("members_count"),
                    "channel_title": metrics.get("channel_title") or metrics.get("group_name"),
                    "collected_at": metrics.get("collected_at"),
                    "public_url": metrics.get("public_url"),
                    "note": metrics.get("note"),
                },
            )
            self.logger.debug(f"Recorded metrics for post {post.id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to record metrics for {post.id}: {e}")
            return False

    def _extract_vk_post_id(self, source_url: Optional[str]) -> Optional[str]:
        """Извлекает VK post_id из source_url."""
        if not source_url:
            return None

        # Паттерн: https://vk.com/wall-123_456 или vk.com/wall-123_456
        match = re.search(r'wall(-?\d+_\d+)', source_url)
        if match:
            return match.group(1)

        return None