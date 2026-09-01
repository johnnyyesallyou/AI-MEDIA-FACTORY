"""Sprint 68.2: Strategy Suggestor — предлагает стратегии на основе theme/archetype."""
import logging
from typing import Dict, Any, List, Optional

from core.models.archetypes import Archetype, get_archetype_defaults
from backend.engines.source_recommendations import get_source_urls

logger = logging.getLogger(__name__)


# Маппинг theme/niche → рекомендуемые research sources
THEME_SOURCES: Dict[str, List[str]] = {
    # Technology
    "technology": ["rss", "web", "hacker_news", "techcrunch", "arstechnica"],
    "ai": ["rss", "web", "arxiv", "papers_with_code", "huggingface"],
    "gaming": ["rss", "web", "steam", "ign", "gamespot", "reddit_r_gaming"],
    
    # Entertainment
    "entertainment": ["rss", "web", "reddit", "twitter"],
    "manga": ["rss", "web", "mangadex", "anilist", "myanimelist"],
    "anime": ["rss", "web", "anilist", "myanimelist", "crunchyroll"],
    "movies": ["rss", "web", "imdb", "rottentomatoes", "letterboxd"],
    "cats": ["web", "reddit_r_cats", "imgur", "tiktok_trending"],
    
    # Knowledge
    "science": ["rss", "web", "arxiv", "nature", "science_daily"],
    "education": ["rss", "web", "coursera", "khan_academy"],
    
    # Business/Finance
    "business": ["rss", "web", "techcrunch", "venture_beat", "producthunt"],
    "finance": ["rss", "web", "bloomberg", "cnbc", "financial_times"],
    "crypto": ["rss", "web", "coindesk", "cointelegraph", "reddit_r_crypto"],
    
    # Lifestyle
    "fitness": ["rss", "web", "reddit_r_fitness", "youtube_trending"],
    "cooking": ["rss", "web", "reddit_r_cooking", "food_blogs"],
    "travel": ["rss", "web", "reddit_r_travel", "travel_blogs"],
    
    # General
    "news": ["rss", "web"],
    "general": ["rss", "web"],
}


class StrategySuggestor:
    """
    Предлагает стратегии для канала на основе theme/archetype/risk.
    
    Возвращает:
    - frequency_per_day (из ArchetypeDefaults, скорректированный по risk)
    - content_formats (из ArchetypeDefaults)
    - media_policy (из ArchetypeDefaults)
    - research_sources (из THEME_SOURCES по theme/niche)
    """
    
    def suggest(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Предложить стратегии на основе классификации."""
        try:
            archetype = Archetype(classification.get("archetype", "news"))
        except ValueError:
            archetype = Archetype.NEWS
        
        defaults = get_archetype_defaults(archetype)
        theme = classification.get("theme", "general")
        niche = classification.get("niche", "")
        risk = classification.get("risk_level", "medium")
        
        # Frequency: корректируем по risk (high = меньше публикаций для ручного ревью)
        frequency = defaults.frequency_per_day
        if risk == "high":
            frequency = max(1, frequency // 2)
        elif risk == "low" and archetype in (Archetype.VIRAL, Archetype.ENTERTAINMENT):
            frequency = min(12, frequency + 2)
        
        # Research sources: сначала niche, потом theme, fallback ["rss", "web"]
        sources = (
            THEME_SOURCES.get(niche) or
            THEME_SOURCES.get(theme) or
            ["rss", "web"]
        )
        
        # Sprint 68.3: реальные URLs вместо строк
        source_urls = get_source_urls(niche, theme, limit=5)
        
        strategy = {
            "frequency_per_day": frequency,
            "content_formats": defaults.allowed_formats,
            "media_policy": defaults.media_policy,
            "tone": defaults.tone,
            "max_post_length": defaults.max_post_length,
            "research_sources": sources,  # строки (для совместимости)
            "research_source_urls": source_urls,  # Sprint 68.3: реальные URLs
            "publishing_mode": classification.get("publishing_mode", defaults.publishing_mode),
        }
        
        logger.info(
            f"Strategy suggested for {archetype.value}/{theme}: "
            f"freq={frequency}, sources={len(sources)}, mode={strategy['publishing_mode']}"
        )
        return strategy