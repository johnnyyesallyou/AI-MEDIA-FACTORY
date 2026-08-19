"""Manga Enrichment Job - Sprint 30.5 (new API).

Использует CrossSourceEnricher.enrich() — source-aware enrichment.
"""
import logging
from typing import Any, Dict

from core.database import SessionLocal
from core.models.manga_knowledge import MangaTitle
from engines.cross_source_enricher import CrossSourceEnricher

logger = logging.getLogger(__name__)


class MangaEnrichmentJob:
    """Обогащает тайтлы, у которых нет описания/жанров."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.enricher = CrossSourceEnricher()

    def run(self, limit: int = 20) -> Dict[str, Any]:
        self.logger.info(f"MangaEnrichmentJob started (limit={limit})")

        db = SessionLocal()
        try:
            titles = db.query(MangaTitle).filter(
                (MangaTitle.description == None) | (MangaTitle.description == "")
            ).limit(limit).all()

            self.logger.info(f"Titles to enrich: {len(titles)}")

            enriched = 0
            for title in titles:
                try:
                    # Новый API: enrich() напрямую модифицирует объект
                    self.enricher.enrich(title)
                    
                    # Проверяем что что-то изменилось
                    if title.description or title.genres:
                        enriched += 1
                        self.logger.info(f"Enriched: {title.canonical_title[:50]}")
                except Exception as e:
                    self.logger.error(f"Enrichment failed for {title.canonical_title[:50]}: {e}")

            db.commit()

            stats = {"status": "ok", "processed": len(titles), "enriched": enriched}
            self.logger.info(f"MangaEnrichmentJob finished: {stats}")
            return stats

        except Exception as e:
            db.rollback()
            self.logger.exception(f"MangaEnrichmentJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()