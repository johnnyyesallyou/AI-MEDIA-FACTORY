"""Posting Time Optimizer - Sprint 39.

Определение оптимального времени публикации на основе engagement данных.
- Анализ engagement по часам
- Рекомендации оптимального времени
- Интеграция с ChannelScheduler
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy import func, extract

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.analytics import PostMetric


logger = logging.getLogger(__name__)


class PostingTimeOptimizer:
    """Оптимизация времени публикации."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def analyze_engagement_by_hour(
        self,
        channel_id: Optional[str] = None,
        days: int = 30,
    ) -> Dict[int, Dict]:
        """Анализирует engagement по часам суток."""
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            query = db.query(
                extract('hour', ContentORM.published_at).label('hour'),
                func.count(ContentORM.id).label('post_count'),
                func.sum(PostMetric.views_count).label('total_views'),
                func.avg(PostMetric.views_count).label('avg_views'),
            ).join(
                PostMetric, PostMetric.content_id == ContentORM.id
            ).filter(
                ContentORM.status == "published",
                ContentORM.published_at >= cutoff,
                PostMetric.measured_at >= cutoff,
            )

            if channel_id:
                query = query.filter(ContentORM.channel_id == channel_id)

            results = query.group_by(
                extract('hour', ContentORM.published_at)
            ).all()

            hourly_stats = {}
            for row in results:
                hour = int(row.hour)
                hourly_stats[hour] = {
                    "post_count": row.post_count or 0,
                    "total_views": row.total_views or 0,
                    "avg_views": round(float(row.avg_views or 0), 2),
                }

            return hourly_stats

        finally:
            db.close()

    def get_best_posting_times(
        self,
        channel_id: Optional[str] = None,
        days: int = 30,
        top_n: int = 3,
    ) -> List[Dict]:
        """Возвращает топ N лучших часов для публикации."""
        hourly = self.analyze_engagement_by_hour(channel_id, days)

        # Сортируем по avg_views
        sorted_hours = sorted(
            hourly.items(),
            key=lambda x: x[1]["avg_views"],
            reverse=True
        )

        best_times = []
        for hour, stats in sorted_hours[:top_n]:
            best_times.append({
                "hour": hour,
                "time_str": f"{hour:02d}:00",
                "avg_views": stats["avg_views"],
                "post_count": stats["post_count"],
            })

        return best_times

    def suggest_posting_time(
        self,
        channel_id: Optional[str] = None,
        days: int = 30,
    ) -> Dict:
        """Предлагает оптимальное время публикации."""
        best_times = self.get_best_posting_times(channel_id, days, top_n=3)
        hourly = self.analyze_engagement_by_hour(channel_id, days)

        if not best_times:
            # Fallback: стандартные peak hours
            return {
                "best_time": "10:00",
                "reason": "Нет данных, используем стандартное время",
                "alternatives": ["18:00", "20:00"],
            }

        return {
            "best_time": best_times[0]["time_str"],
            "avg_views": best_times[0]["avg_views"],
            "reason": f"Лучший engagement в {best_times[0]['time_str']}",
            "alternatives": [t["time_str"] for t in best_times[1:]],
            "hourly_stats": hourly,
        }