"""Channel Content Profiles - Sprint 25.2 (extended).

Полный профиль канала:
  content_type, language, sources,
  image_policy, publishing_policy, formatting_profile,
  source_policy, enrichment_policy
"""
import copy
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

_BASE = {
    "theme": "general",
    "content_type": "news",
    "language": "ru",
    "sources": [],
    "image_policy": {
        "mode": "source_first",
        "preferred": "og_image",
        "fallback": "ai_generated",
        "style": "news",
    },
    "publishing_policy": {
        "platform": "telegram",
        "min_interval_seconds": 2.5,
        "max_per_minute": 24,
        "require_ru_title": False,
        "strip_non_ru_description": False,
        "telegraph_page": False,
        "inline_buttons": False,
    },
    "formatting_profile": {
        "emoji_header": "📰",
        "include_description": True,
        "include_hashtags": True,
        "max_hashtags": 10,
        "caption_limit": 1024,
        "unescape_html": True,
        "max_title_length": 250,
    },
    "source_policy": {
        "allowed_sources": [],
        "dedup": True,
    },
    "enrichment_policy": {
        "description": True,
        "genres": True,
        "cover": True,
        "preview_pages": False,
    },
}

PROFILES: Dict[str, Dict[str, Any]] = {
    "ai_news": {
        "theme": "technology",
        "content_type": "news",
        "sources": ["habr", "vc", "openai", "techcrunch", "theverge", "blog.google"],
        "image_policy": {
            "preferred": "og_image",
            "fallback": "ai_generated",
            "style": "news",
        },
        "publishing_policy": {
            "require_ru_title": False,
            "strip_non_ru_description": False,
            "telegraph_page": True,
            "inline_buttons": True,
        },
        "formatting_profile": {
            "emoji_header": "📰",
            "max_hashtags": 8,
            "include_description": True,
        },
        "source_policy": {"allowed_sources": ["habr", "vc", "openai", "techcrunch", "theverge", "blog.google"]},
        "enrichment_policy": {"description": True, "cover": True},
    },
    "anime_news": {
        "theme": "anime",
        "content_type": "anime",  # Sprint 51: не news, чтобы не попадал под AI fallback
        "sources": ["anime_news"],
        "image_policy": {"preferred": "anime_visual", "fallback": "ai_generated", "style": "anime"},
        "formatting_profile": {"emoji_header": "🎬"},
    },
    "anime_release": {
        "theme": "anime",
        "content_type": "anime_release",
        "image_policy": {"preferred": "anime_title_visual", "fallback": "none", "style": "anime"},
        "publishing_policy": {"telegraph_page": False, "inline_buttons": True},
        "formatting_profile": {"emoji_header": "🎬"},
    },
    "manga_releases": {
        "theme": "manga",
        "content_type": "chapter_release",
        "sources": ["remanga", "mangadex"],
        "image_policy": {"preferred": "manga_cover", "fallback": "none", "style": "manga"},
        "publishing_policy": {
            "require_ru_title": False,  # Sprint 51: временно для теста
            "strip_non_ru_description": False,  # Sprint 51: временно для теста
            "telegraph_page": True,
            "inline_buttons": True,
        },
        "formatting_profile": {"emoji_header": "📚", "max_hashtags": 15},
        "source_policy": {"allowed_sources": ["remanga", "mangadex"]},
        "enrichment_policy": {"description": True, "genres": True, "cover": True, "preview_pages": True},
    },
}


def _deep_merge(base: Dict, override: Dict) -> Dict:
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def profile_for(profile_key: str) -> Dict[str, Any]:
    return _deep_merge(_BASE, PROFILES.get(profile_key, {}))


def guess_profile_key(channel) -> str:
    name = (getattr(channel, "name", "") or "").lower()
    if "манга" in name or "manga" in name:
        return "manga_releases"
    if "anime" in name or "аниме" in name:
        if "news" in name or "новости" in name:
            return "anime_news"
        return "anime_release"
    if "manga" in name or "манга" in name:
        return "manga_releases"
    # Default для news-каналов
    return "ai_news"


def resolve_channel_profile(channel) -> Dict[str, Any]:
    stored = getattr(channel, "content_profile", None) or {}
    key = stored.get("profile_key") or guess_profile_key(channel)
    merged = profile_for(key)
    merged = _deep_merge(merged, stored)
    merged["profile_key"] = key
    return merged