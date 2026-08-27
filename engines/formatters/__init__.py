"""Formatter Layer - Sprint 54.

Формат поста определяется здесь, а не в publish job-ах.
"""
from engines.formatters.base import (
    BaseFormatter,
    FormatContext,
    format_hashtag,
    smart_truncate,
    translate_to_russian,
    unescape,
    has_cyrillic,
)
from engines.formatters.manga_formatter import MangaFormatter
from engines.formatters.news_formatter import NewsFormatter
from engines.formatters.anime_formatter import AnimeFormatter
from engines.formatters.formatter_registry import get_formatter

__all__ = [
    "BaseFormatter",
    "FormatContext",
    "MangaFormatter",
    "NewsFormatter",
    "AnimeFormatter",
    "get_formatter",
    "format_hashtag",
    "smart_truncate",
    "translate_to_russian",
    "unescape",
    "has_cyrillic",
]