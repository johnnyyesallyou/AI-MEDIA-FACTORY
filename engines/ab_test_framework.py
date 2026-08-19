"""A/B Testing Framework - Sprint 37.

Content-format A/B тесты поверх ab_tests / ab_test_results.

Lifecycle:
  create_test()  -> draft
  start_test()   -> running
  (publish job: assign_variant + record_exposure + apply config)
  update_results() -> агрегация PostMetric в ab_test_results
  analyze()      -> winner + статистическая значимость (Welch t-test)
  complete_test() -> фиксирует winner, status=completed
"""
import hashlib
import logging
import math
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import func

from core.database import SessionLocal
from core.models.analytics import ABTest, ABTestResult, PostMetric


logger = logging.getLogger(__name__)


METRIC_COLUMNS = {
    "views": PostMetric.views_count,
    "likes": PostMetric.likes_count,
    "shares": PostMetric.shares_count,
    "comments": PostMetric.comments_count,
}


class ABTestFramework:
    """Управление A/B тестами форматов контента."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    # ---------------- lifecycle ----------------

    def create_test(
        self,
        name: str,
        variants: List[Dict],
        traffic_split: Dict[str, int],
        description: str = "",
        winner_metric: str = "views",
        scope: Optional[Dict] = None,
    ) -> str:
        """Создаёт тест. variants: [{id, name, config}]."""
        db = SessionLocal()
        try:
            test = ABTest(
                id=uuid.uuid4(),
                name=name,
                description=description,
                variants=variants,
                traffic_split=traffic_split,
                status="draft",
                winner_metric=winner_metric,
                scope=scope or {},
            )
            db.add(test)
            db.commit()
            self.logger.info(f"AB test created: {name} ({test.id})")
            return str(test.id)
        finally:
            db.close()

    def start_test(self, test_id: str) -> bool:
        db = SessionLocal()
        try:
            test = db.query(ABTest).filter(ABTest.id == test_id).first()
            if not test:
                return False
            test.status = "running"
            test.start_time = datetime.utcnow()
            db.commit()
            return True
        finally:
            db.close()

    def complete_test(self, test_id: str) -> Optional[Dict]:
        """Завершает тест и фиксирует winner."""
        analysis = self.analyze(test_id)
        if not analysis:
            return None

        db = SessionLocal()
        try:
            test = db.query(ABTest).filter(ABTest.id == test_id).first()
            if not test:
                return None
            test.status = "completed"
            test.end_time = datetime.utcnow()
            if analysis.get("significant") and analysis.get("winner_variant_id"):
                test.winner_variant_id = uuid.UUID(analysis["winner_variant_id"])
            db.commit()
            return analysis
        finally:
            db.close()

    def list_tests(self, status: Optional[str] = None) -> List[Dict]:
        db = SessionLocal()
        try:
            q = db.query(ABTest)
            if status:
                q = q.filter(ABTest.status == status)
            return [
                {
                    "id": str(t.id),
                    "name": t.name,
                    "status": t.status,
                    "metric": t.winner_metric,
                    "variants": len(t.variants or []),
                    "scope": t.scope or {},
                }
                for t in q.all()
            ]
        finally:
            db.close()

    # ---------------- assignment ----------------

    def get_active_test(
        self,
        channel_id: str,
        content_type: str,
    ) -> Optional[ABTest]:
        """Находит running тест, подходящий по scope."""
        db = SessionLocal()
        try:
            tests = db.query(ABTest).filter(ABTest.status == "running").all()
            for t in tests:
                scope = t.scope or {}
                ch_ids = scope.get("channel_ids")
                if ch_ids and channel_id not in ch_ids:
                    continue
                ct = scope.get("content_type")
                if ct and ct != content_type:
                    continue
                return t
            return None
        finally:
            db.close()

    def assign_variant(self, test: ABTest, content_id: str) -> Dict:
        """Детерминированное назначение варианта (hash-based)."""
        h = int(hashlib.md5(f"{test.id}:{content_id}".encode()).hexdigest(), 16) % 100
        cumulative = 0
        for variant in (test.variants or []):
            cumulative += int((test.traffic_split or {}).get(variant["id"], 0))
            if h < cumulative:
                return variant
        return (test.variants or [{}])[-1]

    def record_exposure(self, test_id: str, content_id: str, variant_id: str):
        """Создаёт строку ab_test_results (если нет)."""
        db = SessionLocal()
        try:
            existing = db.query(ABTestResult).filter(
                ABTestResult.test_id == uuid.UUID(test_id),
                ABTestResult.content_id == content_id,
            ).first()
            if existing:
                return
            db.add(ABTestResult(
                test_id=uuid.UUID(test_id),
                content_id=content_id,
                variant_id=uuid.UUID(variant_id) if self._is_uuid(variant_id) else uuid.uuid5(uuid.NAMESPACE_DNS, variant_id),
            ))
            db.commit()
        except Exception as e:
            db.rollback()
            self.logger.warning(f"record_exposure failed: {e}")
        finally:
            db.close()

    @staticmethod
    def _is_uuid(s: str) -> bool:
        try:
            uuid.UUID(s)
            return True
        except (ValueError, AttributeError, TypeError):
            return False

    # ---------------- analysis ----------------

    def update_results(self, test_id: str):
        """Агрегирует PostMetric в ab_test_results."""
        db = SessionLocal()
        try:
            rows = db.query(ABTestResult).filter(
                ABTestResult.test_id == uuid.UUID(test_id)
            ).all()

            for row in rows:
                agg = db.query(
                    func.sum(PostMetric.views_count),
                    func.sum(PostMetric.link_clicks),
                    func.sum(PostMetric.shares_count),
                ).filter(PostMetric.content_id == row.content_id).first()

                row.impressions = int(agg[0] or 0)
                row.clicks = int(agg[1] or 0)
                row.conversions = int(agg[2] or 0)

            db.commit()
            self.logger.info(f"Updated results for test {test_id}: {len(rows)} rows")
        finally:
            db.close()

    def analyze(self, test_id: str) -> Optional[Dict]:
        """Welch t-test по per-content значениям winner_metric."""
        db = SessionLocal()
        try:
            test = db.query(ABTest).filter(ABTest.id == test_id).first()
            if not test or len(test.variants or []) < 2:
                return None

            metric_col = METRIC_COLUMNS.get(test.winner_metric, PostMetric.views_count)
            per_variant = {}

            for variant in test.variants:
                rows = db.query(ABTestResult.content_id).filter(
                    ABTestResult.test_id == test.id,
                    ABTestResult.variant_id == (
                        uuid.UUID(variant["id"]) if self._is_uuid(variant["id"])
                        else uuid.uuid5(uuid.NAMESPACE_DNS, variant["id"])
                    ),
                ).all()
                content_ids = [r.content_id for r in rows]
                if not content_ids:
                    per_variant[variant["id"]] = []
                    continue

                values = db.query(
                    PostMetric.content_id,
                    func.sum(metric_col),
                ).filter(
                    PostMetric.content_id.in_(content_ids)
                ).group_by(PostMetric.content_id).all()

                per_variant[variant["id"]] = [float(v[1] or 0) for v in values]

            v_a, v_b = test.variants[0]["id"], test.variants[1]["id"]
            a, b = per_variant.get(v_a, []), per_variant.get(v_b, [])

            stats_a = self._stats(a)
            stats_b = self._stats(b)
            t_stat, p_value = self._welch_t_test(a, b)

            significant = p_value < 0.05 and len(a) >= 2 and len(b) >= 2
            winner = None
            improvement = 0.0
            if stats_a["mean"] != stats_b["mean"]:
                winner = v_a if stats_a["mean"] > stats_b["mean"] else v_b
                loser_mean = min(stats_a["mean"], stats_b["mean"])
                winner_mean = max(stats_a["mean"], stats_b["mean"])
                if loser_mean > 0:
                    improvement = round((winner_mean - loser_mean) / loser_mean * 100, 1)

            return {
                "test_id": test_id,
                "metric": test.winner_metric,
                "variants": {
                    v_a: {**stats_a, "name": test.variants[0].get("name")},
                    v_b: {**stats_b, "name": test.variants[1].get("name")},
                },
                "t_statistic": round(t_stat, 3),
                "p_value": round(p_value, 4),
                "significant": significant,
                "winner_variant_id": winner if significant else None,
                "improvement_pct": improvement,
            }
        finally:
            db.close()

    @staticmethod
    def _stats(values: List[float]) -> Dict:
        n = len(values)
        if n == 0:
            return {"n": 0, "mean": 0.0, "var": 0.0}
        mean = sum(values) / n
        var = sum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else 0.0
        return {"n": n, "mean": round(mean, 2), "var": round(var, 2)}

    @staticmethod
    def _welch_t_test(a: List[float], b: List[float]):
        """Welch t-test; p-value через нормальную аппроксимацию."""
        na, nb = len(a), len(b)
        if na < 2 or nb < 2:
            return 0.0, 1.0
        ma = sum(a) / na
        mb = sum(b) / nb
        va = sum((x - ma) ** 2 for x in a) / (na - 1)
        vb = sum((x - mb) ** 2 for x in b) / (nb - 1)
        se = math.sqrt(va / na + vb / nb)
        if se == 0:
            return 0.0, 1.0
        t = (ma - mb) / se
        # p-value (two-tailed) через нормальную аппроксимацию
        p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
        return t, max(min(p, 1.0), 0.0)