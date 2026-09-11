import logging
from typing import List
from .config import RSS_SOURCES
from .sources.rss import RSSSource
from .deduplicator import Deduplicator
from .scorer import TopicScorer

logger = logging.getLogger(__name__)


class ResearchEngine:
    """
    Упрощённая боевая версия Research Engine.
    Без BaseEngine/ExecutionContext/MetricsCollector - тот контекст
    в лабораторной версии не использовался внутри логики, поэтому убран,
    чтобы не тащить неиспользуемую инфраструктуру.
    """

    def __init__(self):
        self.sources: List[RSSSource] = []
        self.deduplicator = Deduplicator(similarity_threshold=0.35)
        self.scorer = TopicScorer()
        self._initialized = False

    def initialize(self, channel=None, sources_override=None):
        if self._initialized:
            return
        # Sprint 75.1: Profile sources (primary runtime config) → channel.sources (legacy) → RSS fallback
        if sources_override:
            sources_to_use = sources_override
            logger.info(f"Инициализация Research Engine с {len(sources_to_use)} источниками из Channel Profile (Sprint 75.1)")
        elif channel and getattr(channel, "sources", None):
            sources_to_use = channel.sources
            logger.info(f"Инициализация Research Engine с {len(sources_to_use)} источниками из канала")
        else:
            # Fallback на hardcoded RSS_SOURCES для обратной совместимости
            sources_to_use = RSS_SOURCES
            logger.info(f"Инициализация Research Engine с {len(sources_to_use)} hardcoded источниками (fallback)")
        
        for source_config in sources_to_use:
            try:
                self.sources.append(RSSSource(source_config))
            except Exception as e:
                logger.warning(f"Failed to init source {source_config.get('name', 'unknown')}: {e}")
        self._initialized = True

    def run(self, channel=None, sources_override=None) -> dict:
        """Синхронный прогон полного research pipeline. Возвращает dict с темами.

        Sprint 75.1: sources_override — источники из Channel Profile
        (приоритет над channel.sources / RSS fallback).
        """
        if not self._initialized:
            self.initialize(channel=channel, sources_override=sources_override)

        logger.info("Запуск Research Pipeline")

        all_articles = []
        tokens_input = 0
        for source in self.sources:
            articles = source.fetch(max_items=20)
            all_articles.extend(articles)
            for article in articles:
                tokens_input += len(article.content.split()) // 4

        logger.info(f"Загружено {len(all_articles)} сырых статей")

        topics = self.deduplicator.group_into_topics(all_articles)
        scored_topics = self.scorer.score_topics(topics)

        result_topics = []
        high_score_count = 0
        for topic in scored_topics:
            if topic.importance_score >= 80:
                high_score_count += 1
            result_topics.append({
                "title": topic.title,
                "summary": topic.summary,
                "importance_score": round(topic.importance_score, 1),
                "mention_count": len(topic.articles),
                "max_trust_score": topic.max_trust_score,
                "sources": list(set(a.source for a in topic.articles)),
                "urls": [a.url for a in topic.articles[:3]],
            })

        return {
            "topics": result_topics,
            "total_raw_articles": len(all_articles),
            "unique_topics": len(topics),
            "high_score_topics": high_score_count,
            "tokens_input": tokens_input,
        }
