"""
Sprint 75.1: Profile → Pipeline runtime contract.

Единая точка загрузки runtime-конфигурации канала для Research/Writing/Evaluation jobs.

Приоритет источников конфигурации:
    1. ChannelProfileORM (channel.profile_id) — primary runtime config source
    2. channel.content_profile (JSONB) — secondary
    3. Legacy defaults (TELEGRAM_AI_EXPERT + hardcoded fallbacks) — fallback only

Возвращает unified dict `profile_config`:
    profile_id, profile_name, source ("profile"|"content_profile"|"legacy"),
    topic, audience, tone, language, content_length,
    sources (list of source dicts or None), freshness_hours,
    style_profile (dict для WritingEngine.generate(style_profile=...)),
    target_style (str для LLMEvaluatorEngine.evaluate(target_style=...)).

Sprint 75.2: полный A/B behavior-тест (75.1 = загрузка + wiring + smoke).
"""
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Sprint 75.1: legacy fallback ONLY (не primary). Полный стиль WritingJob по умолчанию.
from engines.writing.styles.profiles import TELEGRAM_AI_EXPERT as LEGACY_STYLE_PROFILE

LEGACY_TARGET_STYLE = "Telegram expert IT channel"
LEGACY_TOPIC = None


def _audience_to_str(audience: Any) -> Optional[str]:
    """ChannelProfileORM.audience — JSONB {"age": ..., "interests": [...]} или str."""
    if audience is None:
        return None
    if isinstance(audience, str):
        return audience
    if isinstance(audience, dict):
        parts = []
        age = audience.get("age")
        interests = audience.get("interests")
        if age:
            parts.append(str(age))
        if interests:
            parts.append(", ".join(map(str, interests)))
        return "Аудитория: " + ", ".join(parts) if parts else None
    return str(audience)


def _fmt_to_str(fmt: Any) -> Optional[str]:
    """profile.content.formats может быть списком ["telegram_post", ...] или строкой."""
    if fmt is None:
        return None
    if isinstance(fmt, str):
        return fmt
    if isinstance(fmt, (list, tuple)):
        return ", ".join(map(str, fmt))
    return str(fmt)


def _style_profile_from_orm(profile) -> dict:
    """Собирает style_profile dict из ChannelProfileORM (формат WritingEngine)."""
    content = getattr(profile, "content", None) or {}
    length = content.get("max_length") or content.get("length_chars")
    audience_str = _audience_to_str(getattr(profile, "audience", None))
    return {
        "name": getattr(profile, "name", None) or "channel_profile",
        "channel": "telegram",
        "audience": audience_str or LEGACY_STYLE_PROFILE.get("audience"),
        "tone": getattr(profile, "tone", None) or LEGACY_STYLE_PROFILE.get("tone"),
        "length_chars": int(length) if length else LEGACY_STYLE_PROFILE.get("length_chars", 1200),
        "format": _fmt_to_str(content.get("format") or content.get("formats"))
                  or LEGACY_STYLE_PROFILE.get("format"),
        "emoji_usage": content.get("emoji_usage") or LEGACY_STYLE_PROFILE.get("emoji_usage"),
        "forbidden": content.get("forbidden") or LEGACY_STYLE_PROFILE.get("forbidden", []),
        "example": content.get("example") or LEGACY_STYLE_PROFILE.get("example"),
    }


def _target_style_from_orm(profile) -> str:
    """Строка стиля для LLM-as-a-Judge (стиль-aware критерии оценки)."""
    archetype = getattr(profile, "archetype", None) or "news"
    name = getattr(profile, "name", None) or "channel"
    tone = getattr(profile, "tone", None) or "informative"
    language = getattr(profile, "language", None) or "ru"
    audience_str = _audience_to_str(getattr(profile, "audience", None)) or "широкая аудитория"
    content = getattr(profile, "content", None) or {}
    length = content.get("max_length") or content.get("length_chars") or 1200
    return (
        f"Channel '{name}' (archetype: {archetype}). "
        f"Tone: {tone}. Audience: {audience_str}. "
        f"Language: {language}. Target post length: {length} chars."
    )


