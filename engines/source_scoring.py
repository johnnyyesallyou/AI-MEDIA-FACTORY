"""Source Discovery Engine - Sprint 76.1 (Part 1: Source Scoring + Recommendations).

Детерминированный скоринг известных источников и автоматические рекомендации
для content_type/topic/language. Не требует внешних сетей.
"""
from dataclasses import dataclass
from typing import List, Optional

from .source_registry import SOURCES, SourceDefinition

# Капабилити, релевантные для каждого content_type (используются в скоринге)
CAPABILITY_RELEVANCE = {
    "manga": ("chapters", "covers", "descriptions", "genres"),
    "anime": ("episodes", "covers", "descriptions", "genres"),
    "news": ("articles", "summaries", "covers"),
}

WEIGHT_CONTENT_TYPE = 40.0
WEIGHT_TOPIC = 20.0
WEIGHT_LANGUAGE = 10.0
WEIGHT_CAPABILITIES = 20.0
WEIGHT_RATE_LIMIT = 10.0
PENALTY_API_KEY = 15.0


@dataclass(frozen=True)
class SourceScore:
    """Оценка источника под конкретный content_type/topic/language."""

    source_id: str
    name: str
    score: float  # 0..100
    content_type: str
    capabilities: tuple
    matched_capabilities: tuple
    reason: str = ""


class SourceDiscoveryEngine:
    """Scoring + рекомендации источников."""

    @staticmethod
    def score_source(
        defn: SourceDefinition,
        content_type: str,
        topic: Optional[str] = None,
        language: Optional[str] = None,
    ) -> SourceScore:
        """Детерминированный скоринг 0..100."""
        if content_type not in defn.content_types:
            return SourceScore(
                defn.id, defn.name, 0.0, content_type,
                defn.capabilities, (),
                reason=f"unsupported content_type '{content_type}'",
            )

        score = WEIGHT_CONTENT_TYPE

        if topic and topic in defn.topics:
            score += WEIGHT_TOPIC

        if language and language in defn.languages:
            score += WEIGHT_LANGUAGE

        relevant = CAPABILITY_RELEVANCE.get(content_type, defn.capabilities)
        matched = tuple(c for c in relevant if c in defn.capabilities)
        if relevant:
            score += WEIGHT_CAPABILITIES * (len(matched) / len(relevant))

        # Чем выше rate_limit (req/hr), тем больше headroom -> выше счёт
        score += min(WEIGHT_RATE_LIMIT, defn.rate_limit / 40.0)

        if defn.requires_api_key:
            score -= PENALTY_API_KEY

        score = max(0.0, min(100.0, round(score, 1)))
        reason = f"matched capabilities: {', '.join(matched) or 'none'}"
        return SourceScore(
            defn.id, defn.name, score, content_type,
            defn.capabilities, matched, reason,
        )

    @staticmethod
    def recommend(
        content_type: str,
        topic: Optional[str] = None,
        language: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> List[SourceScore]:
        """Рейтинг источников под content_type, отсортированный по score desc."""
        results = [
            SourceDiscoveryEngine.score_source(d, content_type, topic, language)
            for d in SOURCES.values()
        ]
        results = [r for r in results if r.score > 0]
        results.sort(key=lambda r: r.score, reverse=True)
        if top_k:
            results = results[:top_k]
        return results