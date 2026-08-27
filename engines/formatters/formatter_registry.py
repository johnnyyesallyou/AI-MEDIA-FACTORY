"""Formatter Registry - Sprint 54.

Возвращает нужный formatter по content_type + topic.

Маппинг:
  manga    -> MangaFormatter
  news     -> NewsFormatter
  anime    -> AnimeFormatter
  (другое) -> NewsFormatter (default fallback)
"""
from typing import Optional

from engines.formatters.base import BaseFormatter
from engines.formatters.manga_formatter import MangaFormatter
from engines.formatters.news_formatter import NewsFormatter
from engines.formatters.anime_formatter import AnimeFormatter


_REGISTRY = {
    "manga": MangaFormatter,
    "chapter_release": MangaFormatter,
    "news": NewsFormatter,
    "technology": NewsFormatter,
    "anime": AnimeFormatter,
    "anime_news": AnimeFormatter,
}


def get_formatter(content_type: str, topic: str = None) -> BaseFormatter:
    """Возвращает formatter для данного content_type/topic.

    Приоритет: сначала topic, потом content_type, потом NewsFormatter как fallback.
    """
    if topic and topic in _REGISTRY:
        return _REGISTRY[topic]()
    if content_type in _REGISTRY:
        return _REGISTRY[content_type]()
    # Fallback
    return NewsFormatter()