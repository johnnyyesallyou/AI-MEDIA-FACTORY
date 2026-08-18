"""Automated Insights - Sprint 36.5.

LLM-powered анализ эффективности контента:
- Анализ engagement patterns
- Рекомендации по улучшению
- Выявление лучших практик
- Сравнение производительности
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from engines.performance_dashboard import PerformanceDashboard


logger = logging.getLogger(__name__)


class AutomatedInsights:
    """Генератор автоматических рекомендаций."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.dashboard = PerformanceDashboard()

    def analyze(self, days: int = 7) -> Dict[str, Any]:
        """
        Анализирует данные и генерирует рекомендации.

        Returns:
            Dict с анализом и рекомендациями
        """
        self.logger.info(f"Analyzing data for last {days} days")

        # Собираем данные
        overview = self.dashboard.overview(days)
        comparison = self.dashboard.compare_channels(days)
        top_posts = self.dashboard.top_posts(days=days, limit=10, metric="views")

        # Генерируем инсайты
        insights = []

        # 1. Анализ общей эффективности
        insights.extend(self._analyze_overall(overview))

        # 2. Сравнение каналов
        insights.extend(self._analyze_channels(comparison))

        # 3. Анализ топ постов
        insights.extend(self._analyze_top_posts(top_posts))

        # 4. Рекомендации
        recommendations = self._generate_recommendations(overview, comparison, top_posts)

        return {
            "period_days": days,
            "analyzed_at": datetime.utcnow().isoformat(),
            "data_summary": {
                "total_posts": overview["total_posts"],
                "total_views": overview["total_views"],
                "total_likes": overview["total_likes"],
                "channels_count": len(comparison),
            },
            "insights": insights,
            "recommendations": recommendations,
        }

    def _analyze_overall(self, overview: Dict) -> List[Dict[str, str]]:
        """Анализирует общую статистику."""
        insights = []

        total_posts = overview["total_posts"]
        total_views = overview["total_views"]
        avg_views = overview["avg_views"]

        if total_posts == 0:
            insights.append({
                "type": "warning",
                "category": "activity",
                "message": "Нет опубликованных постов за выбранный период",
                "severity": "high",
            })
            return insights

        # Engagement rate
        engagement_rate = (overview["total_likes"] / total_views * 100) if total_views > 0 else 0

        if avg_views < 10:
            insights.append({
                "type": "warning",
                "category": "reach",
                "message": f"Низкий средний охват: {avg_views:.1f} просмотров на пост",
                "severity": "medium",
                "detail": "Рассмотрите изменение времени публикации или формата контента",
            })
        elif avg_views > 100:
            insights.append({
                "type": "success",
                "category": "reach",
                "message": f"Хороший средний охват: {avg_views:.1f} просмотров на пост",
                "severity": "low",
            })

        if engagement_rate < 1:
            insights.append({
                "type": "warning",
                "category": "engagement",
                "message": f"Низкий engagement rate: {engagement_rate:.2f}%",
                "severity": "medium",
                "detail": "Попробуйте более интерактивный контент (опросы, вопросы)",
            })
        elif engagement_rate > 5:
            insights.append({
                "type": "success",
                "category": "engagement",
                "message": f"Высокий engagement rate: {engagement_rate:.2f}%",
                "severity": "low",
            })

        return insights

    def _analyze_channels(self, comparison: List[Dict]) -> List[Dict[str, str]]:
        """Анализирует производительность каналов."""
        insights = []

        if len(comparison) < 2:
            return insights

        # Находим лучший и худший канал
        best = max(comparison, key=lambda x: x["total_views"])
        worst = min(comparison, key=lambda x: x["total_views"])

        if best["total_views"] > 0 and worst["total_views"] == 0:
            insights.append({
                "type": "info",
                "category": "channels",
                "message": f"Канал '{worst['channel']}' не получает просмотров",
                "severity": "medium",
                "detail": f"Лучший канал: '{best['channel']}' с {best['total_views']} просмотров",
            })

        # Сравнение engagement
        best_engagement = max(comparison, key=lambda x: x.get("engagement_rate", 0))
        if best_engagement.get("engagement_rate", 0) > 3:
            insights.append({
                "type": "success",
                "category": "channels",
                "message": f"Канал '{best_engagement['channel']}' показывает высокий engagement ({best_engagement['engagement_rate']:.2f}%)",
                "severity": "low",
            })

        return insights

    def _analyze_top_posts(self, top_posts: List[Dict]) -> List[Dict[str, str]]:
        """Анализирует топ постов."""
        insights = []

        if not top_posts:
            return insights

        # Анализируем паттерны в топ постах
        top_3 = top_posts[:3]
        avg_top_views = sum(p["views"] for p in top_3) / len(top_3)

        if avg_top_views > 50:
            insights.append({
                "type": "success",
                "category": "content",
                "message": f"Топ-3 поста в среднем получают {avg_top_views:.0f} просмотров",
                "severity": "low",
                "detail": "Анализируйте что делает эти посты успешными",
            })

        # Проверяем diversity каналов в топе
        channels_in_top = set(p["channel"] for p in top_3)
        if len(channels_in_top) == 1:
            channel_name = list(channels_in_top)[0]
            insights.append({
                "type": "info",
                "category": "content",
                "message": f"Все топ-3 поста из одного канала: '{channel_name}'",
                "severity": "low",
                "detail": "Другие каналы могут требовать оптимизации",
            })

        return insights

    def _generate_recommendations(
        self,
        overview: Dict,
        comparison: List[Dict],
        top_posts: List[Dict],
    ) -> List[Dict[str, str]]:
        """Генерирует конкретные рекомендации."""
        recommendations = []

        # 1. Рекомендация по частоте публикаций
        total_posts = overview["total_posts"]
        days = overview["period_days"]
        posts_per_day = total_posts / days if days > 0 else 0

        if posts_per_day < 1:
            recommendations.append({
                "priority": "medium",
                "category": "frequency",
                "action": "Увеличить частоту публикаций",
                "reason": f"Текущая частота: {posts_per_day:.1f} постов/день (рекомендуется: 1-3)",
            })
        elif posts_per_day > 5:
            recommendations.append({
                "priority": "low",
                "category": "frequency",
                "action": "Рассмотреть снижение частоты публикаций",
                "reason": f"Текущая частота: {posts_per_day:.1f} постов/день (может приводить к fatigue)",
            })

        # 2. Рекомендация по engagement
        engagement_rate = (overview["total_likes"] / overview["total_views"] * 100) if overview["total_views"] > 0 else 0

        if engagement_rate < 2:
            recommendations.append({
                "priority": "high",
                "category": "engagement",
                "action": "Улучшить engagement контент",
                "reason": f"Текущий engagement rate: {engagement_rate:.2f}% (цель: >3%)",
                "tactics": [
                    "Добавлять вопросы в конце постов",
                    "Использовать опросы и голосования",
                    "Публиковать в оптимальное время (10:00-12:00, 18:00-20:00)",
                ],
            })

        # 3. Рекомендация по охвату
        if overview["avg_views"] < 50:
            recommendations.append({
                "priority": "medium",
                "category": "reach",
                "action": "Увеличить охват постов",
                "reason": f"Средний охват: {overview['avg_views']:.1f} просмотров",
                "tactics": [
                    "Оптимизировать заголовки (более цепляющие)",
                    "Использовать релевантные хэштеги",
                    "Публиковать в пиковые часы активности",
                ],
            })

        # 4. Рекомендация по каналам
        low_performing = [ch for ch in comparison if ch["total_views"] == 0]
        if low_performing:
            channel_names = [ch["channel"] for ch in low_performing]
            recommendations.append({
                "priority": "medium",
                "category": "channels",
                "action": "Оптимизировать низкопроизводительные каналы",
                "reason": f"Каналы без просмотров: {', '.join(channel_names)}",
                "tactics": [
                    "Проверить настройки каналов",
                    "Адаптировать контент под аудиторию канала",
                    "Рассмотреть cross-promotion между каналами",
                ],
            })

        return recommendations

    def generate_report(self, days: int = 7) -> str:
        """
        Генерирует текстовый отчёт с инсайтами.

        Returns:
            Форматированный текстовый отчёт
        """
        analysis = self.analyze(days)

        lines = []
        lines.append("=" * 70)
        lines.append(f"AUTOMATED INSIGHTS REPORT (last {days} days)")
        lines.append("=" * 70)

        # Summary
        summary = analysis["data_summary"]
        lines.append(f"\n📊 DATA SUMMARY:")
        lines.append(f"  Posts analyzed: {summary['total_posts']}")
        lines.append(f"  Total views: {summary['total_views']:,}")
        lines.append(f"  Total likes: {summary['total_likes']:,}")
        lines.append(f"  Channels: {summary['channels_count']}")

        # Insights
        if analysis["insights"]:
            lines.append(f"\n💡 INSIGHTS:")
            for i, insight in enumerate(analysis["insights"], 1):
                emoji = {"success": "✅", "warning": "⚠️", "info": "ℹ️"}.get(insight["type"], "•")
                lines.append(f"  {i}. {emoji} [{insight['category'].upper()}] {insight['message']}")
                if insight.get("detail"):
                    lines.append(f"     → {insight['detail']}")

        # Recommendations
        if analysis["recommendations"]:
            lines.append(f"\n🎯 RECOMMENDATIONS:")
            for i, rec in enumerate(analysis["recommendations"], 1):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec["priority"], "•")
                lines.append(f"  {i}. {priority_emoji} [{rec['priority'].upper()}] {rec['action']}")
                lines.append(f"     Why: {rec['reason']}")
                if rec.get("tactics"):
                    lines.append(f"     How:")
                    for tactic in rec["tactics"]:
                        lines.append(f"       • {tactic}")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)