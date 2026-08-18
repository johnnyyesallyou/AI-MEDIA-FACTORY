"""Manga Image Resolver - source-first обложки манги."""
import logging
import json
from typing import Optional, Dict, Any
from pathlib import Path

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from engines.asset.manager import AssetManager

logger = logging.getLogger(__name__)


class MangaImageResolver:
    """
    Source-first image resolver for manga chapters.
    
    Priority:
    1. Cover URL из metadata (manga_cover_url)
    2. Fallback на AI-генерацию (не используется)
    3. None (оставляем без картинки)
    
    Sprint 15: Manga Chapter Release
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.asset_manager = AssetManager()
    
    def resolve_all_research(self, limit: int = 100) -> Dict[str, Any]:
        """
        Process all manga research items and download covers.
        
        Args:
            limit: Max items to process
        
        Returns:
            Stats dict
        """
        db = SessionLocal()
        processed = 0
        downloaded = 0
        failed = 0
        
        try:
            # Get research items without asset_id
            items = db.query(ContentORM).filter(
                ContentORM.status == "research",
                ContentORM.asset_id == None,
                ContentORM.source_url.like("%remanga.org%")
            ).limit(limit).all()
            
            self.logger.info(f"Processing {len(items)} manga research items")
            
            for item in items:
                try:
                    processed += 1
                    
                    # Parse manga metadata from source_text
                    metadata = self._parse_metadata(item.source_text)
                    if not metadata:
                        self.logger.warning(f"No metadata for {item.id}")
                        failed += 1
                        continue
                    
                    cover_url = metadata.get("manga_cover_url")
                    if not cover_url:
                        self.logger.warning(f"No cover_url for {item.headline}")
                        failed += 1
                        continue
                    
                    # Sanitize URL (remove <date> artifacts)
                    cover_url = self._sanitize_url(cover_url)
                    
                    # Download via AssetManager
                    self.logger.info(f"Downloading cover for {item.headline[:50]}...")
                    asset = self.asset_manager.save_from_url(
                        image_url=cover_url,
                        content_id=item.id,
                        prompt=metadata.get("manga_title_name", ""),
                        model="manga_cover",
                        width=400,
                        height=600
                    )
                    
                    if asset:
                        item.asset_id = asset.id
                        item.image_url = asset.public_url
                        db.commit()
                        downloaded += 1
                        self.logger.info(f"  Cover saved: {asset.public_url}")
                    else:
                        failed += 1
                        self.logger.error(f"  Failed to download cover")
                
                except Exception as e:
                    failed += 1
                    self.logger.error(f"Error processing {item.id}: {e}")
                    db.rollback()
            
            stats = {
                "status": "ok",
                "processed": processed,
                "downloaded": downloaded,
                "failed": failed,
            }
            
            self.logger.info(
                f"MangaImageResolver finished: {processed} processed, "
                f"{downloaded} downloaded, {failed} failed"
            )
            
            return stats
        
        except Exception as e:
            db.rollback()
            self.logger.exception(f"MangaImageResolver failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()
    
    def _parse_metadata(self, source_text: Optional[str]) -> Optional[Dict[str, Any]]:
        """Parse manga metadata JSON from source_text."""
        if not source_text:
            return None
        
        try:
            return json.loads(source_text)
        except json.JSONDecodeError as e:
            self.logger.warning(f"Invalid JSON in source_text: {e}")
            return None
    
    def _sanitize_url(self, url: str) -> str:
        """
        Sanitize URL by removing artifacts like <29.04.2026>.
        
        Example:
            https://remanga.org/manga/<29.04.2026>shark_/...
            → https://remanga.org/manga/shark_/...
        """
        import re
        # Remove <date> patterns
        cleaned = re.sub(r'<[^>]+>', '', url)
        
        if cleaned != url:
            self.logger.info(f"URL sanitized: {url[:80]} → {cleaned[:80]}")
        
        return cleaned
