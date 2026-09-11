"""Tests for Source Health Checker - Sprint 76.5."""
import pytest
from datetime import datetime, timedelta

from engines.source_health_checker import (
    SourceHealthChecker,
    HealthStatus,
    HealthMetrics,
)
from core.models.source_orm import SourceORM


class TestHealthMetrics:
    """Tests for health metrics calculation."""

    def test_healthy_status_high_success_rate(self):
        """Source with 95% success rate is HEALTHY."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )
        source.success_count = 95
        source.failure_count = 5
        source.success_rate = 0.95

        status = HealthMetrics.get_status(source)
        assert status == HealthStatus.HEALTHY

    def test_degraded_status_medium_success_rate(self):
        """Source with 75% success rate is DEGRADED."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )
        source.success_count = 75
        source.failure_count = 25
        source.success_rate = 0.75

        status = HealthMetrics.get_status(source)
        assert status == HealthStatus.DEGRADED

    def test_sick_status_low_success_rate(self):
        """Source with 40% success rate is SICK."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )
        source.success_count = 40
        source.failure_count = 60
        source.success_rate = 0.40

        status = HealthMetrics.get_status(source)
        assert status == HealthStatus.SICK

    def test_quarantined_status_very_low_success_rate(self):
        """Source with 20% success rate is QUARANTINED."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )
        source.success_count = 20
        source.failure_count = 80
        source.success_rate = 0.20

        status = HealthMetrics.get_status(source)
        assert status == HealthStatus.QUARANTINED

    def test_should_quarantine_high_failure_count(self, db_session):
        """Source should be quarantined if failure_count causes low success_rate."""
        from core.repositories.source_repository import SourceRepository

        repo = SourceRepository(db_session)
        source = repo.create(
            canonical_url="https://example.com/bad.xml",
            name="Bad Feed",
        )
        source.success_count = 2
        source.failure_count = 10
        source.success_rate = 0.166  # 2 / (2 + 10)
        db_session.commit()

        assert HealthMetrics.should_quarantine(source) == True

    def test_should_quarantine_low_success_rate(self):
        """Source should be quarantined if success_rate too low."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )
        source.success_count = 2
        source.failure_count = 10
        source.success_rate = 0.166
        source.is_active = True

        assert HealthMetrics.should_quarantine(source) == True

    def test_should_not_quarantine_healthy_source(self, db_session):
        """Healthy source should not be quarantined."""
        from core.repositories.source_repository import SourceRepository

        repo = SourceRepository(db_session)
        source = repo.create(
            canonical_url="https://example.com/healthy.xml",
            name="Healthy Feed",
        )
        source.success_count = 90
        source.failure_count = 10
        source.success_rate = 0.90
        db_session.commit()

        assert HealthMetrics.should_quarantine(source) == False

    def test_can_recover_after_timeout(self):
        """Source can recover after recovery timeout."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )
        source.is_active = False
        source.last_failed_fetch_at = datetime.utcnow() - timedelta(days=2)

        assert HealthMetrics.can_recover(source) == True

    def test_cannot_recover_before_timeout(self):
        """Source cannot recover before timeout."""
        source = SourceORM(
            canonical_url="https://example.com/feed.xml",
            name="Test Feed",
        )
        source.is_active = False
        source.last_failed_fetch_at = datetime.utcnow() - timedelta(hours=1)

        assert HealthMetrics.can_recover(source) == False


class TestSourceHealthChecker:
    """Tests for health checker."""

    def test_check_source_healthy(self, db_session):
        """Check health of healthy source."""
        from core.repositories.source_repository import SourceRepository

        repo = SourceRepository(db_session)
        source = repo.create(
            canonical_url="https://example.com/healthy.xml",
            name="Healthy Feed",
        )
        source.success_count = 90
        source.failure_count = 10
        source.success_rate = 0.90
        db_session.commit()

        checker = SourceHealthChecker(db_session)
        health = checker.check_source(source.id)

        assert health["status"] == HealthStatus.HEALTHY.value
        assert health["success_rate"] == 0.90
        assert health["should_quarantine"] == False

    def test_check_source_sick(self, db_session):
        """Check health of sick source."""
        from core.repositories.source_repository import SourceRepository

        repo = SourceRepository(db_session)
        source = repo.create(
            canonical_url="https://example.com/sick.xml",
            name="Sick Feed",
        )
        source.success_count = 35
        source.failure_count = 65
        source.success_rate = 0.35
        db_session.commit()

        checker = SourceHealthChecker(db_session)
        health = checker.check_source(source.id)

        assert health["status"] == HealthStatus.SICK.value
        assert health["success_rate"] == 0.35

    def test_quarantine_source(self, db_session):
        """Quarantine a source."""
        from core.repositories.source_repository import SourceRepository

        repo = SourceRepository(db_session)
        source = repo.create(
            canonical_url="https://example.com/bad.xml",
            name="Bad Feed",
        )

        checker = SourceHealthChecker(db_session)
        quarantined = checker.quarantine(source.id, "Test quarantine")

        assert quarantined.is_active == False
        assert "Quarantined" in quarantined.disabled_reason

    def test_recover_source(self, db_session):
        """Recover a quarantined source."""
        from core.repositories.source_repository import SourceRepository

        repo = SourceRepository(db_session)
        source = repo.create(
            canonical_url="https://example.com/recover.xml",
            name="Recovering Feed",
        )
        source.is_active = False
        db_session.commit()

        checker = SourceHealthChecker(db_session)
        recovered = checker.recover(source.id)

        assert recovered.is_active == True
        assert recovered.disabled_reason is None

    def test_check_all_sources(self, db_session):
        """Check health of all sources."""
        from core.repositories.source_repository import SourceRepository

        repo = SourceRepository(db_session)

        # Create healthy source
        healthy = repo.create(
            canonical_url="https://example.com/h1.xml",
            name="Healthy 1",
        )
        healthy.success_count = 90
        healthy.failure_count = 10
        healthy.success_rate = 0.90

        # Create degraded source
        degraded = repo.create(
            canonical_url="https://example.com/d1.xml",
            name="Degraded 1",
        )
        degraded.success_count = 70
        degraded.failure_count = 30
        degraded.success_rate = 0.70

        # Create sick source
        sick = repo.create(
            canonical_url="https://example.com/s1.xml",
            name="Sick 1",
        )
        sick.success_count = 30
        sick.failure_count = 70
        sick.success_rate = 0.30

        db_session.commit()

        checker = SourceHealthChecker(db_session)
        report = checker.check_all_sources()

        assert report["total"] >= 3
        assert report["healthy"] >= 1
        assert report["degraded"] >= 1
        assert report["sick"] >= 1

    def test_get_health_report(self, db_session):
        """Get overall health report."""
        from core.repositories.source_repository import SourceRepository

        repo = SourceRepository(db_session)
        repo.create(
            canonical_url="https://example.com/test.xml",
            name="Test Feed",
        )

        checker = SourceHealthChecker(db_session)
        report = checker.get_health_report()

        assert "timestamp" in report
        assert "health_score" in report
        assert "status" in report
        assert "statistics" in report
        assert 0 <= report["health_score"] <= 100


@pytest.fixture
def db_session():
    """Fixture for database session."""
    from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Base, engine

    Base.metadata.create_all(bind=engine)
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
