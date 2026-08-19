"""Feedback Loop - Sprint 45.

Замыкает контур: метрики → оптимизация → следующий research.
Запускается каждые 6 часов (interval_hours).
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List

from sqlalchemy import func

from core.database import SessionLocal
from core.models.analytics import PostMetric
from core.models.channel_orm import ChannelORM
from engines.content_optimization.auto_apply import OptimizationApplier


logger = logging.getLogger(__name__)


class FeedbackLoop:
    """Замкнутый контур: метрики → оптимизация → research."""
    
    def __init__(self):
        self.applier = OptimizationApplier()
    
    def get_active_channels(self) -> List[str]:
        """Возвращает ID активных каналов (UUID)."""
        db = SessionLocal()
        try:
            channels = db.query(ChannelORM).all()
            return [ch.id for ch in channels]
        finally:
            db.close()
    
    def run_optimization_cycle(self) -> Dict:
        """Запускает один цикл оптимизации для всех каналов."""
        channels = self.get_active_channels()
        results = {}
        
        logger.info(f"Starting optimization cycle for {len(channels)} channels")
        
        for channel_id in channels:
            try:
                result = self.applier.run_full_optimization(channel_id)
                results[channel_id] = result
            except Exception as e:
                logger.error(f"Failed to optimize channel {channel_id}: {e}")
                results[channel_id] = {"error": str(e)}
        
        return results
    
    def get_feedback_stats(self) -> Dict:
        """Статистика feedback loop."""
        db = SessionLocal()
        try:
            total_posts = db.query(func.count(PostMetric.id)).scalar() or 0
            posts_with_engagement = db.query(func.count(PostMetric.id)).filter(
                PostMetric.views_count > 0
            ).scalar() or 0
            
            total_views = db.query(func.sum(PostMetric.views_count)).scalar() or 0
            total_likes = db.query(func.sum(PostMetric.likes_count)).scalar() or 0
            
            return {
                "total_metrics": total_posts,
                "posts_with_views": posts_with_engagement,
                "engagement_rate": posts_with_engagement / total_posts if total_posts > 0 else 0,
                "total_views": total_views,
                "total_likes": total_likes,
                "last_run": datetime.utcnow().isoformat(),
            }
        finally:
            db.close()


_feedback_loop = FeedbackLoop()


async def start_feedback_loop(interval_hours: int = 6):
    """Фоновая задача: оптимизация каждые interval_hours."""
    interval_sec = interval_hours * 3600
    logger.info(f"Feedback loop started (interval={interval_hours}h)")
    
    while True:
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, _feedback_loop.run_optimization_cycle
            )
        except Exception as e:
            logger.error(f"feedback loop error: {e}")
        await asyncio.sleep(interval_sec)