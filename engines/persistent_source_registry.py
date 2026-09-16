"""Persistent Source Registry - Sprint 76.4.

Замена in-memory QualityRegistry на persistent версию с PostgreSQL.
Обеспечивает durability качества и метрик источников после перезапуска.
"""
from typing import Optional, List
from datetime import datetime
import logging

from core.database import SessionLocal
from core.models.source_orm import SourceORM
from core.repositories.source_repository import SourceRepository

logger = logging.getLogger(__name__)

# ``SourceDefinition`` predates the persistent registry and deliberately has no
# URL field.  Keep this bridge explicit: it is a compatibility contract, not a
# name/domain matching heuristic.  The values are the canonical endpoints used
# by the corresponding adapters/RSS jobs.
LOGICAL_SOURCE_URLS = {
    "remanga": "https://remanga.org/api/",
    "mangadex": "https://api.mangadex.org/",
    "readmanga": "https://readmanga.me/",
    "anilist": "https://graphql.anilist.co",
    "myanimelist": "https://myanimelist.net/rss/news.xml",
    "habr": "https://habr.com/ru/rss/articles/",
    "vc": "https://vc.ru/rss/all",
    "techcrunch": "https://techcrunch.com/feed/",
    "theverge": "https://www.theverge.com/rss/index.xml",
}


class PersistentSourceRegistry:
    """Persistent registry for source quality metrics and selection tracking."""

    def __init__(self, db_session=None):
        """Initialize registry with optional session (for testing)."""
        self.db = db_session
        self._owns_session = db_session is None

    def _get_db(self):
        """Get database session."""
        if self.db is None:
            self.db = SessionLocal()
        return self.db

    def close(self) -> None:
        """Close a session created by this registry, never an injected one."""
        if self._owns_session and self.db is not None:
            self.db.close()
            self.db = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def _get_repo(self):
        """Get repository instance."""
        return SourceRepository(self._get_db())

    def register(
        self,
        canonical_url: str,
        name: str,
        language: str = "ru",
        source_type: str = "rss",
        category: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        discovered_from: Optional[str] = None,
    ) -> SourceORM:
        """Register a new source or get existing."""
        repo = self._get_repo()

        # Check if already exists
        existing = repo.get_by_url(canonical_url)
        if existing:
            return existing

        # Create new
        return repo.create(
            canonical_url=canonical_url,
            name=name,
            language=language,
            source_type=source_type,
            category=category,
            capabilities=capabilities,
            discovered_from=discovered_from,
        )

    def record(self, source_id: str, outcome: str, items_count: int = 0) -> Optional[SourceORM]:
        """Record fetch outcome for a source."""
        try:
            repo = self._get_repo()
            return repo.update_quality_metrics(source_id, outcome, items_count)
        except Exception as e:
            logger.warning(f"Failed to record metrics for {source_id}: {e}")
            return None

    def bump_selection(self, source_id: str) -> Optional[SourceORM]:
        """Record that a source was selected."""
        try:
            repo = self._get_repo()
            return repo.record_selection(source_id)
        except Exception as e:
            logger.warning(f"Failed to record selection for {source_id}: {e}")
            return None

    def quality_adjustment(self, source_id: str) -> float:
        """Get quality adjustment for a source."""
        repo = self._get_repo()
        source = repo.get_by_id(source_id)

        if not source:
            return 0.0

        # Simple adjustment: (quality_score - 50) / 10, clamped to [-10, +8]
        # This is compatible with the SmartSourceSelector logic
        adjustment = (source.quality_score - 50.0) / 10.0
        return max(-10.0, min(8.0, adjustment))

    def get_source(self, source_id: str) -> Optional[SourceORM]:
        """Get a source by database ID or an explicitly mapped logical ID."""
        repo = self._get_repo()
        source = repo.get_by_id(source_id)
        if source is not None:
            return source

        canonical_url = LOGICAL_SOURCE_URLS.get(source_id)
        return repo.get_by_url(canonical_url) if canonical_url else None

    def get_source_by_logical_id(self, source_id: str) -> Optional[SourceORM]:
        """Resolve a legacy logical source ID through its exact canonical URL."""
        canonical_url = LOGICAL_SOURCE_URLS.get(source_id)
        if canonical_url is None:
            return None
        return self._get_repo().get_by_url(canonical_url)

    def get_source_by_url(self, canonical_url: str) -> Optional[SourceORM]:
        """Get source by URL."""
        repo = self._get_repo()
        return repo.get_by_url(canonical_url)

    def list_sources(
        self,
        language: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
    ) -> List[SourceORM]:
        """List sources with optional filters."""
        repo = self._get_repo()
        return repo.list_all(language=language, category=category, limit=limit)

    def list_by_content_type(
        self,
        content_type: str,
        language: Optional[str] = None,
        limit: int = 20,
    ) -> List[SourceORM]:
        """List sources for a specific content type."""
        repo = self._get_repo()
        return repo.list_by_content_type(content_type, language, limit)

    def list_by_topic(
        self,
        topic: str,
        language: Optional[str] = None,
        limit: int = 20,
    ) -> List[SourceORM]:
        """List sources for a specific topic."""
        repo = self._get_repo()
        return repo.list_by_topic(topic, language, limit)

    def disable(self, source_id: str, reason: str = "Manual disable"):
        """Disable a source."""
        try:
            repo = self._get_repo()
            return repo.disable_source(source_id, reason)
        except Exception as e:
            logger.warning(f"Failed to disable {source_id}: {e}")
            return None

    def enable(self, source_id: str):
        """Enable a source."""
        try:
            repo = self._get_repo()
            return repo.enable_source(source_id)
        except Exception as e:
            logger.warning(f"Failed to enable {source_id}: {e}")
            return None

    def quarantine(self, source_id: str, reason: str):
        """Move source to quarantine (disabled state)."""
        return self.disable(source_id, f"Quarantine: {reason}")

    def get_unhealthy_sources(
        self,
        failure_threshold: int = 5,
        success_rate_threshold: float = 0.3,
    ) -> List[SourceORM]:
        """Get unhealthy sources."""
        repo = self._get_repo()
        return repo.get_unhealthy_sources(failure_threshold, success_rate_threshold)

    def get_statistics(self) -> dict:
        """Get registry statistics."""
        repo = self._get_repo()
        return repo.get_statistics()

    def health_check(self) -> dict:
        """Health check: ensure registry is operational."""
        try:
            stats = self.get_statistics()
            return {
                "status": "healthy",
                "statistics": stats,
            }
        except Exception as e:
            logger.error(f"Registry health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }


# Global singleton instance
_persistent_registry: Optional[PersistentSourceRegistry] = None


def get_persistent_registry() -> PersistentSourceRegistry:
    """Get or create global persistent registry instance."""
    global _persistent_registry
    if _persistent_registry is None:
        _persistent_registry = PersistentSourceRegistry()
    return _persistent_registry


def reset_persistent_registry():
    """Reset the global registry (for testing)."""
    global _persistent_registry
    _persistent_registry = None
