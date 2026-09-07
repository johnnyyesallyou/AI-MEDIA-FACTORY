"""Sprint 70.4: очистка текста для безопасной отправки в Telegram.

Корневая причина 400 Bad Request: в текст поста попадал сырой HTML
из RSS-фидов (<p>, <a href>, ...), а Telegram Bot API в parse_mode=HTML
поддерживает строго ограниченный набор тегов (b, i, a, code, pre, ...).

Стратегия защиты:
1. strip_html() — убрать ВСЕ теги + раскрыть HTML-сущности (для fallback-текстов).
2. sanitize_telegram_text() — strip_html + экранирование остаточных <>&
   для parse_mode=HTML + обрезка под лимит Telegram (4096).
"""
import html
import re

_TAG_RE = re.compile(r"<[^>]+>")
_BLANK_LINES_RE = re.compile(r"\n{3,}")

TELEGRAM_MAX_LENGTH = 4096
# Оставляем запас под добавку "Источник: ..." и служебные символы
SAFE_MAX_LENGTH = 4000


def strip_html(text: str) -> str:
    """Убирает все HTML-теги и раскрывает HTML-сущности."""
    if not text:
        return ""
    text = _TAG_RE.sub("", text)
    text = html.unescape(text)
    text = _BLANK_LINES_RE.sub("\n\n", text)
    return text.strip()


def sanitize_telegram_text(text: str, max_length: int = SAFE_MAX_LENGTH) -> str:
    """Готовит текст для отправки с parse_mode=HTML.

    Убирает теги, экранирует остаточные &, <, > (чтобы случайная
    непарная разметка из LLM/RSS не ломала парсинг Telegram),
    обрезает до max_length.
    """
    text = strip_html(text)
    text = html.escape(text, quote=False)
    if len(text) > max_length:
        text = text[: max_length - 1].rstrip() + "…"
    return text
