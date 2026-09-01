"""Sprint 69.3: Simple RSS fetcher для NewsResearchStrategy."""
import logging
from typing import List, Dict, Any
import feedparser
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


async def fetch_rss_topics(sources: List[Dict[str, Any]], max_age_hours: int = 24, max_topics: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch topics from RSS sources.
    
    Args:
        sources: list of {"name": "...", "url": "...", "type": "rss"}
        max_age_hours: only include entries from last N hours
        max_topics: max total topics to return
    
    Returns:
        list of {"title": "...", "summary": "...", "url": "...", "source": "..."}
    """
    topics = []
    cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
    
    for src in sources:
        if src.get("type") != "rss":
            continue
        
        url = src.get("url")
        name = src.get("name", "Unknown")
        
        try:
            logger.info(f"Fetching RSS: {name} ({url})")
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_topics]:
                # Parse published date
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                
                # Skip old entries
                if published and published < cutoff:
                    continue
                
                topic = {
                    "title": entry.get("title", "").strip(),
                    "summary": entry.get("summary", entry.get("description", "")).strip()[:500],
                    "url": entry.get("link", ""),
                    "source": name,
                    "published": published.isoformat() if published else None,
                }
                topics.append(topic)
                
                if len(topics) >= max_topics:
                    break
            
            logger.info(f"  {name}: {len([t for t in topics if t['source'] == name])} topics")
        
        except Exception as e:
            logger.error(f"Failed to fetch {name}: {e}")
    
    logger.info(f"Total: {len(topics)} topics from {len(sources)} sources")
    return topics[:max_topics]