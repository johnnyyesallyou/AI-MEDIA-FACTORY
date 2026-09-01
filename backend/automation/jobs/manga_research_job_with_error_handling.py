"""
Sprint 66.5.5: Manga Research Job with Error Handling (Integration Example)

Пример того, как использовать JobErrorHandler в существующих job'ах.
Оригинальный файл: backend/automation/jobs/manga_research_job.py
"""

import logging
from typing import Any, Dict
from datetime import datetime
import uuid
import json

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from core.models.manga_knowledge import MangaTitle, MangaChapter
from engines.source_adapters.manga_registry import MangaRegistry
from engines.manga_knowledge_engine import MangaKnowledgeEngine
from engines.cross_source_enricher import CrossSourceEnricher
from backend.automation.job_error_handler import JobErrorHandler
from backend.core.error_logger import get_error_logger

logger = logging.getLogger(__name__)


class MangaResearchJobWithErrorHandling:
    """
    Orchestrates manga research via Knowledge Layer.
    WITH Sprint 66.5 error tracking.
    """

    MANGA_CHANNEL_ID = "manga-channel-001"

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.knowledge = MangaKnowledgeEngine()
        self.enricher = CrossSourceEnricher()

    def run(
        self,
        channel: ChannelORM = None,
        limit_per_source: int = 20,
        execution_id: str = None,
    ) -> Dict[str, Any]:
        """
        Run manga research with automatic error handling.
        
        Args:
            channel: Channel ORM object
            limit_per_source: Limit for each source
            execution_id: Execution ID for tracing
        
        Returns:
            Result dict with status and metrics
        """
        
        # Получаем channel_id для ошибок
        channel_id = channel.id if channel else self.MANGA_CHANNEL_ID
        
        # Используем контекстный менеджер для логирования ошибок
        with JobErrorHandler(
            channel_id=channel_id,
            pipeline="research",
            job="fetch_manga_sources",
            execution_id=execution_id,
            max_attempts=3,
        ) as ctx:
            self.logger.info(f"MangaResearchJob started (limit_per_source={limit_per_source})")

            db = SessionLocal()

            try:
                manga_channel = channel or self._get_manga_channel(db)
                if not manga_channel:
                    self.logger.error("Manga channel not found!")
                    ctx.log_error(Exception("Manga channel not found"))
                    return {"status": "failed", "error": "Manga channel not found"}

                profile = manga_channel.content_profile or {}
                sources = profile.get("sources") or MangaRegistry.available_sources()
                available = MangaRegistry.available_sources()
                sources = [s for s in sources if s in available]

                if not sources:
                    self.logger.warning("No valid sources, using all available")
                    sources = available

                self.logger.info(f"Fetching from sources: {sources}")

                # 1. Fetch chapters через MangaRegistry
                try:
                    all_items = MangaRegistry.fetch_all(limit=limit_per_source, sources=sources)
                except Exception as e:
                    self.logger.error(f"Failed to fetch items: {e}")
                    ctx.log_error(e)
                    raise

                if not all_items:
                    self.logger.warning("No items fetched")
                    return {"status": "ok", "new_chapters": 0, "sources": sources}

                self.logger.info(f"Fetched {len(all_items)} items from {len(sources)} sources")

                # 2. Передаём в Knowledge Layer (в ТОЙ ЖЕ сессии)
                try:
                    result = self.knowledge.process_items(db, all_items)
                except Exception as e:
                    self.logger.error(f"Knowledge Layer processing failed: {e}")
                    ctx.log_error(e)
                    raise

                self.logger.info(
                    f"Knowledge Layer: {result.new_titles} new titles, "
                    f"{result.new_chapters} new chapters, "
                    f"{result.existing_chapters} existing"
                )

                # Sprint 26: Enrichment для новых тайтлов
                if result.new_chapter_ids:
                    try:
                        self._enrich_new_titles(db, result.new_chapter_ids)
                    except Exception as e:
                        self.logger.warning(f"Enrichment failed: {e}")
                        ctx.log_error(e, context={"severity": "warning"})

                if not result.new_chapter_ids:
                    return {
                        "status": "ok",
                        "new_chapters": 0,
                        "existing": result.existing_chapters,
                        "sources": sources,
                    }

                # 3. Загружаем MangaChapter объекты из текущей сессии
                try:
                    new_chapters = db.query(MangaChapter).filter(
                        MangaChapter.id.in_(result.new_chapter_ids)
                    ).all()
                except Exception as e:
                    self.logger.error(f"Failed to query chapters: {e}")
                    ctx.log_error(e)
                    raise

                self.logger.info(f"Creating {len(new_chapters)} ContentORM items...")
                research_items_created = 0

                for chapter in new_chapters:
                    try:
                        title = db.query(MangaTitle).filter(
                            MangaTitle.id == chapter.manga_title_id
                        ).first()
                        if not title:
                            continue

                        research_item = self._create_research_item(
                            db=db,
                            chapter=chapter,
                            title=title,
                            channel=manga_channel,
                        )
                        if research_item:
                            research_items_created += 1
                    except Exception as e:
                        self.logger.error(f"Failed to create research item: {e}")
                        ctx.log_error(e, context={"chapter_id": chapter.id})

                db.commit()

                duration = ctx.get_duration()
                final_result = {
                    "status": "ok",
                    "new_chapters": research_items_created,
                    "existing": result.existing_chapters,
                    "new_titles": result.new_titles,
                    "sources": sources,
                    "duration_seconds": duration,
                    "execution_id": ctx.execution_id,
                }

                self.logger.info(f"MangaResearchJob completed: {final_result}")
                return final_result

            except Exception as e:
                db.rollback()
                self.logger.exception(f"MangaResearchJob failed: {e}")
                # Ошибка уже залогирована в JobErrorHandler.__exit__
                return {
                    "status": "failed",
                    "error": str(e),
                    "execution_id": ctx.execution_id,
                }
            finally:
                db.close()

    def _enrich_new_titles(self, db, chapter_ids):
        """Обогащает тайтлы, связанные с новыми главами."""
        from core.models.manga_knowledge import MangaChapter, MangaTitle
        
        # Находим уникальные manga_title_id
        chapters = db.query(MangaChapter).filter(
            MangaChapter.id.in_(chapter_ids)
        ).all()
        title_ids = list(set(ch.manga_title_id for ch in chapters))
        
        # Загружаем тайтлы без описания
        titles = db.query(MangaTitle).filter(
            MangaTitle.id.in_(title_ids),
            (MangaTitle.description == None) | (MangaTitle.description == "")
        ).all()
        
        enriched = 0
        for title in titles:
            try:
                sources_data = self.enricher._build_sources_data(title)
                if sources_data != (title.sources_data or {}):
                    title.sources_data = sources_data
                
                # Sprint 51: используем enrich() вместо merge()
                self.enricher.enrich(title)
                desc = title.description
                genres = title.genres
                cover = title.cover_url
                
                if desc and not title.description:
                    title.description = desc
                if genres and not title.genres:
                    title.genres = genres
                if cover and not title.cover_url:
                    title.cover_url = cover
                
                if desc or genres:
                    enriched += 1
                    self.logger.info(f"Enriched: {title.canonical_title[:40]}")
            except Exception as e:
                self.logger.warning(f"Enrichment failed for {title.canonical_title[:40]}: {e}")
        
        if enriched:
            self.logger.info(f"Enriched {enriched} new titles")

    def _get_manga_channel(self, db) -> ChannelORM:
        channel = db.query(ChannelORM).filter(
            ChannelORM.id == self.MANGA_CHANNEL_ID
        ).first()
        if not channel:
            channel = db.query(ChannelORM).filter(
                ChannelORM.name.like("%Манга%")
            ).first()
        return channel

    def _create_research_item(
        self,
        db: SessionLocal,
        chapter: MangaChapter,
        title: MangaTitle,
        channel: ChannelORM,
    ) -> ContentORM:
        """Создаёт ContentORM со ссылкой на MangaChapter."""
        title_name = title.canonical_title
        if title.aliases and chapter.language in title.aliases:
            title_name = title.aliases[chapter.language]

        headline = f"\U0001f4da \u041d\u043e\u0432\u0430\u044f \u0433\u043b\u0430\u0432\u0430: {title_name} \u2014 \u0433\u043b\u0430\u0432\u0430 {chapter.chapter_number}"

        metadata = {
            "type": "manga_chapter",
            "manga_source": chapter.source,
            "manga_title_id": title.id,
            "manga_title_canonical": title.canonical_title,
            "manga_title_aliases": title.aliases or {},
            "manga_title_slug": title.title_slug,
            "manga_title_name": title_name,
            "manga_title_external_ids": title.external_ids or {},
            "manga_chapter_number": chapter.chapter_number,
            "manga_chapter_id": chapter.id,
            "manga_chapter_external_id": chapter.external_id,
            "manga_cover_url": title.cover_url,
            "manga_chapter_url": chapter.url,
            "manga_upload_date": chapter.published_at.isoformat() if chapter.published_at else None,
        }

        research_item = ContentORM(
            id=str(uuid.uuid4()),
            channel_id=channel.id,
            headline=headline,
            draft_text=headline,
            source_url=chapter.url or "",
            source_text=json.dumps(metadata, ensure_ascii=False),
            manga_chapter_id=chapter.id,
            status="research",
            created_at=datetime.utcnow(),
        )
        db.add(research_item)
        self.logger.debug(f"Created research item: {headline[:50]} (chapter_id={chapter.id[:8]})")
        return research_item
