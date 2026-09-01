"""Sprint 67.3: Strategy Registry — регистрация стратегий для архетипов."""
from typing import Dict, Type, Any
from dataclasses import dataclass

from core.models.archetypes import Archetype


@dataclass
class StrategyBundle:
    """Набор стратегий для архетипа."""
    research: Type[Any]
    generation: Type[Any]
    media: Type[Any]
    publishing: Type[Any]


# Registry: Archetype → StrategyBundle
STRATEGY_REGISTRY: Dict[Archetype, StrategyBundle] = {}


def register_strategies(
    archetype: Archetype,
    research: Type[Any],
    generation: Type[Any],
    media: Type[Any],
    publishing: Type[Any],
) -> None:
    """Зарегистрировать набор стратегий для архетипа."""
    STRATEGY_REGISTRY[archetype] = StrategyBundle(
        research=research,
        generation=generation,
        media=media,
        publishing=publishing,
    )


def get_strategies(archetype: Archetype) -> StrategyBundle:
    """Получить набор стратегий для архетипа."""
    if archetype not in STRATEGY_REGISTRY:
        return STRATEGY_REGISTRY.get(Archetype.NEWS)
    return STRATEGY_REGISTRY[archetype]


def list_registered_archetypes() -> list:
    """Список зарегистрированных архетипов."""
    return list(STRATEGY_REGISTRY.keys())