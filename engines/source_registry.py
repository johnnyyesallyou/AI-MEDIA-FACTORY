"""Source Registry - Sprint 53.

Unified registry of all content sources with self-describing capabilities.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SourceDefinition:
    """Self-describing source definition."""
    id: str
    name: str
    content_types: tuple  # ("manga", "anime", "news")
    topics: tuple          # ("new_chapters", "news", "releases")
    languages: tuple       # ("ru", "en")
    adapter: str           # adapter class name
    capabilities: tuple    # ("chapters", "covers", "descriptions")
    requires_api_key: bool = False
    api_key_env_var: Optional[str] = None
    rate_limit: int = 100  # requests per hour
    
    def supports(self, content_type: str, topic: str = None, language: str = None) -> bool:
        """Check if source supports given content type/topic/language."""
        if content_type not in self.content_types:
            return False
        if topic and topic not in self.topics:
            return False
        if language and language not in self.languages:
            return False
        return True


# Registry of all available sources
SOURCES: Dict[str, SourceDefinition] = {
    # Manga sources
    "remanga": SourceDefinition(
        id="remanga",
        name="ReManga",
        content_types=("manga",),
        topics=("new_chapters", "releases"),
        languages=("ru", "en"),
        adapter="ReMangaAdapter",
        capabilities=("chapters", "covers", "descriptions", "genres"),
    ),
    "mangadex": SourceDefinition(
        id="mangadex",
        name="MangaDex",
        content_types=("manga",),
        topics=("new_chapters", "releases"),
        languages=("ru", "en", "ja"),
        adapter="MangaDexAdapter",
        capabilities=("chapters", "covers", "descriptions", "genres"),
    ),
    "readmanga": SourceDefinition(
        id="readmanga",
        name="ReadManga",
        content_types=("manga",),
        topics=("new_chapters",),
        languages=("ru",),
        adapter="ReadMangaAdapter",
        capabilities=("chapters", "covers"),
    ),
    
    # Anime sources
    "anilist": SourceDefinition(
        id="anilist",
        name="AniList",
        content_types=("anime",),
        topics=("news", "releases", "seasonal"),
        languages=("ru", "en", "ja"),
        adapter="AniListAdapter",
        capabilities=("episodes", "covers", "descriptions", "genres", "studios"),
    ),
    "myanimelist": SourceDefinition(
        id="myanimelist",
        name="MyAnimeList",
        content_types=("anime",),
        topics=("news", "releases"),
        languages=("en", "ja"),
        adapter="MyAnimeListAdapter",
        capabilities=("episodes", "covers", "descriptions", "genres"),
    ),
    
    # News sources
    "habr": SourceDefinition(
        id="habr",
        name="Habr",
        content_types=("news",),
        topics=("technology", "programming", "ai"),
        languages=("ru",),
        adapter="HabrRSSAdapter",
        capabilities=("articles", "summaries", "covers"),
    ),
    "vc": SourceDefinition(
        id="vc",
        name="VC.ru",
        content_types=("news",),
        topics=("technology", "business", "startups"),
        languages=("ru",),
        adapter="VCRSSAdapter",
        capabilities=("articles", "summaries", "covers"),
    ),
    "techcrunch": SourceDefinition(
        id="techcrunch",
        name="TechCrunch",
        content_types=("news",),
        topics=("technology", "startups", "ai"),
        languages=("en",),
        adapter="TechCrunchRSSAdapter",
        capabilities=("articles", "summaries", "covers"),
    ),
    "theverge": SourceDefinition(
        id="theverge",
        name="The Verge",
        content_types=("news",),
        topics=("technology", "gadgets"),
        languages=("en",),
        adapter="TheVergeRSSAdapter",
        capabilities=("articles", "summaries", "covers"),
    ),
}


class SourceRegistry:
    """Registry for querying available sources."""
    
    @staticmethod
    def get_source(source_id: str) -> Optional[SourceDefinition]:
        """Get source by ID."""
        return SOURCES.get(source_id)
    
    @staticmethod
    def get_sources_for(
        content_type: str,
        topic: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[SourceDefinition]:
        """Get all sources that support given content type/topic/language."""
        result = []
        for source in SOURCES.values():
            if source.supports(content_type, topic, language):
                result.append(source)
        return result
    
    @staticmethod
    def list_all() -> List[SourceDefinition]:
        """List all available sources."""
        return list(SOURCES.values())
    
    @staticmethod
    def validate_sources(source_ids: List[str]) -> tuple[List[str], List[str]]:
        """Validate list of source IDs. Returns (valid, invalid)."""
        valid = []
        invalid = []
        for sid in source_ids:
            if sid in SOURCES:
                valid.append(sid)
            else:
                invalid.append(sid)
        return valid, invalid