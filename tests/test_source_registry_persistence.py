"""Tests for Source Registry Persistence - Sprint 76.4."""
import pytest
from datetime import datetime

from core.models.source_orm import SourceORM
from core.repositories.source_repository import SourceRepository


class TestSourceORM:
    """Tests for Source ORM model."""

    def test_source_orm_creation(self):
        """Create a source ORM instance."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Example News",
            language="ru",
            source_type="rss",
            category="news",
        )

        assert source.canonical_url == "https://example.com/feed.xml"
        assert source.name == "Example News"
        # Defaults may be None before database commit
        assert source.is_active in [True, None]  # Allow both before/after commit

    def test_source_orm_update_quality_metrics_success(self, db_session):
        """Update quality metrics with success."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )
        db_session.add(source)
        db_session.commit()

        source.update_quality_metrics("success", items_count=10)

        assert source.success_count == 1
        assert source.failure_count == 0
        assert source.success_rate == 1.0
        assert source.quality_score > 50.0  # Improved from baseline

    def test_source_orm_update_quality_metrics_failure(self, db_session):
        """Update quality metrics with failure."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )
        db_session.add(source)
        db_session.commit()

        source.update_quality_metrics("failure")

        assert source.success_count == 0
        assert source.failure_count == 1
        assert source.success_rate == 0.0
        assert source.quality_score < 50.0  # Degraded from baseline

    def test_source_orm_record_selection(self, db_session):
        """Record source selection."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )
        db_session.add(source)
        db_session.commit()

        source.record_selection()
        assert source.selection_count == 1
        assert source.last_selected_at is not None

        source.record_selection()
        assert source.selection_count == 2

    def test_source_orm_disable(self):
        """Disable a source."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )

        source.disable("Test disable reason")
        assert source.is_active == False
        assert source.disabled_reason == "Test disable reason"

    def test_source_orm_enable(self):
        """Enable a source."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
            is_active=False,
            disabled_reason="Was disabled",
        )

        source.enable()
        assert source.is_active == True
        assert source.disabled_reason is None

    def test_source_orm_mark_validation(self):
        """Mark validation status."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )

        source.mark_validation_status("valid")
        assert source.validation_status == "valid"

        source.mark_validation_status("invalid", error="Not a valid RSS feed")
        assert source.validation_status == "invalid"
        assert source.disabled_reason == "Not a valid RSS feed"

    def test_source_orm_to_dict(self):
        """Convert source to dictionary."""
        source = SourceORM(
            id="test-123",
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
            language="en",
        )

        data = source.to_dict()

        assert data["id"] == "test-123"
        assert data["canonical_url"] == "https://example.com/feed.xml"
        assert data["name"] == "Test Feed"
        assert data["language"] == "en"
        assert "quality_score" in data
        assert "created_at" in data


class TestSourceRepository:
    """Tests for Source Repository."""

    def test_repository_create(self, db_session):
        """Create a source via repository."""
        repo = SourceRepository(db_session)

        source = repo.create(
            canonical_url="https://example.com/feed1.xml",
            name="Feed 1",
            language="ru",
        )

        assert source.id is not None
        assert source.canonical_url == "https://example.com/feed1.xml"

    def test_repository_get_by_url(self, db_session):
        """Get source by URL."""
        repo = SourceRepository(db_session)

        source1 = repo.create(
            canonical_url="https://example.com/feed1.xml",
            name="Feed 1",
        )

        retrieved = repo.get_by_url("https://example.com/feed1.xml")
        assert retrieved is not None
        assert retrieved.id == source1.id

    def test_repository_list_all(self, db_session):
        """List all sources."""
        repo = SourceRepository(db_session)

        repo.create(
            canonical_url="https://example.com/feed1.xml",
            name="Feed 1",
            language="ru",
        )
        repo.create(
            canonical_url="https://example.com/feed2.xml",
            name="Feed 2",
            language="en",
        )

        sources = repo.list_all()
        assert len(sources) >= 2

    def test_repository_list_by_language(self, db_session):
        """List sources by language."""
        repo = SourceRepository(db_session)

        repo.create(
            canonical_url="https://example.com/ru_feed.xml",
            name="Russian Feed",
            language="ru",
        )
        repo.create(
            canonical_url="https://example.com/en_feed.xml",
            name="English Feed",
            language="en",
        )

        ru_sources = repo.list_all(language="ru")
        assert all(s.language == "ru" for s in ru_sources)

    def test_repository_update_quality_metrics(self, db_session):
        """Update quality metrics via repository."""
        repo = SourceRepository(db_session)

        source = repo.create(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )

        updated = repo.update_quality_metrics(source.id, "success")
        assert updated.success_count == 1

    def test_repository_record_selection(self, db_session):
        """Record selection via repository."""
        repo = SourceRepository(db_session)

        source = repo.create(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )

        updated = repo.record_selection(source.id)
        assert updated.selection_count == 1

    def test_repository_disable_source(self, db_session):
        """Disable source via repository."""
        repo = SourceRepository(db_session)

        source = repo.create(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )

        disabled = repo.disable_source(source.id, "Test disable")
        assert disabled.is_active == False
        assert disabled.disabled_reason == "Test disable"

    def test_repository_get_unhealthy_sources(self, db_session):
        """Get unhealthy sources."""
        repo = SourceRepository(db_session)

        # Create healthy source
        healthy = repo.create(
            canonical_url="https://example.com/healthy.xml",
            name="Healthy Feed",
        )
        healthy.success_count = 10
        healthy.failure_count = 1
        db_session.commit()

        # Create unhealthy source
        unhealthy = repo.create(
            canonical_url="https://example.com/unhealthy.xml",
            name="Unhealthy Feed",
        )
        unhealthy.failure_count = 10
        db_session.commit()

        bad_sources = repo.get_unhealthy_sources(failure_threshold=5)
        assert len(bad_sources) > 0
        assert unhealthy.id in [s.id for s in bad_sources]

    def test_repository_get_statistics(self, db_session):
        """Get registry statistics."""
        repo = SourceRepository(db_session)

        repo.create(
            canonical_url="https://example.com/feed1.xml",
            name="Feed 1",
        )
        repo.create(
            canonical_url="https://example.com/feed2.xml",
            name="Feed 2",
        )

        stats = repo.get_statistics()
        assert "total" in stats
        assert "active" in stats
        assert "average_quality" in stats


@pytest.fixture
def db_session():
    """Fixture for database session."""
    from core.database import SessionLocal, Base, engine

    # Create tables
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    yield session
    session.close()

    # Drop tables
    Base.metadata.drop_all(bind=engine)


class TestPersistentSourceRegistry:
    """Tests for Persistent Source Registry."""

    def test_registry_register_new_source(self, db_session):
        """Register a new source."""
        from engines.persistent_source_registry import PersistentSourceRegistry

        registry = PersistentSourceRegistry(db_session)

        source = registry.register(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )

        assert source is not None
        assert source.canonical_url == "https://example.com/feed.xml"

    def test_registry_register_existing_source(self, db_session):
        """Register existing source returns same instance."""
        from engines.persistent_source_registry import PersistentSourceRegistry

        registry = PersistentSourceRegistry(db_session)

        source1 = registry.register(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )

        source2 = registry.register(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )

        assert source1.id == source2.id

    def test_registry_quality_adjustment(self, db_session):
        """Get quality adjustment for source."""
        from engines.persistent_source_registry import PersistentSourceRegistry

        registry = PersistentSourceRegistry(db_session)

        source = registry.register(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )

        # Record success to improve quality
        registry.record(source.id, "success")

        adjustment = registry.quality_adjustment(source.id)
        assert adjustment > 0  # Improved from baseline

    def test_registry_health_check(self, db_session):
        """Health check registry."""
        from engines.persistent_source_registry import PersistentSourceRegistry

        registry = PersistentSourceRegistry(db_session)

        health = registry.health_check()
        assert health["status"] in ["healthy", "unhealthy"]
        assert "statistics" in health or "error" in health
