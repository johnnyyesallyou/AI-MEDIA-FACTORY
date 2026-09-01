"""Sprint 67.4: Регистрация стратегий для ВСЕХ архетипов."""
from core.models.archetypes import Archetype
from backend.engines.strategy_registry import register_strategies
from backend.engines.news_strategies import (
    NewsResearchStrategy, NewsGenerationStrategy,
    NewsMediaStrategy, NewsPublishingStrategy,
)
from backend.engines.generic_strategies import (
    GenericResearchStrategy, GenericGenerationStrategy,
    GenericMediaStrategy, GenericPublishingStrategy,
)


def register_all_strategies():
    # NEWS — специализированные стратегии
    register_strategies(
        Archetype.NEWS,
        NewsResearchStrategy, NewsGenerationStrategy,
        NewsMediaStrategy, NewsPublishingStrategy,
    )
    # Остальные 7 — generic (параметризованы архетипом)
    for archetype in Archetype:
        if archetype == Archetype.NEWS:
            continue
        register_strategies(
            archetype,
            GenericResearchStrategy, GenericGenerationStrategy,
            GenericMediaStrategy, GenericPublishingStrategy,
        )


register_all_strategies()