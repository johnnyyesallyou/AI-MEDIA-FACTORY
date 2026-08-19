"""Headline Optimizer - Sprint 39.

Оптимизация заголовков на основе успешных постов.
- Анализ топ заголовков (из PostMetric)
- Генерация вариаций (LLM-based)
- Рекомендации по улучшению
"""
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from sqlalchemy import func, desc

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.analytics import PostMetric


logger = logging.getLogger(__name__)


class HeadlineOptimizer:
    """Оптимизация заголовков."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def analyze_top_headlines(
        self,
        channel_id: Optional[str] = None,
        days: int = 30,
        limit: int = 20,
        metric: str = "views",
    ) -> List[Dict]:
        """Анализирует топ заголовки по engagement."""
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            metric_col = {
                "views": PostMetric.views_count,
                "likes": PostMetric.likes_count,
            }.get(metric, PostMetric.views_count)

            query = db.query(
                ContentORM.id,
                ContentORM.headline,
                func.sum(metric_col).label("metric_value"),
            ).join(
                PostMetric, PostMetric.content_id == ContentORM.id
            ).filter(
                ContentORM.status == "published",
                PostMetric.measured_at >= cutoff,
            )

            if channel_id:
                query = query.filter(ContentORM.channel_id == channel_id)

            results = query.group_by(
                ContentORM.id, ContentORM.headline
            ).order_by(
                desc("metric_value")
            ).limit(limit).all()

            headlines = []
            for row in results:
                headlines.append({
                    "content_id": row.id,
                    "headline": row.headline,
                    "metric_value": row.metric_value or 0,
                    "char_count": len(row.headline),
                    "word_count": len(row.headline.split()),
                })

            return headlines

        finally:
            db.close()

    def generate_variations(
        self,
        headline: str,
        platform: str = "telegram",
    ) -> List[Dict]:
        """Генерирует вариации заголовка (placeholder для LLM)."""
        variations = []

        # Базовые вариации
        base = headline.replace("📰", "").replace("🎬", "").replace("📚", "").strip()

        # Emoji variations
        variations.append({
            "headline": f"📰 {base}",
            "strategy": "emoji_prefix",
        })
        variations.append({
            "headline": f"🔥 {base}",
            "strategy": "emoji_fire",
        })

        # Length variations
        if len(base) > 60:
            short = base[:57] + "..."
            variations.append({
                "headline": f"📰 {short}",
                "strategy": "shortened",
            })

        # Platform-specific
        if platform == "telegram":
            variations.append({
                "headline": f"**{base}**",
                "strategy": "bold_markdown",
            })

        return variations

    def suggest_improvements(self, headline: str) -> List[str]:
        """Предлагает улучшения для заголовка."""
        suggestions = []

        # Length check
        if len(headline) > 100:
            suggestions.append("Заголовок слишком длинный (>100 символов)")
        elif len(headline) < 20:
            suggestions.append("Заголовок слишком короткий (<20 символов)")

        # Emoji check
        if not any(c in headline for c in ["📰", "🎬", "📚", "🔥", "⚡", "💡"]):
            suggestions.append("Добавьте emoji для привлечения внимания")

        # Question mark (engagement booster)
        if "?" not in headline and len(headline) < 60:
            suggestions.append("Попробуйте вопросительную форму для engagement")

        # Numbers (listicles work well)
        if not re.search(r'\d+', headline):
            suggestions.append("Числа в заголовке повышают CTR (например: '5 причин...')")

        return suggestions

    def optimize(
        self,
        headline: str,
        channel_id: Optional[str] = None,
        platform: str = "telegram",
    ) -> Dict:
        """Полная оптимизация заголовка."""
        return {
            "original": headline,
            "suggestions": self.suggest_improvements(headline),
            "variations": self.generate_variations(headline, platform),
            "top_examples": self.analyze_top_headlines(channel_id, limit=5),
        }