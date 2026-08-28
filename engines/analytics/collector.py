"""Analytics Collector - Sprint 58.

Собирает метрики по post_history и сохраняет в существующую таблицу post_metrics
через модель core.models.analytics.PostMetric.

Важно:
- НЕ создаём PostMetricsORM
- Используем существующую PostMetric из Sprint 36
- Telegram/VK trackers уже существуют и являются синхронными
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AnalyticsCollector:
    """Сбор метрик + обновление learnings."""

    def __init__(self, db_session):
        self.db = db_session

    async def collect_metrics_for_channel(self, channel_id: str):
        """Собрать метрики за последние 24 часа для всех опубликованных постов канала."""
        from core.models.channel_orm import ChannelORM
        from core.models.post_history_orm import PostHistoryORM
        from core.models.analytics import PostMetric

        channel = self.db.query(ChannelORM).filter_by(id=channel_id).first()
        if not channel:
            logger.warning("AnalyticsCollector: channel not found: %s", channel_id)
            return {"channel_id": channel_id, "posts_checked": 0, "metrics_saved": 0}

        since = datetime.utcnow() - timedelta(hours=24)

        posts = (
            self.db.query(PostHistoryORM)
            .filter_by(channel_id=channel_id)
            .filter(PostHistoryORM.posted_at >= since)
            .all()
        )

        posts_checked = 0
        metrics_saved = 0

        for post in posts:
            posts_checked += 1

            if not post.content_id:
                logger.debug("Skip post_history=%s: no content_id", post.id)
                continue

            if not post.message_id:
                logger.debug("Skip post_history=%s: no message_id", post.id)
                continue

            try:
                raw = self._get_platform_metrics(channel, post)
                if not raw:
                    continue

                normalized = self._normalize_metrics(raw)

                metric = PostMetric(
                    content_id=str(post.content_id),
                    channel_id=str(channel.id),
                    platform=channel.platform or post.platform or "telegram",
                    views_count=normalized.get("views", 0),
                    likes_count=normalized.get("likes", 0),
                    shares_count=normalized.get("shares", 0),
                    comments_count=normalized.get("comments", 0),
                    measured_at=datetime.utcnow(),
                    period_hours=24,
                    extra_metadata={
                        "post_history_id": post.id,
                        "message_id": post.message_id,
                        "raw": raw,
                    },
                )
                self.db.add(metric)
                metrics_saved += 1

            except Exception as e:
                logger.exception("Failed to collect metrics for post_history=%s: %s", post.id, e)

        self.db.commit()

        try:
            await self.update_learnings_for_channel(channel_id)
        except Exception as e:
            logger.exception("Failed to update learnings for channel=%s: %s", channel_id, e)

        logger.info(
            "AnalyticsCollector done: channel=%s checked=%s saved=%s",
            channel_id,
            posts_checked,
            metrics_saved,
        )

        return {
            "channel_id": channel_id,
            "posts_checked": posts_checked,
            "metrics_saved": metrics_saved,
        }

    def _get_platform_metrics(self, channel, post) -> Optional[Dict]:
        """Получить метрики с Telegram/VK."""
        platform = (channel.platform or post.platform or "").lower()

        if platform == "telegram":
            bot_token = getattr(channel, "bot_token", None)
            chat_id = getattr(channel, "chat_id", None)

            if not bot_token or not chat_id:
                logger.debug("Telegram metrics skipped: no bot_token/chat_id for channel=%s", channel.id)
                return None

            from engines.analytics.telegram_tracker import TelegramEngagementTracker

            tracker = TelegramEngagementTracker(bot_token=bot_token, chat_id=chat_id)
            return tracker.get_message_metrics(int(post.message_id))

        if platform == "vk":
            access_token = getattr(channel, "vk_access_token", None)
            group_id = getattr(channel, "vk_group_id", None)

            if not access_token or not group_id:
                logger.debug("VK metrics skipped: no token/group_id for channel=%s", channel.id)
                return None

            from engines.analytics.vk_tracker import VKEngagementTracker

            tracker = VKEngagementTracker(access_token=access_token, group_id=group_id)
            return tracker.get_post_metrics(str(post.message_id))

        logger.debug("Metrics skipped: unsupported platform=%s", platform)
        return None

    def _normalize_metrics(self, raw: Dict) -> Dict:
        """Нормализовать разные форматы tracker-ов."""
        raw = raw or {}

        return {
            "views": (
                raw.get("views")
                or raw.get("views_count")
                or raw.get("impressions")
                or raw.get("reach")
                or 0
            ),
            "likes": (
                raw.get("likes")
                or raw.get("likes_count")
                or raw.get("reactions")
                or 0
            ),
            "shares": (
                raw.get("shares")
                or raw.get("shares_count")
                or raw.get("reposts")
                or raw.get("reposts_count")
                or 0
            ),
            "comments": (
                raw.get("comments")
                or raw.get("comments_count")
                or 0
            ),
        }

    async def update_learnings_for_channel(self, channel_id: str):
        """Анализировать метрики и обновить channel_learnings."""
        from core.models.post_history_orm import PostHistoryORM, ChannelLearningsORM
        from core.models.analytics import PostMetric

        one_month_ago = datetime.utcnow() - timedelta(days=30)

        posts = (
            self.db.query(PostHistoryORM)
            .filter_by(channel_id=channel_id)
            .filter(PostHistoryORM.posted_at >= one_month_ago)
            .all()
        )

        if not posts:
            return

        # Анализ медиа
        self._analyze_media_types(channel_id, posts)

        # Анализ текста
        self._analyze_text_patterns(channel_id, posts)

        self.db.commit()

    def _latest_metric_for_post(self, post):
        from core.models.analytics import PostMetric

        if not post.content_id:
            return None

        return (
            self.db.query(PostMetric)
            .filter_by(content_id=str(post.content_id))
            .order_by(PostMetric.measured_at.desc())
            .first()
        )

    def _get_post_engagement(self, post) -> float:
        metric = self._latest_metric_for_post(post)
        if not metric:
            return 0.0

        return (
            (metric.views_count or 0)
            + (metric.likes_count or 0) * 3
            + (metric.shares_count or 0) * 5
            + (metric.comments_count or 0) * 2
        )

    def _get_avg_engagement(self, posts: list) -> float:
        if not posts:
            return 0.0
        return sum(self._get_post_engagement(p) for p in posts) / len(posts)

    def _upsert_learning(self, channel_id: str, pattern: str, score: float, metadata: dict = None):
        import json
        from core.models.post_history_orm import ChannelLearningsORM

        existing = (
            self.db.query(ChannelLearningsORM)
            .filter_by(channel_id=channel_id, pattern=pattern)
            .first()
        )

        if existing:
            existing.score = float(score)
            existing.evidence_count = (existing.evidence_count or 0) + 1
            existing.last_updated = datetime.utcnow()
            existing.metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
            return existing

        learning = ChannelLearningsORM(
            channel_id=channel_id,
            pattern=pattern,
            score=float(score),
            evidence_count=1,
            last_updated=datetime.utcnow(),
            metadata_json=json.dumps(metadata or {}, ensure_ascii=False),
        )
        self.db.add(learning)
        return learning

    def _analyze_media_types(self, channel_id: str, posts: list):
        video_posts = [p for p in posts if p.media_type == "video"]
        image_posts = [p for p in posts if p.media_type == "image"]

        if not video_posts or not image_posts:
            return

        video_eng = self._get_avg_engagement(video_posts)
        image_eng = self._get_avg_engagement(image_posts)

        if video_eng <= 0 and image_eng <= 0:
            return

        if video_eng > image_eng * 1.3:
            self._upsert_learning(
                channel_id,
                "video_increases_engagement_by_30%",
                min(1.0, video_eng / (image_eng + 1.0)),
                {"video_engagement": video_eng, "image_engagement": image_eng},
            )
        elif image_eng > video_eng * 1.3:
            self._upsert_learning(
                channel_id,
                "image_increases_engagement_by_30%",
                min(1.0, image_eng / (video_eng + 1.0)),
                {"video_engagement": video_eng, "image_engagement": image_eng},
            )
        else:
            self._upsert_learning(
                channel_id,
                "image_content_performs_similarly_to_video",
                0.5,
                {"video_engagement": video_eng, "image_engagement": image_eng},
            )

    def _analyze_text_patterns(self, channel_id: str, posts: list):
        high = [p for p in posts if self._get_post_engagement(p) > 100]
        if not high:
            return

        patterns = {}

        for post in high:
            text = (post.text or "").lower()

            if "как" in text or "how to" in text:
                patterns["how_to_format"] = patterns.get("how_to_format", 0) + 1

            if any(x in text for x in ["```", "def ", "class ", "import "]):
                patterns["code_examples"] = patterns.get("code_examples", 0) + 1

            if len(text) > 500:
                patterns["long_form_content"] = patterns.get("long_form_content", 0) + 1

            if any(x in text for x in ["🔥", "⚡", "🚀"]):
                patterns["strong_emoji_hooks"] = patterns.get("strong_emoji_hooks", 0) + 1

        for pattern, count in patterns.items():
            if count >= 2:
                score = min(1.0, count / len(high))
                self._upsert_learning(
                    channel_id,
                    pattern,
                    score,
                    {"count": count, "high_engagement_posts": len(high)},
                )