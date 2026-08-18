"""Analytics Engine - Sprint 36.

Собирает и анализирует метрики engagement.
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from core.database import SessionLocal
from core.models.analytics import PostMetric, ABTest, ABTestResult
from core.models.content_orm import ContentORM


logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Engine для работы с аналитикой."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def record_post_metric(
        self,
        content_id: str,
        channel_id: str,
        platform: str,
        views: int = 0,
        likes: int = 0,
        shares: int = 0,
        comments: int = 0,
        link_clicks: int = 0,
        button_clicks: Optional[Dict] = None,
        extra_metadata: Optional[Dict] = None,
    ) -> PostMetric:
        """Записывает метрики поста."""
        db = SessionLocal()
        try:
            metric = PostMetric(
                content_id=content_id,
                channel_id=channel_id,
                platform=platform,
                views_count=views,
                likes_count=likes,
                shares_count=shares,
                comments_count=comments,
                link_clicks=link_clicks,
                button_clicks=button_clicks or {},
                extra_metadata=extra_metadata or {},
            )
            db.add(metric)
            db.commit()
            db.refresh(metric)
            db.expunge(metric)  # detach от сессии, но с загруженными атрибутами
            self.logger.info(f"Recorded metric for {content_id}: views={views}")
            return metric
        finally:
            db.close()
    
    def get_post_metrics(
        self,
        content_id: str,
        hours: int = 24,
    ) -> List[PostMetric]:
        """Получает метрики поста за период."""
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            metrics = db.query(PostMetric).filter(
                PostMetric.content_id == content_id,
                PostMetric.measured_at >= cutoff,
            ).order_by(desc(PostMetric.measured_at)).all()
            
            return metrics
        finally:
            db.close()
    
    def get_channel_analytics(
        self,
        channel_id: str,
        days: int = 7,
    ) -> Dict:
        """Получает аналитику канала за период."""
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            # Aggregate metrics
            result = db.query(
                func.count(PostMetric.id).label("total_posts"),
                func.sum(PostMetric.views_count).label("total_views"),
                func.sum(PostMetric.likes_count).label("total_likes"),
                func.sum(PostMetric.shares_count).label("total_shares"),
                func.sum(PostMetric.comments_count).label("total_comments"),
                func.avg(PostMetric.views_count).label("avg_views"),
                func.avg(PostMetric.likes_count).label("avg_likes"),
            ).filter(
                PostMetric.channel_id == channel_id,
                PostMetric.measured_at >= cutoff,
            ).first()
            
            return {
                "channel_id": channel_id,
                "period_days": days,
                "total_posts": result.total_posts or 0,
                "total_views": result.total_views or 0,
                "total_likes": result.total_likes or 0,
                "total_shares": result.total_shares or 0,
                "total_comments": result.total_comments or 0,
                "avg_views": round(float(result.avg_views or 0), 2),
                "avg_likes": round(float(result.avg_likes or 0), 2),
                "engagement_rate": round(
                    (result.total_likes or 0) / (result.total_views or 1) * 100, 2
                ),
            }
        finally:
            db.close()
    
    def get_top_posts(
        self,
        channel_id: str,
        days: int = 7,
        limit: int = 10,
        metric: str = "views",
    ) -> List[Dict]:
        """Получает топ постов по метрике."""
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            # Map metric name to column
            metric_column = {
                "views": PostMetric.views_count,
                "likes": PostMetric.likes_count,
                "shares": PostMetric.shares_count,
                "comments": PostMetric.comments_count,
            }.get(metric, PostMetric.views_count)
            
            # Query top posts
            results = db.query(
                PostMetric.content_id,
                func.sum(metric_column).label("metric_value"),
            ).filter(
                PostMetric.channel_id == channel_id,
                PostMetric.measured_at >= cutoff,
            ).group_by(
                PostMetric.content_id
            ).order_by(
                desc("metric_value")
            ).limit(limit).all()
            
            # Enrich with content info
            top_posts = []
            for result in results:
                content = db.query(ContentORM).filter(
                    ContentORM.id == result.content_id
                ).first()
                
                if content:
                    top_posts.append({
                        "content_id": result.content_id,
                        "headline": content.headline[:60],
                        "metric_value": result.metric_value,
                        "status": content.status,
                        "created_at": content.created_at.isoformat(),
                    })
            
            return top_posts
        finally:
            db.close()