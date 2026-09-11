"""Source Repository - Sprint 76.4.

Data access layer для работы с Sources в PostgreSQL.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from core.models.source_orm import SourceORM


class SourceRepository:
    """Repository for Source operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        canonical_url: str,
        name: str,
        language: str = "ru",
        source_type: str = "rss",
        category: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        discovered_from: Optional[str] = None,
    ) -> SourceORM:
        """Create a new source."""
        source = SourceORM(
            canonical_url=canonical_url,
            name=name,
            language=language,
            source_type=source_type,
            category=category,
            capabilities=capabilities or [],
            discovered_from=discovered_from,
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def get_by_url(self, canonical_url: str) -> Optional[SourceORM]:
        """Get source by canonical URL."""
        return self.db.query(SourceORM).filter(
            SourceORM.canonical_url == canonical_url
        ).first()

    def get_by_id(self, source_id: str) -> Optional[SourceORM]:
        """Get source by ID."""
        return self.db.query(SourceORM).filter(
            SourceORM.id == source_id
        ).first()

    def list_all(
        self,
        language: Optional[str] = None,
        category: Optional[str] = None,
        is_active: bool = True,
        limit: int = 100,
    ) -> List[SourceORM]:
        """List sources with optional filters."""
        query = self.db.query(SourceORM)

        if language:
            query = query.filter(SourceORM.language == language)
        if category:
            query = query.filter(SourceORM.category == category)
        if is_active:
            query = query.filter(SourceORM.is_active == True)

        return query.order_by(SourceORM.quality_score.desc()).limit(limit).all()

    def list_by_content_type(
        self,
        content_type: str,
        language: Optional[str] = None,
        limit: int = 20,
    ) -> List[SourceORM]:
        """List sources that support a specific content type.

        Content types are determined by capabilities:
        - "news": articles, summaries, covers
        - "manga": chapters, covers, descriptions
        - "anime": episodes, covers, descriptions
        """
        # Capability mapping
        capability_map = {
            "news": ["articles", "summaries", "covers"],
            "manga": ["chapters", "covers", "descriptions"],
            "anime": ["episodes", "covers", "descriptions"],
        }

        required_capabilities = capability_map.get(content_type, [])
        if not required_capabilities:
            return []

        query = self.db.query(SourceORM).filter(SourceORM.is_active == True)

        if language:
            query = query.filter(SourceORM.language == language)

        # Filter by capabilities (sources must have at least one)
        sources = []
        for source in query.all():
            source_caps = set(source.capabilities or [])
            if any(cap in source_caps for cap in required_capabilities):
                sources.append(source)

        # Sort by quality
        sources.sort(key=lambda s: s.quality_score, reverse=True)
        return sources[:limit]

    def list_by_topic(
        self,
        topic: str,
        language: Optional[str] = None,
        limit: int = 20,
    ) -> List[SourceORM]:
        """List sources that cover a specific topic."""
        query = self.db.query(SourceORM).filter(SourceORM.is_active == True)

        if language:
            query = query.filter(SourceORM.language == language)

        # Filter by topic
        sources = []
        for source in query.all():
            source_topics = set(source.topics or [])
            if topic.lower() in [t.lower() for t in source_topics]:
                sources.append(source)

        sources.sort(key=lambda s: s.quality_score, reverse=True)
        return sources[:limit]

    def update_quality_metrics(self, source_id: str, outcome: str, items_count: int = 0):
        """Update quality metrics for a source."""
        source = self.get_by_id(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")

        source.update_quality_metrics(outcome, items_count)
        self.db.commit()
        return source

    def record_selection(self, source_id: str):
        """Record that a source was selected."""
        source = self.get_by_id(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")

        source.record_selection()
        self.db.commit()
        return source

    def mark_validation(self, source_id: str, status: str, error: str = None):
        """Mark validation status."""
        source = self.get_by_id(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")

        source.mark_validation_status(status, error)
        self.db.commit()
        return source

    def disable_source(self, source_id: str, reason: str):
        """Disable a source."""
        source = self.get_by_id(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")

        source.disable(reason)
        self.db.commit()
        return source

    def enable_source(self, source_id: str):
        """Enable a source."""
        source = self.get_by_id(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")

        source.enable()
        self.db.commit()
        return source

    def get_unhealthy_sources(
        self,
        failure_threshold: int = 5,
        success_rate_threshold: float = 0.3,
    ) -> List[SourceORM]:
        """Get sources that are unhealthy based on metrics."""
        query = self.db.query(SourceORM).filter(SourceORM.is_active == True)

        unhealthy = []
        for source in query.all():
            # High failure count
            if source.failure_count >= failure_threshold:
                unhealthy.append(source)
                continue

            # Low success rate
            if source.success_rate and source.success_rate < success_rate_threshold:
                unhealthy.append(source)

        return unhealthy

    def get_statistics(self) -> dict:
        """Get registry statistics."""
        from sqlalchemy import func

        active = self.db.query(SourceORM).filter(SourceORM.is_active == True).count()
        inactive = self.db.query(SourceORM).filter(SourceORM.is_active == False).count()
        total = active + inactive

        avg_quality = self.db.query(func.avg(SourceORM.quality_score)).filter(
            SourceORM.is_active == True
        ).scalar() or 0.0

        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "average_quality": float(avg_quality),
        }

    def delete_by_url(self, canonical_url: str) -> bool:
        """Delete a source by URL."""
        source = self.get_by_url(canonical_url)
        if not source:
            return False

        self.db.delete(source)
        self.db.commit()
        return True

    def bulk_create(self, sources_data: List[dict]) -> List[SourceORM]:
        """Create multiple sources at once."""
        created = []
        for data in sources_data:
            source = self.create(**data)
            created.append(source)
        return created
