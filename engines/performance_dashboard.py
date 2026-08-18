"""Performance Dashboard - Sprint 36.4.

CLI отчёты по эффективности каналов:
- Общая статистика по всем каналам
- Детальная статистика по конкретному каналу
- Топ постов по engagement
- Сравнение каналов
- Тренды во времени
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from core.models.analytics import PostMetric


logger = logging.getLogger(__name__)


class PerformanceDashboard:
    """Dashboard для анализа эффективности каналов."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def overview(self, days: int = 7) -> Dict[str, Any]:
        """
        Общая статистика по всем каналам.

        Returns:
            Dict с общей статистикой
        """
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            # Общая статистика
            total_posts = db.query(ContentORM).filter(
                ContentORM.status == "published",
                ContentORM.published_at >= cutoff,
            ).count()

            # Метрики
            metrics_agg = db.query(
                func.sum(PostMetric.views_count).label("total_views"),
                func.sum(PostMetric.likes_count).label("total_likes"),
                func.sum(PostMetric.shares_count).label("total_shares"),
                func.sum(PostMetric.comments_count).label("total_comments"),
                func.avg(PostMetric.views_count).label("avg_views"),
                func.count(PostMetric.id).label("metrics_count"),
            ).filter(
                PostMetric.measured_at >= cutoff,
            ).first()

            # По платформам
            platform_stats = db.query(
                PostMetric.platform,
                func.count(PostMetric.id).label("count"),
                func.sum(PostMetric.views_count).label("views"),
            ).filter(
                PostMetric.measured_at >= cutoff,
            ).group_by(PostMetric.platform).all()

            # По каналам
            channel_stats = db.query(
                ChannelORM.name,
                func.count(ContentORM.id).label("posts"),
            ).join(
                ContentORM, ContentORM.channel_id == ChannelORM.id
            ).filter(
                ContentORM.status == "published",
                ContentORM.published_at >= cutoff,
            ).group_by(ChannelORM.name).all()

            return {
                "period_days": days,
                "total_posts": total_posts,
                "total_views": metrics_agg.total_views or 0,
                "total_likes": metrics_agg.total_likes or 0,
                "total_shares": metrics_agg.total_shares or 0,
                "total_comments": metrics_agg.total_comments or 0,
                "avg_views": round(float(metrics_agg.avg_views or 0), 2),
                "metrics_count": metrics_agg.metrics_count or 0,
                "by_platform": {
                    row.platform: {"count": row.count, "views": row.views or 0}
                    for row in platform_stats
                },
                "by_channel": {
                    row.name: {"posts": row.posts}
                    for row in channel_stats
                },
            }
        finally:
            db.close()

    def channel_details(
        self,
        channel_name: str,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Детальная статистика по конкретному каналу.

        Args:
            channel_name: Название канала
            days: Период в днях
        """
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            # Находим канал
            channel = db.query(ChannelORM).filter(
                ChannelORM.name == channel_name
            ).first()

            if not channel:
                return {"error": f"Channel '{channel_name}' not found"}

            # Посты канала
            posts = db.query(ContentORM).filter(
                ContentORM.channel_id == channel.id,
                ContentORM.status == "published",
                ContentORM.published_at >= cutoff,
            ).all()

            # Метрики для этих постов
            post_ids = [p.id for p in posts]
            if not post_ids:
                return {
                    "channel": channel_name,
                    "period_days": days,
                    "posts": 0,
                    "message": "No published posts in this period",
                }

            metrics = db.query(PostMetric).filter(
                PostMetric.content_id.in_(post_ids),
            ).all()

            # Агрегация
            total_views = sum(m.views_count for m in metrics)
            total_likes = sum(m.likes_count for m in metrics)
            total_shares = sum(m.shares_count for m in metrics)
            total_comments = sum(m.comments_count for m in metrics)
            avg_views = total_views / len(metrics) if metrics else 0

            # Подписчики (последнее значение)
            subscribers = None
            if metrics:
                last_metric = max(metrics, key=lambda m: m.measured_at)
                subscribers = last_metric.extra_metadata.get("subscribers") if last_metric.extra_metadata else None

            return {
                "channel": channel_name,
                "platform": channel.platform,
                "period_days": days,
                "posts": len(posts),
                "metrics_count": len(metrics),
                "total_views": total_views,
                "total_likes": total_likes,
                "total_shares": total_shares,
                "total_comments": total_comments,
                "avg_views": round(avg_views, 2),
                "subscribers": subscribers,
                "engagement_rate": round(
                    (total_likes + total_comments) / (total_views or 1) * 100, 2
                ),
            }
        finally:
            db.close()

    def top_posts(
        self,
        channel_name: Optional[str] = None,
        days: int = 7,
        limit: int = 10,
        metric: str = "views",
    ) -> List[Dict[str, Any]]:
        """
        Топ постов по метрике.

        Args:
            channel_name: Фильтр по каналу (None = все)
            days: Период в днях
            limit: Количество постов
            metric: Метрика для сортировки (views, likes, shares, comments)
        """
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            # Базовый query
            query = db.query(
                PostMetric.content_id,
                func.sum(PostMetric.views_count).label("views"),
                func.sum(PostMetric.likes_count).label("likes"),
                func.sum(PostMetric.shares_count).label("shares"),
                func.sum(PostMetric.comments_count).label("comments"),
            ).filter(
                PostMetric.measured_at >= cutoff,
            )

            # Фильтр по каналу
            if channel_name:
                channel = db.query(ChannelORM).filter(
                    ChannelORM.name == channel_name
                ).first()
                if channel:
                    post_ids = [
                        p.id for p in db.query(ContentORM).filter(
                            ContentORM.channel_id == channel.id
                        ).all()
                    ]
                    query = query.filter(PostMetric.content_id.in_(post_ids))

            # Группировка и сортировка
            results = query.group_by(
                PostMetric.content_id
            ).order_by(
                desc(metric)
            ).limit(limit).all()

            # Enrich с информацией о постах
            top_posts = []
            for row in results:
                post = db.query(ContentORM).filter(
                    ContentORM.id == row.content_id
                ).first()

                if post:
                    channel = db.query(ChannelORM).filter(
                        ChannelORM.id == post.channel_id
                    ).first()

                    top_posts.append({
                        "content_id": row.content_id,
                        "headline": post.headline[:80],
                        "channel": channel.name if channel else "Unknown",
                        "platform": channel.platform if channel else "Unknown",
                        "views": row.views or 0,
                        "likes": row.likes or 0,
                        "shares": row.shares or 0,
                        "comments": row.comments or 0,
                        "published_at": post.published_at.isoformat() if post.published_at else None,
                    })

            return top_posts
        finally:
            db.close()

    def compare_channels(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Сравнение эффективности каналов.

        Returns:
            List словарей с метриками для каждого канала
        """
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            channels = db.query(ChannelORM).all()
            comparison = []

            for channel in channels:
                # Посты канала
                posts = db.query(ContentORM).filter(
                    ContentORM.channel_id == channel.id,
                    ContentORM.status == "published",
                    ContentORM.published_at >= cutoff,
                ).all()

                if not posts:
                    continue

                post_ids = [p.id for p in posts]

                # Метрики
                metrics_agg = db.query(
                    func.sum(PostMetric.views_count).label("views"),
                    func.sum(PostMetric.likes_count).label("likes"),
                    func.avg(PostMetric.views_count).label("avg_views"),
                ).filter(
                    PostMetric.content_id.in_(post_ids),
                ).first()

                comparison.append({
                    "channel": channel.name,
                    "platform": channel.platform,
                    "posts": len(posts),
                    "total_views": metrics_agg.views or 0,
                    "total_likes": metrics_agg.likes or 0,
                    "avg_views": round(float(metrics_agg.avg_views or 0), 2),
                    "engagement_rate": round(
                        (metrics_agg.likes or 0) / (metrics_agg.views or 1) * 100, 2
                    ),
                })

            # Сортировка по total_views
            comparison.sort(key=lambda x: x["total_views"], reverse=True)

            return comparison
        finally:
            db.close()

    def generate_report(self, days: int = 7) -> str:
        """
        Генерирует текстовый отчёт.

        Returns:
            Форматированный текстовый отчёт
        """
        overview = self.overview(days)
        comparison = self.compare_channels(days)
        top = self.top_posts(days=days, limit=5, metric="views")

        lines = []
        lines.append("=" * 70)
        lines.append(f"PERFORMANCE REPORT (last {days} days)")
        lines.append("=" * 70)

        # Overview
        lines.append(f"\n📊 OVERVIEW:")
        lines.append(f"  Total posts: {overview['total_posts']}")
        lines.append(f"  Total views: {overview['total_views']:,}")
        lines.append(f"  Total likes: {overview['total_likes']:,}")
        lines.append(f"  Avg views per post: {overview['avg_views']:.1f}")

        # By platform
        lines.append(f"\n📱 BY PLATFORM:")
        for platform, stats in overview["by_platform"].items():
            lines.append(f"  {platform}: {stats['count']} metrics, {stats['views']:,} views")

        # Channel comparison
        lines.append(f"\n📈 CHANNEL COMPARISON:")
        for ch in comparison:
            lines.append(f"  {ch['channel']} ({ch['platform']}):")
            lines.append(f"    Posts: {ch['posts']}, Views: {ch['total_views']:,}, Avg: {ch['avg_views']:.1f}")

        # Top posts
        lines.append(f"\n🏆 TOP 5 POSTS (by views):")
        for i, post in enumerate(top, 1):
            lines.append(f"  {i}. {post['headline'][:50]}...")
            lines.append(f"     {post['channel']} | 👁 {post['views']:,} | ❤️ {post['likes']}")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)