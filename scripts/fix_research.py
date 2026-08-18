import pathlib

new_content = r'''"""Manga Research Job - orchestrates source adapters and chapter detection."""
import logging
from typing import Any, Dict, List
from datetime import datetime
import uuid
import json

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from engines.source_adapters import ReMangaAdapter, MangaDexAdapter
from engines.chapter_detector import ChapterDetector

logger = logging.getLogger(__name__)


class MangaResearchJob:
    """Orchestrates manga source adapters and chapter detection."""
    
    MANGA_CHANNEL_ID = "manga-channel-001"
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.adapters = [
            ReMangaAdapter(),
            MangaDexAdapter(),
        ]
        self.detector = ChapterDetector()
    
    def run(self, channel: ChannelORM = None, limit_per_source: int = 20) -> Dict[str, Any]:
        self.logger.info(f"MangaResearchJob started (limit_per_source={limit_per_source})")
        
        db = SessionLocal()
        
        try:
            total_fetched = 0
            all_new_items = []
            all_existing_items = []
            research_items_created = 0
            
            for adapter in self.adapters:
                source_name = adapter.get_source_name()
                self.logger.info(f"Fetching from {source_name}...")
                
                try:
                    items = adapter.fetch_latest_chapters(limit=limit_per_source)
                    total_fetched += len(items)
                    self.logger.info(f"  Fetched {len(items)} chapters from {source_name}")
                    
                    new_items, existing_items = self.detector.detect_new_chapters(
                        items,
                        update_state=True
                    )
                    
                    all_new_items.extend(new_items)
                    all_existing_items.extend(existing_items)
                    
                    self.logger.info(
                        f"  {source_name}: {len(new_items)} new, {len(existing_items)} existing"
                    )
                
                except Exception as e:
                    self.logger.error(f"Failed to fetch from {source_name}: {e}")
                    continue
            
            if all_new_items:
                self.logger.info(f"Creating {len(all_new_items)} research items...")
                
                manga_channel = self._get_manga_channel(db)
                if not manga_channel:
                    self.logger.error("Manga channel not found!")
                    return {"status": "failed", "error": "Manga channel not found"}
                
                for item in all_new_items:
                    try:
                        research_item = self._create_research_item(db, item, manga_channel)
                        if research_item:
                            research_items_created += 1
                    except Exception as e:
                        self.logger.error(f"Failed to create research item: {e}")
                        continue
                
                db.commit()
            
            stats = {
                "status": "ok",
                "total_fetched": total_fetched,
                "new_chapters": len(all_new_items),
                "existing_chapters": len(all_existing_items),
                "research_items_created": research_items_created,
            }
            
            self.logger.info(
                f"MangaResearchJob finished: {stats['total_fetched']} fetched, "
                f"{stats['new_chapters']} new, {stats['research_items_created']} created"
            )
            
            return stats
        
        except Exception as e:
            db.rollback()
            self.logger.exception(f"MangaResearchJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()
    
    def _get_manga_channel(self, db: SessionLocal) -> ChannelORM:
        """Get manga channel (try by name first, fallback by ID, then first active)."""
        # Try by name
        channel = db.query(ChannelORM).filter(
            ChannelORM.name == "????? ? ????? ?????"
        ).first()
        
        if channel:
            self.logger.info(f"Found manga channel by name: {channel.name}")
            return channel
        
        # Try by ID
        channel = db.query(ChannelORM).filter(
            ChannelORM.id == self.MANGA_CHANNEL_ID
        ).first()
        
        if channel:
            self.logger.info(f"Found manga channel by ID: {channel.name}")
            return channel
        
        # Fallback to first active
        self.logger.warning("Manga channel not found by name/ID, using first active as fallback")
        return db.query(ChannelORM).filter(
            ChannelORM.is_active == True
        ).first()
    
    def _create_research_item(
        self,
        db: SessionLocal,
        item: Any,
        channel: ChannelORM
    ) -> ContentORM:
        headline = f"\U0001f4da \u041d\u043e\u0432\u0430\u044f \u0433\u043b\u0430\u0432\u0430: {item.title_name}"
        if item.chapter_number:
            headline += f" \u2014 \u0433\u043b\u0430\u0432\u0430 {item.chapter_number}"
        
        draft_text = f"**{item.title_name}**\n\n"
        if item.chapter_number:
            draft_text += f"\U0001f4d6 \u0413\u043b\u0430\u0432\u0430 {item.chapter_number}\n\n"
        if item.title_name_en:
            draft_text += f"\U0001f310 {item.title_name_en}\n\n"
        draft_text += f"\U0001f517 [\u0427\u0438\u0442\u0430\u0442\u044c \u043d\u0430 {item.source}]({item.chapter_url or item.title_url})\n\n"
        draft_text += f"#\u043c\u0430\u043d\u0433\u0430 #\u043d\u043e\u0432\u0430\u044f\u0433\u043b\u0430\u0432\u0430 #{item.source}"
        
        manga_metadata = {
            "type": "manga_chapter",
            "manga_source": item.source,
            "manga_title_id": item.title_id,
            "manga_title_name": item.title_name,
            "manga_title_name_en": item.title_name_en,
            "manga_chapter_number": item.chapter_number,
            "manga_chapter_id": item.chapter_id,
            "manga_cover_url": item.cover_url,
            "manga_title_url": item.title_url,
            "manga_chapter_url": item.chapter_url,
            "manga_upload_date": item.upload_date.isoformat() if item.upload_date else None,
        }
        
        content = ContentORM(
            id=str(uuid.uuid4()),
            channel_id=channel.id,
            headline=headline,
            draft_text=draft_text,
            source_url=item.chapter_url or item.title_url,
            source_text=json.dumps(manga_metadata, ensure_ascii=False),
            status="research",
            created_at=datetime.utcnow(),
        )
        
        db.add(content)
        return content
'''

f = pathlib.Path("/app/backend/automation/jobs/manga_research_job.py")
f.write_text(new_content, encoding="utf-8")

# Verify no BOM
with open(f, "rb") as fh:
    first3 = fh.read(3)
    if first3 == b"\xef\xbb\xbf":
        print("ERROR: BOM still present!")
    else:
        print(f"OK: No BOM, file rewritten ({f.stat().st_size} bytes)")

# Syntax check
import ast
try:
    ast.parse(new_content)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
