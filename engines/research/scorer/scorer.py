import logging
from datetime import datetime, timezone
from typing import List
from ..deduplicator import Topic

logger = logging.getLogger(__name__)

class TopicScorer:
    def score_topics(self, topics: List[Topic]) -> List[Topic]:
        logger.info(f"Скоринг: оцениваем {len(topics)} тем...")
        now = datetime.now(timezone.utc)

        for topic in topics:
            score = 0.0
            score += topic.max_trust_score * 0.5
            mention_count = len(topic.articles)
            score += min(mention_count * 10, 30)

            if topic.first_published:
                pub_time = topic.first_published
                if pub_time.tzinfo is None:
                    pub_time = pub_time.replace(tzinfo=timezone.utc)
                hours_old = (now - pub_time).total_seconds() / 3600
                if hours_old < 48:
                    score += 20
                elif hours_old < 168:
                    score += 10

            topic.importance_score = min(score, 100.0)

        topics.sort(key=lambda x: x.importance_score, reverse=True)
        logger.info(f"Скоринг завершен. Топ-3: {[f'{t.importance_score:.1f}' for t in topics[:3]]}")
        return topics
