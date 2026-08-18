import logging
from typing import List
from ..models import Article

logger = logging.getLogger(__name__)

class Topic:
    def __init__(self, representative_article: Article):
        self.id = representative_article.id
        self.title = representative_article.title
        self.summary = representative_article.summary
        self.articles: List[Article] = [representative_article]
        self.max_trust_score = representative_article.trust_score
        self.first_published = representative_article.published_at
        self.importance_score = 0.0

    def add_article(self, article: Article):
        self.articles.append(article)
        if article.trust_score > self.max_trust_score:
            self.max_trust_score = article.trust_score
            self.title = article.title
            self.summary = article.summary

class Deduplicator:
    def __init__(self, similarity_threshold: float = 0.4):
        self.threshold = similarity_threshold

    def group_into_topics(self, articles: List[Article]) -> List[Topic]:
        logger.info(f"Дедупликация: обрабатываем {len(articles)} статей...")
        topics: List[Topic] = []

        for article in articles:
            text_to_compare = (article.title + " " + article.summary).lower()
            words = set(self._tokenize(text_to_compare))
            matched_topic = None

            for topic in topics:
                topic_text = (topic.title + " " + topic.summary).lower()
                topic_words = set(self._tokenize(topic_text))
                intersection = len(words.intersection(topic_words))
                union = len(words.union(topic_words))
                similarity = intersection / union if union > 0 else 0.0
                if similarity >= self.threshold:
                    matched_topic = topic
                    break

            if matched_topic:
                matched_topic.add_article(article)
            else:
                topics.append(Topic(article))

        logger.info(f"Дедупликация завершена: {len(articles)} статей сгруппированы в {len(topics)} уникальных тем.")
        return topics

    def _tokenize(self, text: str) -> List[str]:
        import re
        return re.findall(r"\b\w+\b", text)
