"""RSS/Atom feed validation - Sprint 76.1 (Part 2: Feed Discovery).

Валидация URL как RSS/Atom фида. `fetch` инжектируется для тестов
(в проде default — httpx).
"""
import logging
import re
from dataclasses import dataclass
from typing import Callable, Optional

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 10.0


@dataclass(frozen=True)
class FeedValidation:
    """Результат валидации фида."""

    url: str
    is_valid: bool
    feed_type: str  # "rss" | "atom" | "html" | "none"
    title: Optional[str] = None
    item_count: int = 0
    error: Optional[str] = None


def _extract_feed_type(text: str) -> str:
    head = text[:5000].lower()
    if "<rss" in head or "<rdf" in head or "<rss " in head:
        return "rss"
    if "<feed" in head and "xmlns" in head:
        return "atom"
    return "html"


def _extract_title(text: str) -> Optional[str]:
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else None


def _count_items(text: str) -> int:
    lower = text.lower()
    return max(lower.count("<item"), lower.count("<entry"))


def validate_feed(url: str, fetch: Optional[Callable[[str], str]] = None) -> FeedValidation:
    """Проверить, что URL — валидный RSS/Atom фид.

    Args:
        url: URL фида.
        fetch: клиент, возвращающий текст ответа. Default = httpx.get.
               (инжектируется в тестах, чтобы не ходить в сеть).
    """
    try:
        if fetch is None:
            import httpx
            resp = httpx.get(url, timeout=_DEFAULT_TIMEOUT, follow_redirects=True)
            resp.raise_for_status()
            body = resp.text
        else:
            body = fetch(url)

        feed_type = _extract_feed_type(body)
        if feed_type in ("rss", "atom"):
            return FeedValidation(
                url=url,
                is_valid=True,
                feed_type=feed_type,
                title=_extract_title(body),
                item_count=_count_items(body),
            )
        return FeedValidation(
            url=url,
            is_valid=False,
            feed_type=feed_type,
            error=f"not an RSS/Atom feed (detected: {feed_type})",
        )
    except Exception as e:  # noqa: BLE001 — любой сбой сети/парсинга = invalid
        logger.info("Feed validation failed %s: %s", url, e)
        return FeedValidation(url=url, is_valid=False, feed_type="none", error=str(e))