"""Base Formatter - Sprint 54.

Единый интерфейс форматирования постов + общие text-утилиты.
Jobs отвечают за research/enrichment/image/telegraph,
formatters владеют текстом и кнопками.
"""
import html as html_lib
import re
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import requests

from engines.publishing import Publication, PublicationButton

logger = logging.getLogger(__name__)

CAPTION_LIMIT = 1024


# ---------------------------------------------------------------------------
# Shared text utilities (ранее дублировались в 3 publish job-ах)
# ---------------------------------------------------------------------------

def unescape(text: Optional[str]) -> str:
    """Unescape HTML entities (&quot; -> ")."""
    return html_lib.unescape(text or "")


def has_cyrillic(text: Optional[str]) -> bool:
    return bool(re.search(r"[а-яА-ЯёЁ]", text or ""))


def format_hashtag(tag: str) -> str:
    """Превращает тег/жанр в валидный hashtag."""
    tag = html_lib.unescape((tag or "").strip())
    tag = re.sub(r'[^\wа-яА-ЯёЁ\s]', '', tag)
    tag = tag.replace(' ', '_')
    tag = re.sub(r'^[\d_]+', '', tag)
    return f"#{tag}" if tag else ""


def smart_truncate(text: str, max_length: int) -> str:
    """Обрезает текст по границе слова/предложения."""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > max_length // 2:
        truncated = truncated[:last_space]
    last_punct = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
    if last_punct > max_length // 2:
        truncated = truncated[:last_punct + 1]
    return truncated


def translate_to_russian(text: str, max_length: int = 500, timeout: int = 120) -> str:
    """Перевод EN -> RU через локальный Ollama (gemma2:9b). Возвращает '' при ошибке."""
    if not text or not text.strip():
        return ""
    if has_cyrillic(text):
        return text
    try:
        prompt = (
            "Переведи следующий текст на русский язык. Сохрани стиль и факты. "
            "Только перевод, без пояснений и комментариев.\n\n"
            f"Текст: {text[:800]}\n\nПеревод на русском:"
        )
        response = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={
                "model": "gemma2:9b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 600},
            },
            timeout=timeout,
        )
        if response.status_code == 200:
            translated = response.json().get("response", "").strip()
            if translated:
                logger.info(f"Translated: {text[:50]}... -> {translated[:50]}...")
                return translated[:max_length]
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
    return ""


# ---------------------------------------------------------------------------
# FormatContext: всё, что нужно formatter-у, кроме knowledge object
# ---------------------------------------------------------------------------

@dataclass
class FormatContext:
    """Контекст форматирования (канал + ссылки + политики)."""
    item: Any                                  # ContentORM
    meta: Dict[str, Any] = field(default_factory=dict)   # распарсенный source_text
    related_items: List[Any] = field(default_factory=list)
    telegraph_url: Optional[str] = None
    short_url: str = ""
    image_url: Optional[str] = None
    formatting: Dict[str, Any] = field(default_factory=dict)
    publishing_policy: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# BaseFormatter
# ---------------------------------------------------------------------------

class BaseFormatter(ABC):
    """Базовый класс форматтеров контента.

    format(knowledge_object, ctx) -> Publication
    """

    content_type: str = "generic"

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def format(self, knowledge_object: Any, ctx: FormatContext) -> Publication:
        """Строит Publication из knowledge object + контекста."""
        raise NotImplementedError

    # ---- shared helpers ----

    def build_hashtags(self, tags: List[str], max_hashtags: int) -> List[str]:
        hashtags = [format_hashtag(t) for t in (tags or [])[:max_hashtags]]
        return [h for h in hashtags if h]

    def build_buttons(
        self,
        ctx: FormatContext,
        telegraph_text: str = "📖 Читать полностью",
        source_text: str = "🔗 Источник",
    ) -> List[PublicationButton]:
        """Inline buttons по publishing_policy."""
        buttons: List[PublicationButton] = []
        if ctx.publishing_policy.get("inline_buttons"):
            if ctx.telegraph_url:
                buttons.append(PublicationButton(text=telegraph_text, url=ctx.telegraph_url))
            if ctx.short_url and ctx.short_url != ctx.telegraph_url:
                buttons.append(PublicationButton(text=source_text, url=ctx.short_url))
        return buttons