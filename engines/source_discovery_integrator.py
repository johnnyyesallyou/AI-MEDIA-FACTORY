"""Source Discovery Integrator - Sprint 76.3.

Интегрирует различные sources discovery (Subscribe.ru, известные источники)
в единый pipeline с нормализацией, валидацией и дедупликацией.
"""
import logging
from dataclasses import dataclass
from typing import List, Optional, Set, Callable
from urllib.parse import urlparse

from .source_validation import validate_feed, FeedValidation
from .subscribe_ru_adapter import SubscribeRuAdapter, SubscribeRuResult
from .source_registry import SOURCES, SourceDefinition

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DiscoveredSource:
    """Нормализованный источник из discovery."""

    url: str
    name: str
    source_type: str  # "subscribe_ru", "known_sources", "manual"
    language: str
    category: Optional[str] = None
    description: Optional[str] = None
    is_rss_validated: bool = False
    feed_type: Optional[str] = None  # "rss" или "atom"
    item_count: int = 0
    quality_score: float = 0.0


class SourceDiscoveryIntegrator:
    """Объединяет результаты из разных sources discovery."""

    @staticmethod
    def discover_and_normalize(
        topic: str,
        language: str = "ru",
        content_type: Optional[str] = None,
        validate_feeds: bool = True,
        top_k: Optional[int] = None,
        fetch: Optional[Callable[[str], str]] = None,
    ) -> List[DiscoveredSource]:
        """Discover, normalize и validate источники.

        Pipeline:
        1. Subscribe.ru discovery
        2. Нормализация результатов
        3. Валидация RSS feeds
        4. Дедупликация
        5. Сортировка по качеству
        6. Fallback на известные источники

        Args:
            topic: Поисковый запрос
            language: Язык
            content_type: Тип контента
            validate_feeds: Проверять ли результаты как RSS
            top_k: Максимум результатов

        Returns:
            Список нормализованных источников
        """
        discovered = []
        seen_urls: Set[str] = set()

        try:
            # Этап 1: Subscribe.ru discovery
            logger.info(f"Discovering sources for topic='{topic}', content_type='{content_type}'")
            subscribe_ru_results = SubscribeRuAdapter.discover(
                topic=topic,
                language=language,
                content_type=content_type,
                top_k=top_k or 50,
                fetch=fetch,
            )

            # Этап 2: Нормализация + валидация
            for sr in subscribe_ru_results:
                if sr.rss_url in seen_urls:
                    continue  # Дедупликация

                source = _normalize_subscribe_ru_result(
                    sr, validate_feeds=validate_feeds
                )
                if source:
                    discovered.append(source)
                    seen_urls.add(sr.rss_url)

        except Exception as e:
            logger.warning(f"Subscribe.ru discovery failed: {e}. Using fallback.")

        # Этап 3: Fallback на известные источники (если discover не вернул результатов)
        if not discovered:
            logger.info("No sources discovered. Using known sources as fallback.")
            known = _get_known_sources_as_discovered(
                content_type=content_type, language=language
            )
            discovered.extend(known)
            seen_urls.update(s.url for s in known)

        # Этап 4: Сортировка по quality_score (валидные + количество item's)
        discovered.sort(
            key=lambda s: (
                s.is_rss_validated,  # Валидные RSS фиды в начале
                s.item_count,        # Затем по количеству item's
                s.quality_score,     # Затем по quality score
            ),
            reverse=True,
        )

        if top_k:
            discovered = discovered[:top_k]

        logger.info(
            f"Discovery complete: {len(discovered)} sources "
            f"({sum(1 for s in discovered if s.is_rss_validated)} validated)"
        )
        return discovered

    @staticmethod
    def get_fallback_sources(
        content_type: Optional[str] = None,
        language: str = "ru",
    ) -> List[DiscoveredSource]:
        """Получить fallback список известных источников."""
        return _get_known_sources_as_discovered(content_type, language)


def _normalize_subscribe_ru_result(
    sr: SubscribeRuResult,
    validate_feeds: bool = True,
) -> Optional[DiscoveredSource]:
    """Нормализовать результат Subscribe.ru в DiscoveredSource."""
    if not sr.rss_url:
        logger.warning(f"Subscribe.ru result has no RSS URL: {sr.title}")
        return None

    # Валидируем как RSS (если требуется)
    feed_validation: Optional[FeedValidation] = None
    is_rss_validated = False
    feed_type = None
    item_count = 0

    if validate_feeds:
        try:
            feed_validation = validate_feed(sr.rss_url)
            is_rss_validated = feed_validation.is_valid
            feed_type = feed_validation.feed_type
            item_count = feed_validation.item_count
        except Exception as e:
            logger.warning(f"Feed validation failed for {sr.rss_url}: {e}")

    # Если не валидный RSS и validation обязателен, пропускаем
    if validate_feeds and not is_rss_validated:
        logger.warning(f"Not a valid RSS feed: {sr.rss_url}")
        return None

    # Качество = подписчики / 1000 (нормализуем к 0..100)
    quality_score = min(100.0, sr.subscribers / 10.0) if sr.subscribers else 50.0

    return DiscoveredSource(
        url=sr.rss_url,
        name=sr.title or "Unknown",
        source_type="subscribe_ru",
        language=sr.language,
        category=sr.category,
        description=sr.description,
        is_rss_validated=is_rss_validated,
        feed_type=feed_type,
        item_count=item_count,
        quality_score=quality_score,
    )


def _get_known_sources_as_discovered(
    content_type: Optional[str] = None,
    language: str = "ru",
) -> List[DiscoveredSource]:
    """Преобразовать известные источники в DiscoveredSource."""
    discovered = []

    for source_def in SOURCES.values():
        # Фильтруем по content_type и language
        if content_type and content_type not in source_def.content_types:
            continue
        if language not in source_def.languages:
            continue

        # Известные источники имеют RSS URLs
        # (мы не знаем их точного количества, используем placeholder)
        discovered.append(
            DiscoveredSource(
                url=source_def.id,  # используем source_id как placeholder
                name=source_def.name,
                source_type="known_sources",
                language=language,
                category="known",
                description=None,
                is_rss_validated=True,  # Известные источники уже валидны
                feed_type="rss",
                item_count=100,  # Placeholder
                quality_score=75.0,  # Baseline для известных источников
            )
        )

    return discovered


def _deduplicate_by_url(sources: List[DiscoveredSource]) -> List[DiscoveredSource]:
    """Удалить дубликаты по URL."""
    seen: Set[str] = set()
    unique = []

    for source in sources:
        # Нормализуем URL для сравнения
        normalized_url = _normalize_url_for_comparison(source.url)
        if normalized_url not in seen:
            unique.append(source)
            seen.add(normalized_url)

    return unique


def _normalize_url_for_comparison(url: str) -> str:
    """Нормализовать URL для сравнения."""
    # Удаляем trailing slash, protocol, www
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    netloc = parsed.netloc.lstrip("www.")
    return f"{netloc}{path}".lower()


# Public API
__all__ = [
    "SourceDiscoveryIntegrator",
    "DiscoveredSource",
]
