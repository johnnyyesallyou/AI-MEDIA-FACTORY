"""Analytics Collector - Sprint 57.

Собирает метрики с платформ и обновляет learnings.
Запускается каждый час через APScheduler.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class AnalyticsCollector:
    """
    Собирает метрики с платформ и обновляет learnings.
    """
    
    def __init__(self, db_session, telegram_tracker=None, vk_tracker=None):
        self.db = db_session
        self.telegram_tracker = telegram_tracker
        self.vk_tracker = vk_tracker
    
    async def collect_metrics_for_channel(self, channel_id: str):
        """
        Собрать метрики за последние 24 часа для всех постов канала.
        """
        from core.models.channel_orm import ChannelORM
        from core.models.post_history_orm import PostHistoryORM, PostMetricsORM
        
        channel = self.db.query(ChannelORM).filter_by(id=channel_id).first()
        if not channel:
            logger.warning(f"Channel {channel_id} not found")
            return
        
        # Получить посты за последние 24 часа
        posts = self.db.query(PostHistoryORM)\
            .filter_by(channel_id=channel_id)\
            .filter(PostHistoryORM.posted_at > (datetime.utcnow() - timedelta(hours=24)))\
            .all()
        
        logger.info(f"Collecting metrics for {len(posts)} posts in channel {channel.name}")
        
        for post in posts:
            try:
                metrics = await self._get_platform_metrics(channel, post)
                if metrics:
                    # Сохранить в БД
                    pm = PostMetricsORM(
                        post_id=post.id,
                        platform=channel.platform,
                        views=metrics.get("views", 0),
                        likes=metrics.get("likes", 0),
                        shares=metrics.get("shares", 0),
                        reposts=metrics.get("reposts", 0),
                        comments=metrics.get("comments", 0),
                        engagement_rate=metrics.get("engagement_rate", 0.0)
                    )
                    self.db.add(pm)
            except Exception as e:
                logger.error(f"Error collecting metrics for post {post.id}: {e}")
        
        self.db.commit()
        
        # Обновить learnings после сбора метрик
        await self.update_learnings_for_channel(channel_id)
    
    async def _get_platform_metrics(self, channel, post) -> Optional[Dict]:
        """Получить метрики с конкретной платформы"""
        # Для MVP: возвращаем mock данные (позже интегрируем реальные API)
        if not post.message_id:
            return None
        
        # TODO: Интегрировать реальные platform trackers
        # if channel.platform == "telegram" and self.telegram_tracker:
        #     metrics = await self.telegram_tracker.get_message_metrics(...)
        # elif channel.platform == "vk" and self.vk_tracker:
        #     metrics = await self.vk_tracker.get_post_metrics(...)
        
        # Mock данные для тестирования
        import random
        return {
            "views": random.randint(10, 500),
            "likes": random.randint(1, 50),
            "shares": random.randint(0, 10),
            "reposts": random.randint(0, 5),
            "comments": random.randint(0, 20),
            "engagement_rate": random.uniform(0.01, 0.15)
        }
    
    async def update_learnings_for_channel(self, channel_id: str):
        """
        Анализировать метрики и обновить learnings.
        """
        from core.models.post_history_orm import PostHistoryORM, PostMetricsORM, ChannelLearningsORM
        
        # Получить все посты с метриками за последний месяц
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        posts = self.db.query(PostHistoryORM)\
            .filter_by(channel_id=channel_id)\
            .filter(PostHistoryORM.posted_at > one_month_ago)\
            .all()
        
        if not posts:
            return
        
        # Анализировать медиа типы
        self._analyze_media_types(channel_id, posts)
        
        # Анализировать текстовые паттерны
        self._analyze_text_patterns(channel_id, posts)
        
        self.db.commit()
    
    def _analyze_media_types(self, channel_id: str, posts: list):
        """Анализировать какой тип медиа работает лучше"""
        from core.models.post_history_orm import ChannelLearningsORM, PostMetricsORM
        
        video_posts = [p for p in posts if p.media_type == "video" and p.video_url]
        image_posts = [p for p in posts if p.media_type == "image" and p.image_url]
        
        if video_posts and image_posts:
            # Сравнить среднее engagement
            video_engagement = self._get_avg_engagement(video_posts)
            image_engagement = self._get_avg_engagement(image_posts)
            
            if video_engagement > image_engagement * 1.3:
                # Видео работает на 30%+ лучше
                pattern = "video_increases_engagement_by_30%"
                score = min(1.0, video_engagement / (image_engagement + 0.1))
            else:
                pattern = "image_content_performs_similarly_to_video"
                score = 0.5
            
            # Сохранить или обновить learning
            from core.models.post_history_orm import ChannelLearningsORM
            existing = self.db.query(ChannelLearningsORM)\
                .filter_by(channel_id=channel_id, pattern=pattern)\
                .first()
            
            if existing:
                existing.score = score
                existing.evidence_count += 1
                existing.last_updated = datetime.utcnow()
            else:
                learning = ChannelLearningsORM(
                    channel_id=channel_id,
                    pattern=pattern,
                    score=score,
                    evidence_count=1
                )
                self.db.add(learning)
    
    def _analyze_text_patterns(self, channel_id: str, posts: list):
        """Анализировать какие текстовые паттерны работают"""
        from core.models.post_history_orm import ChannelLearningsORM
        
        # Посты с высоким engagement
        high_engagement_posts = [
            p for p in posts
            if self._get_post_engagement(p) > 100
        ]
        
        if not high_engagement_posts:
            return
        
        # Искать общие паттерны в тексте
        patterns_found = {}
        for post in high_engagement_posts:
            text_lower = (post.text or "").lower()
            
            # Примеры паттернов
            if "как" in text_lower or "how to" in text_lower:
                patterns_found["how_to_format"] = patterns_found.get("how_to_format", 0) + 1
            if any(code in text_lower for code in ["```", "def ", "class ", "import "]):
                patterns_found["code_examples"] = patterns_found.get("code_examples", 0) + 1
            if len(post.text or "") > 500:
                patterns_found["long_form_content"] = patterns_found.get("long_form_content", 0) + 1
        
        # Сохранить найденные паттерны
        for pattern, count in patterns_found.items():
            if count >= 2:  # Только если встречается несколько раз
                score = min(1.0, count / len(high_engagement_posts))
                
                existing = self.db.query(ChannelLearningsORM)\
                    .filter_by(channel_id=channel_id, pattern=pattern)\
                    .first()
                
                if existing:
                    existing.score = score
                    existing.evidence_count += 1
                    existing.last_updated = datetime.utcnow()
                else:
                    learning = ChannelLearningsORM(
                        channel_id=channel_id,
                        pattern=pattern,
                        score=score,
                        evidence_count=1
                    )
                    self.db.add(learning)
    
    def _get_avg_engagement(self, posts: list) -> float:
        """Получить среднее engagement для группы постов"""
        total = sum(self._get_post_engagement(p) for p in posts)
        return total / len(posts) if posts else 0
    
    def _get_post_engagement(self, post) -> float:
        """Получить метрику engagement для поста"""
        from core.models.post_history_orm import PostMetricsORM
        
        latest_metric = self.db.query(PostMetricsORM)\
            .filter_by(post_id=post.id)\
            .order_by(PostMetricsORM.collected_at.desc())\
            .first()
        
        if not latest_metric:
            return 0
        
        # Engagement = views + likes*3 + shares*5
        return latest_metric.views + (latest_metric.likes * 3) + (latest_metric.shares * 5)