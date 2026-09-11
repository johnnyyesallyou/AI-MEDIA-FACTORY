"""Source Health Checker - Sprint 76.5.

Периодическая проверка здоровья источников с автоматическим quarantine/recovery.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum

from core.models.source_orm import SourceORM
from core.repositories.source_repository import SourceRepository
from engines.source_validation import validate_feed

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Source health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    SICK = "sick"
    QUARANTINED = "quarantined"
    RECOVERING = "recovering"


class HealthMetrics:
    """Health metrics for a source."""

    SUCCESS_RATE_HEALTHY = 0.90
    SUCCESS_RATE_DEGRADED = 0.70
    SUCCESS_RATE_SICK = 0.30

    FAILURE_THRESHOLD = 5  # failures to trigger quarantine
    SUCCESS_RATE_THRESHOLD = 0.30  # success rate to trigger quarantine

    RECOVERY_SUCCESS_COUNT = 5  # successes needed to recover
    RECOVERY_CHECK_INTERVAL = 24 * 3600  # 24 hours

    @staticmethod
    def get_status(source: SourceORM) -> HealthStatus:
        """Determine health status based on metrics."""
        # Check if quarantined (is_active can be None before DB commit, treat as True)
        is_active = source.is_active if source.is_active is not None else True
        if not is_active:
            return HealthStatus.QUARANTINED

        if source.success_rate is None:
            return HealthStatus.HEALTHY  # No data yet

        success_rate = source.success_rate

        if success_rate >= HealthMetrics.SUCCESS_RATE_HEALTHY:
            return HealthStatus.HEALTHY
        elif success_rate >= HealthMetrics.SUCCESS_RATE_DEGRADED:
            return HealthStatus.DEGRADED
        elif success_rate >= HealthMetrics.SUCCESS_RATE_SICK:
            return HealthStatus.SICK
        else:
            return HealthStatus.QUARANTINED

    @staticmethod
    def should_quarantine(source: SourceORM) -> bool:
        """Determine if source should be quarantined."""
        # Handle None values (before DB commit)
        is_active = source.is_active if source.is_active is not None else True
        if not is_active:
            return False  # Already quarantined

        # Need at least some attempts to make decision
        total_attempts = (source.success_count or 0) + (source.failure_count or 0)
        if total_attempts < 5:
            return False  # Not enough data

        # Low success rate with enough attempts
        if source.success_rate and source.success_rate < HealthMetrics.SUCCESS_RATE_THRESHOLD:
            return True

        return False

    @staticmethod
    def can_recover(source: SourceORM) -> bool:
        """Determine if source is ready to recover from quarantine."""
        if source.is_active:
            return False  # Already active

        # Check if enough time has passed since quarantine
        if source.last_failed_fetch_at:
            time_since_failure = datetime.utcnow() - source.last_failed_fetch_at
            if time_since_failure < timedelta(seconds=HealthMetrics.RECOVERY_CHECK_INTERVAL):
                return False

        return True


class SourceHealthChecker:
    """Check and manage source health."""

    def __init__(self, db_session=None):
        self.db = db_session
        self.repo: Optional[SourceRepository] = None

    def _get_repo(self):
        """Get repository instance."""
        if self.repo is None:
            from core.database import get_db
            if self.db is None:
                self.db = next(get_db())
            self.repo = SourceRepository(self.db)
        return self.repo

    def check_all_sources(self) -> dict:
        """Check health of all sources and apply quarantine/recovery."""
        repo = self._get_repo()

        healthy = 0
        degraded = 0
        sick = 0
        quarantined = 0
        recovered = 0

        # Get all sources
        all_sources = repo.list_all(limit=1000, is_active=None)

        for source in all_sources:
            status = HealthMetrics.get_status(source)

            if status == HealthStatus.HEALTHY:
                healthy += 1
            elif status == HealthStatus.DEGRADED:
                degraded += 1
            elif status == HealthStatus.SICK:
                sick += 1
            elif status == HealthStatus.QUARANTINED:
                quarantined += 1

            # Auto-quarantine if needed
            if source.is_active and HealthMetrics.should_quarantine(source):
                self.quarantine(
                    source.id,
                    f"Auto-quarantine: success_rate={source.success_rate:.2f}"
                )
                quarantined += 1

            # Try to recover if possible
            elif not source.is_active and HealthMetrics.can_recover(source):
                # Try validation first
                if self._validate_feed(source):
                    self.recover(source.id)
                    recovered += 1

        logger.info(
            f"Health check: healthy={healthy}, degraded={degraded}, "
            f"sick={sick}, quarantined={quarantined}, recovered={recovered}"
        )

        return {
            "healthy": healthy,
            "degraded": degraded,
            "sick": sick,
            "quarantined": quarantined,
            "recovered": recovered,
            "total": len(all_sources),
        }

    def check_source(self, source_id: str) -> dict:
        """Check health of a specific source."""
        repo = self._get_repo()
        source = repo.get_by_id(source_id)

        if not source:
            return {"error": f"Source {source_id} not found"}

        status = HealthMetrics.get_status(source)
        can_quarantine = HealthMetrics.should_quarantine(source)
        can_recover = HealthMetrics.can_recover(source)

        return {
            "source_id": source_id,
            "name": source.name,
            "status": status.value,
            "success_rate": source.success_rate,
            "quality_score": source.quality_score,
            "success_count": source.success_count,
            "failure_count": source.failure_count,
            "is_active": source.is_active,
            "should_quarantine": can_quarantine,
            "can_recover": can_recover,
            "last_selected_at": source.last_selected_at.isoformat() if source.last_selected_at else None,
            "last_successful_fetch_at": source.last_successful_fetch_at.isoformat() if source.last_successful_fetch_at else None,
            "last_failed_fetch_at": source.last_failed_fetch_at.isoformat() if source.last_failed_fetch_at else None,
        }

    def quarantine(self, source_id: str, reason: str = "Health check failure"):
        """Quarantine a source."""
        repo = self._get_repo()
        source = repo.disable_source(source_id, f"Quarantined: {reason}")
        logger.warning(f"Source {source_id} quarantined: {reason}")
        return source

    def recover(self, source_id: str):
        """Attempt to recover a quarantined source."""
        repo = self._get_repo()
        source = repo.enable_source(source_id)
        logger.info(f"Source {source_id} recovered from quarantine")
        return source

    def _validate_feed(self, source: SourceORM) -> bool:
        """Validate that feed is still accessible."""
        try:
            validation = validate_feed(source.canonical_url)
            return validation.is_valid
        except Exception as e:
            logger.warning(f"Feed validation failed for {source.canonical_url}: {e}")
            return False

    def get_health_report(self) -> dict:
        """Get overall health report."""
        stats = self.check_all_sources()

        # Calculate health score
        total = stats["total"]
        if total == 0:
            health_score = 0.0
        else:
            healthy_weight = stats["healthy"] * 1.0
            degraded_weight = stats["degraded"] * 0.5
            sick_weight = stats["sick"] * 0.25
            health_score = (healthy_weight + degraded_weight + sick_weight) / total * 100

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "health_score": health_score,
            "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "unhealthy",
            "statistics": stats,
        }


# Global singleton
_health_checker: Optional[SourceHealthChecker] = None


def get_health_checker(db_session=None) -> SourceHealthChecker:
    """Get or create health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = SourceHealthChecker(db_session)
    return _health_checker
