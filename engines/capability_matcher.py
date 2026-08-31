"""Sprint 65.1: Capability-based matching for Smart Wizard."""
from typing import List
from core.models.wizard_intelligence import ChannelIntent, ChannelStrategy
from engines.topic_classifier import classify_intent
from engines.extended_profiles import get_profile_for_domain
from engines.source_registry import SourceRegistry


def build_strategy(intent: ChannelIntent) -> ChannelStrategy:
    """Строит ChannelStrategy по ChannelIntent."""
    
    # 1. Получаем профиль по domain
    profile = get_profile_for_domain(intent.domain)
    profile_key = profile["profile_key"]
    
    # 2. Находим совместимые sources
    available_sources = SourceRegistry.get_sources_for(
        content_type=intent.suggested_content_types[0] if intent.suggested_content_types else "news",
        topic=None,
        language=intent.language
    )
    
    # 3. Фильтруем по domain (если source поддерживает)
    # TODO: расширить SourceDefinition с supported_domains
    
    # 4. Используем default sources из профиля
    sources = profile.get("default_sources", [])
    
    # 5. Fallback: если нет специфичных, берём общие news sources
    if not sources:
        sources = ["habr", "vc"]
    
    # 6. Publishing frequency
    freq_map = {
        "hourly": "30m",
        "daily": "6h",
        "weekly": "24h",
    }
    frequency = freq_map.get(intent.content_frequency, "6h")
    
    reasoning = [
        f"Domain '{intent.domain}' matched with confidence {intent.confidence:.2f}",
        f"Topic '{intent.topic}' selected",
        f"Profile '{profile_key}' provides sources: {', '.join(sources)}",
        f"Publishing frequency: {frequency} ({intent.content_frequency})",
    ]
    
    return ChannelStrategy(
        profile_key=profile_key,
        research_strategy="rss_news",  # TODO: infer from domain
        sources=sources,
        formatter=profile.get("formatter", "news_formatter"),
        media_policy=profile.get("media_policy", "source_image"),
        publishing_frequency=frequency,
        publishing_mode=profile.get("publishing_mode", "approval_required"),
        reasoning=reasoning,
    )


def suggest_strategy(description: str, name: str = "") -> tuple[ChannelIntent, ChannelStrategy]:
    """Полный pipeline: description → intent → strategy."""
    intent = classify_intent(description, name)
    strategy = build_strategy(intent)
    return intent, strategy