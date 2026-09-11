"""Smart Source Selection Engine - Sprint 76.2.

Компонует скоринг (Sprint 76.1) с:
  - качеством источника (QualityRegistry: успехи/фейлы -> adjustment)
  - ротацией (selection_count -> penalty, чтобы слабо менять состав)
  - diversity (избегаем редундантных источников с идентичным coverage)
  - topic-based matching  (уже встроен в base score через scoring engine)
"""
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple

from .source_registry import SOURCES
from .source_scoring import SourceDiscoveryEngine

DIVERSITY_PENALTY = 5.0
ROTATION_PENALTY = 3.0
QUALITY_MIN = -10.0
QUALITY_MAX = 8.0
QUALITY_TARGET_RATE = 0.7


@dataclass
class SourceQuality:
    """Накопленные метрики качества по источнику."""

    success_count: int = 0
    failure_count: int = 0
    total_items: int = 0
    selection_count: int = 0
    last_outcome: Optional[str] = None

    @property
    def attempts(self) -> int:
        return self.success_count + self.failure_count

    @property
    def success_rate(self) -> Optional[float]:
        if not self.attempts:
            return None
        return self.success_count / self.attempts


class QualityRegistry:
    """In-memory реестр качества источников (runtime)."""

    def __init__(self) -> None:
        self._store: Dict[str, SourceQuality] = {}

    def reset(self) -> None:
        self._store.clear()

    def record(self, source_id: str, outcome: str, items: int = 0) -> SourceQuality:
        q = self._store.setdefault(source_id, SourceQuality())
        if outcome == "success":
            q.success_count += 1
            q.total_items += items
            q.last_outcome = "success"
        else:
            q.failure_count += 1
            q.last_outcome = "failure"
        return q

    def bump_selection(self, source_id: str) -> SourceQuality:
        q = self._store.setdefault(source_id, SourceQuality())
        q.selection_count += 1
        return q

    def get(self, source_id: str) -> SourceQuality:
        return self._store.get(source_id, SourceQuality())

    def quality_adjustment(self, source_id: str) -> float:
        q = self.get(source_id)
        if q.attempts < 3:
            return 0.0  # недостаточно данных
        sr = q.success_rate or 0.0
        adj = (sr - QUALITY_TARGET_RATE) * 20
        return round(max(QUALITY_MIN, min(QUALITY_MAX, adj)), 1)

    def selection_count(self, source_id: str) -> int:
        return self.get(source_id).selection_count


@dataclass(frozen=True)
class SelectedSource:
    source_id: str
    name: str
    base_score: float
    quality_adjustment: float
    final_score: float
    languages: tuple
    matched_capabilities: tuple
    reasons: tuple


# Общий реестр для длительно живущих процессов (API). Тесты инжектят свой.
DEFAULT_REGISTRY = QualityRegistry()


class SmartSourceSelector:
    """Умный выбор источников: score + quality + rotation + diversity."""

    def __init__(self, registry: Optional[QualityRegistry] = None) -> None:
        self.registry = registry or DEFAULT_REGISTRY

    def select(
        self,
        content_type: str,
        topic: Optional[str] = None,
        language: Optional[str] = None,
        top_k: Optional[int] = None,
        diversity: bool = True,
        rotation: bool = True,
    ) -> List[SelectedSource]:
        """Выбрать источники, ранжированные по final_score (score+quality-rot-div)."""
        base = SourceDiscoveryEngine.recommend(
            content_type=content_type, topic=topic, language=language,
        )

        seen_keys: set = set()
        results: List[SelectedSource] = []

        for sc in base:  # уже отсортирован по base_score desc
            langs = SOURCES[sc.source_id].languages
            q_adj = self.registry.quality_adjustment(sc.source_id)
            final = sc.score + q_adj
            reasons = [f"base={sc.score}"]
            if q_adj:
                reasons.append(f"quality={q_adj:+.1f}")

            # Diversity: полное дублирование coverage (caps+language) штрафуем
            key: FrozenSet = (frozenset(sc.matched_capabilities), frozenset(langs))
            if diversity and key in seen_keys:
                final -= DIVERSITY_PENALTY
                reasons.append("redundant")
            seen_keys.add(key)

            # Rotation: недавно часто выбираемые — чуть ниже
            if rotation:
                used = self.registry.selection_count(sc.source_id)
                if used:
                    final -= ROTATION_PENALTY * used
                    reasons.append(f"used={used}")

            final = max(0.0, round(final, 1))
            results.append(SelectedSource(
                source_id=sc.source_id,
                name=sc.name,
                base_score=sc.score,
                quality_adjustment=q_adj,
                final_score=final,
                languages=langs,
                matched_capabilities=sc.matched_capabilities,
                reasons=tuple(reasons),
            ))

        results.sort(key=lambda s: s.final_score, reverse=True)
        if top_k:
            results = results[:top_k]
        return results