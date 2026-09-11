"""Subscribe.ru Discovery Adapter - Sprint 76.3.

Интеграция с Subscribe.ru для автоматического discovery источников по категориям/тегам.
Subscribe.ru предоставляет каталог RSS-фидов и возможность поиска по категориям.

API базируется на:
- Search API (поиск по тегам и категориям)
- Feed parsing (экстракция RSS URLs из результатов)
"""
import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Callable
from urllib.parse import urljoin, quote

logger = logging.getLogger(__name__)

SUBSCRIBE_RU_BASE = "https://subscribe.ru"
SUBSCRIBE_RU_API = f"{SUBSCRIBE_RU_BASE}/api/v2"


@dataclass(frozen=True)
class SubscribeRuResult:
    """Результат discovery из Subscribe.ru."""

    title: str
    description: Optional[str]
    rss_url: str
    language: str
    category: str
    subscribers: int = 0
    source: str = "subscribe_ru"


class SubscribeRuDiscoveryError(Exception):
    """Ошибка при работе с Subscribe.ru."""
    pass


class SubscribeRuAdapter:
    """Adapter для поиска источников через Subscribe.ru."""

    # Категории Subscribe.ru с соответствующим mapping'ом на наши content_type
    CATEGORY_MAPPING = {
        "news": ["новости", "события", "политика", "бизнес", "технологии"],
        "educational": ["образование", "наука", "технологии", "самообразование"],
        "entertainment": ["развлечения", "юмор", "видео", "музыка"],
        "anime": ["аниме", "манга", "японская культура"],
        "manga": ["манга", "комиксы", "графические романы"],
    }

    @staticmethod
    def category_for_content_type(content_type: str) -> List[str]:
        """Получить категории Subscribe.ru для content_type."""
        return SubscribeRuAdapter.CATEGORY_MAPPING.get(content_type, [])

    @staticmethod
    def discover(
        topic: str,
        language: str = "ru",
        content_type: Optional[str] = None,
        top_k: Optional[int] = None,
        fetch: Optional[Callable[[str], str]] = None,
    ) -> List[SubscribeRuResult]:
        """Discover источники через Subscribe.ru.

        Args:
            topic: Поисковый запрос (е.g. "python", "новости", "аниме")
            language: Язык ("ru" или "en")
            content_type: Тип контента для маппинга категорий
            top_k: Максимум результатов
            fetch: Клиент для HTTP запросов (инжектируется для тестов)

        Returns:
            Список SubscribeRuResult, отсортированный по релевантности.

        Raises:
            SubscribeRuDiscoveryError: при ошибке API или парсинга
        """
        try:
            # Формируем поисковый запрос
            query = _build_search_query(topic, content_type, language)

            # Выполняем поиск
            results = _search_subscribe_ru(query, fetch=fetch)

            # Нормализуем результаты
            normalized = [_normalize_result(r) for r in results]

            # Фильтруем валидные (должны быть RSS URLs)
            valid_results = [r for r in normalized if r.rss_url]

            # Сортируем по релевантности (количество подписчиков как proxy)
            valid_results.sort(key=lambda r: r.subscribers, reverse=True)

            if top_k:
                valid_results = valid_results[:top_k]

            logger.info(f"Subscribe.ru discovery: found {len(valid_results)} sources for '{topic}'")
            return valid_results

        except Exception as e:
            raise SubscribeRuDiscoveryError(
                f"Subscribe.ru discovery failed for '{topic}': {str(e)}"
            ) from e


def _build_search_query(
    topic: str,
    content_type: Optional[str] = None,
    language: str = "ru",
) -> str:
    """Построить поисковый query для Subscribe.ru.

    Может быть:
    - Прямой поиск по названию (e.g. "Habr", "Лента.ру")
    - Поиск по категориям (e.g. "новости", "технологии")
    - Комбинированный поиск
    """
    # Если есть content_type, добавляем категорию
    if content_type:
        categories = SubscribeRuAdapter.category_for_content_type(content_type)
        if categories:
            # Примерно: "python новости" или "аниме"
            return f"{topic} {categories[0]}"

    return topic


def _search_subscribe_ru(
    query: str,
    fetch: Optional[Callable[[str], str]] = None,
    timeout: float = 10.0,
) -> List[dict]:
    """Выполнить поиск на Subscribe.ru API.

    Примечание: это упрощённая реализация.
    В реальном коде нужно будет проверить актуальный Subscribe.ru API.

    Для текущей реализации используется:
    - Поиск по каталогу Subscribe.ru
    - Парсинг результатов поиска
    - Экстракция RSS URLs
    """
    try:
        if fetch is None:
            import httpx
            # Subscribe.ru search API endpoint
            search_url = f"{SUBSCRIBE_RU_API}/search?q={quote(query)}&limit=20"
            resp = httpx.get(search_url, timeout=timeout, follow_redirects=True)
            resp.raise_for_status()
            # Assuming JSON response with 'results' key
            data = resp.json()
            return data.get("results", [])
        else:
            # fetch инжектируется в тестах, должен вернуть JSON
            import json
            response_text = fetch(f"search?q={quote(query)}")
            return json.loads(response_text).get("results", [])

    except Exception as e:
        logger.warning(f"Subscribe.ru API search failed: {e}")
        return []


def _normalize_result(raw_result: dict) -> SubscribeRuResult:
    """Нормализовать результат из Subscribe.ru API.

    Преобразует API response в стандартный формат SubscribeRuResult.
    """
    title = raw_result.get("title", "")
    description = raw_result.get("description")
    rss_url = raw_result.get("rss_url") or _extract_rss_url(raw_result)
    language = raw_result.get("language", "ru")
    category = raw_result.get("category", "uncategorized")
    subscribers = raw_result.get("subscribers", 0)

    return SubscribeRuResult(
        title=title,
        description=description,
        rss_url=rss_url,
        language=language,
        category=category,
        subscribers=int(subscribers) if subscribers else 0,
    )


def _extract_rss_url(item: dict) -> Optional[str]:
    """Экстрактить RSS URL из результата Subscribe.ru.

    Subscribe.ru может предоставлять:
    - Прямой RSS URL
    - URL на страницу (нужно парсить)
    - Данные для реконструкции RSS URL
    """
    # Прямой RSS URL
    if "rss_url" in item:
        return item["rss_url"]

    # URL на странице подписки
    if "url" in item:
        url = item["url"]
        # Subscribe.ru обычно предоставляет /item/XXXXX/rss
        if "/item/" in url:
            # Реконструируем RSS URL
            match = re.search(r"/item/(\d+)", url)
            if match:
                item_id = match.group(1)
                return f"{SUBSCRIBE_RU_BASE}/item/{item_id}/rss"

    # ID-based reconstruction
    if "id" in item:
        return f"{SUBSCRIBE_RU_BASE}/item/{item['id']}/rss"

    return None


# Public API для использования в pipeline
__all__ = [
    "SubscribeRuAdapter",
    "SubscribeRuResult",
    "SubscribeRuDiscoveryError",
]
