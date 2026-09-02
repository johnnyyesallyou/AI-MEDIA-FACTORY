"""Sprint 69.6: Deduplicator — фильтрует topics по source_url уже опубликованным."""
import logging
from typing import List, Dict, Any

from core.database import SessionLocal
from sqlalchemy import text

logger = logging.getLogger(__name__)


def filter_new_topics(channel_id: str, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Фильтрует topics — оставляет только те, у которых source_url ещё не публиковался
    для этого канала.
    
    Args:
        channel_id: UUID канала
        topics: список {"title": ..., "url": ..., "source": ..., ...}
    
    Returns:
        Список topics без дубликатов
    """
    if not topics:
        return []
    
    # Извлекаем URLs из topics
    urls = [t.get("url") for t in topics if t.get("url")]
    if not urls:
        logger.warning("No URLs in topics, skipping dedup")
        return topics
    
    # Запрашиваем уже опубликованные URLs для этого канала
    db = SessionLocal()
    try:
        placeholders = ",".join([f":u{i}" for i in range(len(urls))])
        params = {f"u{i}": url for i, url in enumerate(urls)}
        params["channel_id"] = channel_id
        
        query = f"""
            SELECT DISTINCT source_url 
            FROM content 
            WHERE channel_id = :channel_id 
              AND source_url IN ({placeholders})
              AND source_url IS NOT NULL
              AND source_url != ''
              AND (status = 'published' OR telegram_message_id IS NOT NULL OR published_at IS NOT NULL)
        """
        
        result = db.execute(text(query), params)
        existing_urls = {row[0] for row in result.fetchall()}
        
        logger.info(f"Dedup check: {len(existing_urls)} existing URLs found out of {len(urls)} topics")
        
        # Фильтруем topics
        new_topics = [
            t for t in topics 
            if not t.get("url") or t.get("url") not in existing_urls
        ]
        
        skipped = len(topics) - len(new_topics)
        if skipped > 0:
            logger.info(f"Dedup: skipped {skipped} duplicate topics, kept {len(new_topics)} new")
        else:
            logger.info(f"Dedup: all {len(new_topics)} topics are new")
        
        return new_topics
    
    except Exception as e:
        logger.error(f"Dedup failed, returning all topics: {e}")
        return topics
    finally:
        db.close()