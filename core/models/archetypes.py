"""Sprint 67.1: Channel Archetypes — ограниченная типология каналов."""
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional


class Archetype(str, Enum):
    """Archetype определяет базовую стратегию канала."""
    
    NEWS = "news"                    # Breaking news, updates (4-6/day)
    RELEASES = "releases"            # New releases: manga, anime, movies (3-5/day)
    EDUCATIONAL = "educational"      # Facts, learning, how-to (2-4/day)
    ENTERTAINMENT = "entertainment"  # Fun content, memes, casual (4-8/day)
    VIRAL = "viral"                  # Trending, memes, viral (6-12/day)
    REVIEWS = "reviews"              # Reviews, analysis, opinions (2-3/day)
    COMMUNITY = "community"          # Discussion, polls, user content (3-5/day)
    AGGREGATOR = "aggregator"        # Curated content from many sources (8-12/day)


@dataclass
class ArchetypeDefaults:
    """Дефолтные настройки для архетипа."""
    archetype: Archetype
    frequency_per_day: int
    publishing_mode: str  # "auto" | "approval_required" | "manual"
    media_policy: str     # "image" | "video" | "image+video" | "none"
    max_post_length: int
    tone: str             # "informative" | "casual" | "analytical" | "humorous"
    risk_level: str       # "low" | "medium" | "high"
    allowed_formats: List[str]


ARCHETYPE_DEFAULTS = {
    Archetype.NEWS: ArchetypeDefaults(
        archetype=Archetype.NEWS,
        frequency_per_day=5,
        publishing_mode="approval_required",
        media_policy="image",
        max_post_length=1200,
        tone="informative",
        risk_level="medium",
        allowed_formats=["breaking_news", "analysis", "facts"],
    ),
    Archetype.RELEASES: ArchetypeDefaults(
        archetype=Archetype.RELEASES,
        frequency_per_day=4,
        publishing_mode="auto",
        media_policy="image+video",
        max_post_length=800,
        tone="informative",
        risk_level="low",
        allowed_formats=["release_announcement", "preview", "review"],
    ),
    Archetype.EDUCATIONAL: ArchetypeDefaults(
        archetype=Archetype.EDUCATIONAL,
        frequency_per_day=3,
        publishing_mode="approval_required",
        media_policy="image",
        max_post_length=1500,
        tone="informative",
        risk_level="medium",
        allowed_formats=["explainer", "facts", "how_to"],
    ),
    Archetype.ENTERTAINMENT: ArchetypeDefaults(
        archetype=Archetype.ENTERTAINMENT,
        frequency_per_day=6,
        publishing_mode="auto",
        media_policy="image+video",
        max_post_length=600,
        tone="casual",
        risk_level="low",
        allowed_formats=["memes", "fun_facts", "casual_posts"],
    ),
    Archetype.VIRAL: ArchetypeDefaults(
        archetype=Archetype.VIRAL,
        frequency_per_day=8,
        publishing_mode="auto",
        media_policy="image",
        max_post_length=400,
        tone="humorous",
        risk_level="low",
        allowed_formats=["memes", "trending", "viral_posts"],
    ),
    Archetype.REVIEWS: ArchetypeDefaults(
        archetype=Archetype.REVIEWS,
        frequency_per_day=2,
        publishing_mode="approval_required",
        media_policy="image",
        max_post_length=1800,
        tone="analytical",
        risk_level="medium",
        allowed_formats=["review", "analysis", "opinion"],
    ),
    Archetype.COMMUNITY: ArchetypeDefaults(
        archetype=Archetype.COMMUNITY,
        frequency_per_day=4,
        publishing_mode="approval_required",
        media_policy="image",
        max_post_length=1000,
        tone="casual",
        risk_level="medium",
        allowed_formats=["discussion", "poll", "user_content"],
    ),
    Archetype.AGGREGATOR: ArchetypeDefaults(
        archetype=Archetype.AGGREGATOR,
        frequency_per_day=10,
        publishing_mode="approval_required",
        media_policy="image",
        max_post_length=600,
        tone="informative",
        risk_level="medium",
        allowed_formats=["curated", "digest", "summary"],
    ),
}


def get_archetype_defaults(archetype: Archetype) -> ArchetypeDefaults:
    """Получить дефолтные настройки для архетипа."""
    return ARCHETYPE_DEFAULTS.get(archetype, ARCHETYPE_DEFAULTS[Archetype.NEWS])


def classify_risk_level(archetype: Archetype, theme: str = "") -> str:
    """Определить risk_level на основе архетипа и темы."""
    high_risk_themes = {"finance", "crypto", "medicine", "nutrition", "psychology", "biohacking"}
    if theme.lower() in high_risk_themes:
        return "high"
    return get_archetype_defaults(archetype).risk_level