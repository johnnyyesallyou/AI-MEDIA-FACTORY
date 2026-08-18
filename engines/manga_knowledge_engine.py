"""Manga Knowledge Engine - Sprint 24 (session-aware).

Принимает сессию параметром — не создаёт свою.
"""
import logging
import uuid
from typing import Optional, List, Tuple, Set, NamedTuple
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from core.models.manga_knowledge import MangaTitle, MangaChapter
from engines.source_adapters.base_manga_adapter import MangaItem
from engines.title_normalizer import TitleNormalizer

logger = logging.getLogger(__name__)


class ProcessingResult(NamedTuple):
    """Результат обработки MangaItems."""
    new_titles: int
    new_chapters: int
    existing_chapters: int
    skipped_duplicates: int
    new_chapter_ids: List[str]  # ID новых MangaChapter (без объектов)


class MangaKnowledgeEngine:
    """
    Связывает MangaItem с базой знаний о манге.
    
    НЕ создаёт свою сессию — работает с переданной извне.
    НЕ делает commit/rollback — это ответственность вызывающего кода.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.normalizer = TitleNormalizer()

    def process_items(self, db, items: List[MangaItem]) -> ProcessingResult:
        """
        Обрабатывает список MangaItems в переданной сессии.
        
        Args:
            db: SQLAlchemy Session (управляется вызывающим кодом)
            items: список MangaItem
        
        Returns:
            ProcessingResult со списком ID новых MangaChapter
        """
        new_titles_count = 0
        new_chapters = 0
        existing_chapters = 0
        skipped_duplicates = 0
        new_chapter_ids: List[str] = []

        seen_chapters: Set[Tuple[str, str, str, str]] = set()
        titles_cache: dict = {}

        for item in items:
            # 1. Находим/создаём тайтл
            title, title_is_new = self._find_or_create_title(db, item, titles_cache)
            if title is None:
                continue

            if title_is_new:
                new_titles_count += 1

            # 2. In-memory дедупликация
            title_id = title.id
            chapter_key = (title_id, str(item.chapter), item.source, item.language)
            if chapter_key in seen_chapters:
                skipped_duplicates += 1
                continue

            # 3. Находим/создаём главу
            chapter_id, created = self._find_or_create_chapter(db, title_id, item)

            if created:
                new_chapters += 1
                seen_chapters.add(chapter_key)
                new_chapter_ids.append(chapter_id)
            else:
                existing_chapters += 1

        self.logger.info(
            f"Processed: {len(items)} items -> "
            f"{new_titles_count} new titles, {new_chapters} new chapters, "
            f"{existing_chapters} existing, {skipped_duplicates} batch duplicates"
        )

        return ProcessingResult(
            new_titles=new_titles_count,
            new_chapters=new_chapters,
            existing_chapters=existing_chapters,
            skipped_duplicates=skipped_duplicates,
            new_chapter_ids=new_chapter_ids,
        )

    def _find_or_create_title(
        self,
        db,
        item: MangaItem,
        cache: dict,
    ) -> Tuple[Optional[MangaTitle], bool]:
        normalized = self.normalizer.normalize(item.title)
        if not normalized:
            return None, False

        if normalized in cache:
            title = cache[normalized]
            self._update_external_ids(title, item)
            return title, False

        title = db.query(MangaTitle).filter(
            MangaTitle.canonical_title == normalized
        ).first()

        if title:
            self._update_external_ids(title, item)
            cache[normalized] = title
            return title, False

        title = MangaTitle(
            id=str(uuid.uuid4()),
            canonical_title=normalized,
            title_slug=item.title_slug,
            aliases=self._build_aliases(item),
            external_ids={item.source: item.external_id} if item.external_id else {},
            cover_url=item.cover_url,
        )
        db.add(title)
        db.flush()

        cache[normalized] = title
        return title, True

    def _find_or_create_chapter(
        self,
        db,
        title_id: str,
        item: MangaItem,
    ) -> Tuple[str, bool]:
        """Возвращает (chapter_id, is_new)."""
        chapter_number = str(item.chapter)

        existing = db.query(MangaChapter).filter(
            MangaChapter.manga_title_id == title_id,
            MangaChapter.chapter_number == chapter_number,
            MangaChapter.source == item.source,
            MangaChapter.language == item.language,
        ).first()

        if existing:
            return existing.id, False

        chapter_id = str(uuid.uuid4())
        chapter = MangaChapter(
            id=chapter_id,
            manga_title_id=title_id,
            chapter_number=chapter_number,
            source=item.source,
            external_id=item.external_id or "",
            language=item.language,
            url=item.url,
            published_at=item.upload_date,
        )
        db.add(chapter)

        try:
            db.flush()
            return chapter_id, True
        except IntegrityError:
            db.rollback()
            existing = db.query(MangaChapter).filter(
                MangaChapter.manga_title_id == title_id,
                MangaChapter.chapter_number == chapter_number,
                MangaChapter.source == item.source,
                MangaChapter.language == item.language,
            ).first()
            if existing:
                return existing.id, False
            raise

    def _update_external_ids(self, title: MangaTitle, item: MangaItem):
        """Сохраняет ID тайтла из источника (не главы!)."""
        title_id = item.title_external_id
        if not title_id:
            return
        external_ids = dict(title.external_ids or {})
        if item.source not in external_ids:
            external_ids[item.source] = title_id
            title.external_ids = external_ids

    def _build_aliases(self, item: MangaItem) -> dict:
        aliases = {}
        if item.title:
            aliases[item.language] = item.title
        if item.title_name_en and item.title_name_en != item.title:
            aliases["en"] = item.title_name_en
        return aliases