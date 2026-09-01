"""Sprint 67.3 + 69.3: News Strategies — использует реальные RSS из channel.content_profile."""
import logging
from typing import List, Dict, Any, Optional

from backend.engines.rss_fetcher import fetch_rss_topics

logger = logging.getLogger(__name__)


class NewsResearchStrategy:
    """Research стратегия для новостных каналов."""
    
    def __init__(self, profile: Any):
        self.profile = profile
        # Sprint 69.3: читаем из content_profile (проброшен из channel)
        cp = getattr(profile, 'content_profile', None) or {}
        self.real_sources = cp.get('sources', [])
        self.freshness_hours = cp.get('freshness_hours', 24)
        if not self.freshness_hours:
            research_cfg = getattr(profile, 'research', None) or {}
            self.freshness_hours = research_cfg.get('freshness_hours', 24)
    
    async def collect_sources(self) -> List[Dict[str, Any]]:
        if self.real_sources and isinstance(self.real_sources, list):
            logger.info(f"Collecting {len(self.real_sources)} real RSS sources")
            return self.real_sources
        logger.warning("No real RSS sources in content_profile")
        return []
    
    async def extract_topics(self, sources: List[Dict]) -> List[Dict[str, Any]]:
        if not sources:
            logger.warning("No sources provided")
            return []
        topics = await fetch_rss_topics(sources, max_age_hours=self.freshness_hours, max_topics=10)
        logger.info(f"Extracted {len(topics)} topics from RSS")
        return topics


class NewsGenerationStrategy:
    def __init__(self, profile: Any):
        self.profile = profile
        content = getattr(profile, 'content', None) or {}
        self.max_length = content.get('max_length', 1200)
        self.formats = content.get('formats', ['breaking_news'])
        self.tone = getattr(profile, 'tone', 'informative') or 'informative'
    
    async def generate_post(self, topic: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        logger.info(f"Generating news post: {topic.get('title', 'unknown')[:60]}")
        return {
            "title": topic.get("title", ""),
            "content": topic.get("summary", ""),
            "url": topic.get("url", ""),
            "source": topic.get("source", ""),
            "format": self.formats[0] if self.formats else "breaking_news",
        }


class NewsMediaStrategy:
    def __init__(self, profile: Any):
        self.profile = profile
        media = getattr(profile, 'media', None) or {}
        self.preferred = media.get('preferred', ['image'])
    
    async def select_media(self, post: Dict[str, Any]) -> Optional[str]:
        logger.info(f"Selecting media for: {post.get('title', 'unknown')[:50]}")
        return None


class NewsPublishingStrategy:
    def __init__(self, profile: Any):
        self.profile = profile
        publishing = getattr(profile, 'publishing', None) or {}
        self.mode = publishing.get('mode', 'approval_required')
    
    async def publish(self, post: Dict[str, Any], media_url: Optional[str]) -> Dict[str, Any]:
        logger.info(f"Publishing (mode={self.mode}): {post.get('title', '')[:50]}")
        if self.mode == "auto":
            return {"success": True, "mode": "auto"}
        if self.mode == "approval_required":
            return {"success": True, "mode": "approval_required", "status": "draft"}
        return {"success": False, "mode": "manual", "reason": "Manual mode"}