def load_profile_config(db, channel) -> dict:
    """
    Загружает unified profile_config для канала.

    Args:
        db: SQLAlchemy session (для загрузки ChannelProfileORM).
        channel: ChannelORM или None.

    Returns:
        Unified profile_config dict (см. module docstring).
        Никогда не бросает исключений: любой сбой → legacy fallback.
    """
    cfg = {
        "profile_id": None,
        "profile_name": None,
        "source": "legacy",
        "topic": LEGACY_TOPIC,
        "audience": LEGACY_STYLE_PROFILE.get("audience"),
        "tone": LEGACY_STYLE_PROFILE.get("tone"),
        "language": None,
        "content_length": LEGACY_STYLE_PROFILE.get("length_chars", 1200),
        "sources": None,
        "freshness_hours": None,
        "style_profile": dict(LEGACY_STYLE_PROFILE),
        "target_style": LEGACY_TARGET_STYLE,
    }

    if channel is None:
        logger.info("ProfileConfig: no channel -> legacy fallback")
        return cfg

    # Priority 1: ChannelProfileORM (primary runtime config source)
    profile = None
    profile_id = getattr(channel, "profile_id", None)
    if profile_id and db is not None:
        try:
            from core.models.channel_profile_orm import ChannelProfileORM
            profile = (
                db.query(ChannelProfileORM)
                .filter(ChannelProfileORM.id == profile_id)
                .first()
            )
        except Exception as e:
            logger.warning("ProfileConfig: failed to load ChannelProfileORM id=%s: %s", profile_id, e)

    if profile is not None:
        cfg["source"] = "profile"
        cfg["profile_id"] = getattr(profile, "id", None)
        cfg["profile_name"] = getattr(profile, "name", None)
        cfg["language"] = getattr(profile, "language", None)
        cfg["audience"] = _audience_to_str(getattr(profile, "audience", None)) or cfg["audience"]
        cfg["tone"] = getattr(profile, "tone", None) or cfg["tone"]

        content = getattr(profile, "content", None) or {}
        length = content.get("max_length") or content.get("length_chars")
        if length:
            cfg["content_length"] = int(length)

        research = getattr(profile, "research", None) or {}
        cfg["freshness_hours"] = research.get("freshness_hours")
        cfg["sources"] = research.get("sources")  # None -> engine legacy fallback

        cfg["style_profile"] = _style_profile_from_orm(profile)
        cfg["target_style"] = _target_style_from_orm(profile)

        logger.info(
            "ProfileConfig: loaded from ChannelProfileORM name=%s archetype=%s "
            "sources=%s freshness=%s length=%s",
            cfg["profile_name"], getattr(profile, "archetype", None),
            len(cfg["sources"]) if cfg["sources"] else None,
            cfg["freshness_hours"], cfg["content_length"],
        )
        return cfg

    # Priority 2: channel.content_profile (JSONB, secondary)
    cp = getattr(channel, "content_profile", None)
    if isinstance(cp, dict) and cp:
        cfg["source"] = "content_profile"
        cfg["topic"] = cp.get("topic") or cfg["topic"]
        cfg["audience"] = cp.get("audience") or cfg["audience"]
        cfg["tone"] = cp.get("tone") or cfg["tone"]
        cp_sources = cp.get("sources")
        if cp_sources:
            cfg["sources"] = cp_sources
        length = cp.get("max_length") or cp.get("length_chars")
        if length:
            cfg["content_length"] = int(length)
            cfg["style_profile"]["length_chars"] = int(length)

        logger.info(
            "ProfileConfig: loaded from channel.content_profile (profile_name=%s, keys=%s)",
            cp.get("profile_key"), list(cp.keys())[:8],
        )
        return cfg

    # Priority 3: legacy fallback (profile absent)
    logger.info(
        "ProfileConfig: no profile/content_profile for channel=%s -> legacy fallback",
        getattr(channel, "name", None),
    )
    return cfg
