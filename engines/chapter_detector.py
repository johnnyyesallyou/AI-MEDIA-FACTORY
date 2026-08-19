"""Chapter Detector - identifies NEW chapters by comparing with stored state."""
from typing import List, Tuple, Dict
from datetime import datetime
import logging

from core.database import SessionLocal
from core.models.manga_source_state_orm import MangaSourceStateORM
from engines.source_adapters.base import SourceItem

logger = logging.getLogger(__name__)


class ChapterDetector:
    """
    Detects new manga chapters by comparing fetched chapters with stored state.
    
    Logic:
    1. Group items by (source, title_id) - one title may have multiple chapters
    2. For each unique title, find MAX chapter_number
    3. Check if (source, title_id) exists in manga_source_states
    4. If exists: compare max_chapter > last_chapter → NEW
    5. If not exists: NEW (first time seeing this title)
    6. Update state with max chapter info
    
    Returns:
        Tuple[List[SourceItem], List[SourceItem]]: (new_items, existing_items)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def detect_new_chapters(
        self,
        items: List[SourceItem],
        update_state: bool = True
    ) -> Tuple[List[SourceItem], List[SourceItem]]:
        """
        Detect which chapters are NEW.
        
        Args:
            items: List of fetched SourceItem objects
            update_state: Whether to update manga_source_states
        
        Returns:
            Tuple of (new_items, existing_items)
        """
        if not items:
            return [], []
        
        db = SessionLocal()
        new_items = []
        existing_items = []
        
        try:
            # Group items by (source, title_id)
            grouped = self._group_by_title(items)
            
            self.logger.info(f"Grouped {len(items)} items into {len(grouped)} unique titles")
            
            for (source, title_id), title_items in grouped.items():
                # Find max chapter for this title
                max_item = self._find_max_chapter(title_items)
                
                # Check if new
                is_new, state = self._check_if_new(db, max_item)
                
                if is_new:
                    # Mark ALL chapters of this title as new
                    for item in title_items:
                        item.is_new = True
                        new_items.append(item)
                    
                    if update_state:
                        self._update_state(db, max_item, state)
                else:
                    # Mark ALL chapters of this title as existing
                    for item in title_items:
                        item.is_new = False
                        existing_items.append(item)
            
            db.commit()
            
            self.logger.info(
                f"ChapterDetector: {len(new_items)} new, {len(existing_items)} existing"
            )
            
            return new_items, existing_items
        
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error detecting new chapters: {e}")
            raise
        finally:
            db.close()
    
    def _group_by_title(self, items: List[SourceItem]) -> Dict[Tuple[str, str], List[SourceItem]]:
        """Group items by (source, title_id)."""
        grouped = {}
        for item in items:
            key = (item.source, item.title_id)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item)
        return grouped
    
    def _find_max_chapter(self, items: List[SourceItem]) -> SourceItem:
        """Find item with max chapter_number."""
        def get_chapter_num(item):
            try:
                return float(item.chapter_number) if item.chapter_number else 0
            except (ValueError, TypeError):
                return 0
        
        return max(items, key=get_chapter_num)
    
    def _check_if_new(
        self,
        db: SessionLocal,
        item: SourceItem
    ) -> Tuple[bool, MangaSourceStateORM]:
        """
        Check if a chapter is new by comparing with stored state.
        
        Returns:
            Tuple of (is_new, existing_state_or_None)
        """
        state = db.query(MangaSourceStateORM).filter(
            MangaSourceStateORM.source == item.source,
            MangaSourceStateORM.title_id == item.title_id
        ).first()
        
        if not state:
            # First time seeing this title
            self.logger.debug(f"New title: {item.title_name} (first time)")
            return True, None
        
        # Compare chapter numbers
        try:
            new_chapter = float(item.chapter_number) if item.chapter_number else 0
            last_chapter = float(state.last_chapter_number) if state.last_chapter_number else 0
            
            is_new = new_chapter > last_chapter
            
            if is_new:
                self.logger.debug(
                    f"New chapter: {item.title_name} chapter {item.chapter_number} "
                    f"(was {state.last_chapter_number})"
                )
            else:
                self.logger.debug(
                    f"Existing chapter: {item.title_name} chapter {item.chapter_number} "
                    f"(last was {state.last_chapter_number})"
                )
            
            return is_new, state
        
        except (ValueError, TypeError) as e:
            # If chapter numbers are not numeric, compare as strings
            is_new = item.chapter_number != state.last_chapter_number
            return is_new, state
    
    def _update_state(
        self,
        db: SessionLocal,
        item: SourceItem,
        existing_state: MangaSourceStateORM
    ) -> None:
        """
        Update or create manga_source_state for a title.
        """
        if existing_state:
            # Update existing state
            existing_state.last_chapter_number = item.chapter_number
            existing_state.last_chapter_id = item.chapter_id
            existing_state.last_chapter_url = item.chapter_url
            existing_state.last_seen_at = datetime.utcnow()
            existing_state.total_chapters_seen += 1
            
            # Update metadata if provided
            if item.cover_url:
                existing_state.cover_url = item.cover_url
            if item.title_url:
                existing_state.title_url = item.title_url
            
            self.logger.debug(f"Updated state for {item.title_name}")
        else:
            # Create new state
            new_state = MangaSourceStateORM(
                id=f"{item.source}_{item.title_id}",
                source=item.source,
                title_id=item.title_id,
                title_name=item.title_name,
                title_name_en=item.title_name_en,
                title_slug=item.title_slug,
                title_url=item.title_url,
                cover_url=item.cover_url,
                last_chapter_number=item.chapter_number,
                last_chapter_id=item.chapter_id,
                last_chapter_url=item.chapter_url,
                last_seen_at=datetime.utcnow(),
                first_seen_at=datetime.utcnow(),
                total_chapters_seen=1,
            )
            
            db.add(new_state)
            self.logger.debug(f"Created state for {item.title_name}")
