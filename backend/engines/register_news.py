"""Sprint 67.3: Регистрация News strategies в registry."""
from core.models.archetypes import Archetype
from backend.engines.strategy_registry import register_strategies
from backend.engines.news_strategies import (
    NewsResearchStrategy,
    NewsGenerationStrategy,
    NewsMediaStrategy,
    NewsPublishingStrategy,
)


def register_news_strategies():
    """Зарегистрировать News strategies для архетипа NEWS."""
    register_strategies(
        archetype=Archetype.NEWS,
        research=NewsResearchStrategy,
        generation=NewsGenerationStrategy,
        media=NewsMediaStrategy,
        publishing=NewsPublishingStrategy,
    )


register_news_strategies()