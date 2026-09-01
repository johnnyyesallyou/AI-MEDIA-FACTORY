"""Sprint 67.4: Generic Strategies — универсальные стратегии для всех архетипов.

Читают настройки из ChannelProfile + ArchetypeDefaults.
Один код обслуживает releases/educational/viral/reviews/community/aggregator.
"""
import logging
from typing import List, Dict, Any, Optional

from core.models.archetypes import Archetype, get_archetype_defaults

logger = logging.getLogger(__name__)


def _arch(profile: Any) -> Archetype:
    try:
        return Archetype(getattr(profile, "archetype", "news"))
    except (ValueError, KeyError):
        return Archetype.NEWS


class GenericResearchStrategy:
    def __init__(self, profile: Any):
        self.profile = profile
        defaults = get_archetype_defaults(_arch(profile))
        cfg = profile.research or {}
        self.sources = cfg.get("sources", ["rss", "web"])
        self.freshness_hours = cfg.get("freshness_hours", 24)
        self.archetype = defaults.archetype

    async def collect_sources(self) -> List[Dict[str, Any]]:
        logger.info(f"[{self.archetype.value}] Collecting sources: {self.sources}")
        return []

    async def extract_topics(self, sources: List[Dict]) -> List[Dict[str, Any]]:
        logger.info(f"[{self.archetype.value}] Extracting topics from {len(sources)} sources")
        return []


class GenericGenerationStrategy:
    def __init__(self, profile: Any):
        self.profile = profile
        defaults = get_archetype_defaults(_arch(profile))
        cfg = profile.content or {}
        self.max_length = cfg.get("max_length", defaults.max_post_length)
        self.formats = cfg.get("formats", defaults.allowed_formats)
        self.tone = profile.tone or defaults.tone

    async def generate_post(self, topic: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        logger.info(f"[{self.tone}] Generating post (max={self.max_length})")
        return {
            "title": topic.get("title", ""),
            "content": topic.get("summary", ""),
            "format": self.formats[0] if self.formats else "post",
            "tone": self.tone,
            "max_length": self.max_length,
        }


class GenericMediaStrategy:
    def __init__(self, profile: Any):
        self.profile = profile
        defaults = get_archetype_defaults(_arch(profile))
        cfg = profile.media or {}
        self.preferred = cfg.get("preferred", [defaults.media_policy])
        self.fallback = cfg.get("fallback", [])

    async def select_media(self, post: Dict[str, Any]) -> Optional[str]:
        logger.info(f"Selecting media (preferred={self.preferred})")
        return None


class GenericPublishingStrategy:
    def __init__(self, profile: Any):
        self.profile = profile
        defaults = get_archetype_defaults(_arch(profile))
        cfg = profile.publishing or {}
        self.mode = cfg.get("mode", defaults.publishing_mode)
        self.frequency = cfg.get("frequency_per_day", defaults.frequency_per_day)

    async def publish(self, post: Dict[str, Any], media_url: Optional[str]) -> Dict[str, Any]:
        logger.info(f"Publishing (mode={self.mode}, freq={self.frequency}/day)")
        if self.mode == "auto":
            return {"success": True, "mode": "auto"}
        if self.mode == "approval_required":
            return {"success": True, "mode": "approval_required", "status": "draft"}
        return {"success": False, "mode": "manual", "reason": "Manual mode"}