"""Sprint 65.1: Extended profiles for Smart Wizard."""

NEW_PROFILES = {
    "technology_news": {
        "profile_key": "technology_news",
        "name": "Technology News",
        "domain": "technology",
        "topics": ["tech_news", "software", "hardware", "gadgets"],
        "default_sources": ["habr", "vc", "techcrunch", "theverge"],
        "formatter": "news_formatter",
        "media_policy": "source_image",
        "publishing_frequency": "6h",
        "publishing_mode": "approval_required",
    },
    
    "ai_news": {
        "profile_key": "ai_news",
        "name": "AI News",
        "domain": "artificial_intelligence",
        "topics": ["ai_news", "llm", "ai_products", "research"],
        "default_sources": ["habr", "techcrunch", "theverge"],  # TODO: add AI-specific
        "formatter": "news_formatter",
        "media_policy": "source_image",
        "publishing_frequency": "3h",
        "publishing_mode": "approval_required",
    },
    
    "automotive_news": {
        "profile_key": "automotive_news",
        "name": "Automotive News",
        "domain": "automotive",
        "topics": ["car_news", "new_models", "electric_cars", "reviews"],
        "default_sources": ["habr", "vc"],  # TODO: add car-specific sources
        "formatter": "news_formatter",
        "media_policy": "source_image",
        "publishing_frequency": "6h",
        "publishing_mode": "approval_required",
    },
    
    "science_news": {
        "profile_key": "science_news",
        "name": "Science News",
        "domain": "science",
        "topics": ["biology", "physics", "space", "research"],
        "default_sources": ["habr", "vc"],  # TODO: add science-specific
        "formatter": "news_formatter",
        "media_policy": "source_image",
        "publishing_frequency": "12h",
        "publishing_mode": "approval_required",
    },
    
    "gaming_news": {
        "profile_key": "gaming_news",
        "name": "Gaming News",
        "domain": "gaming",
        "topics": ["new_games", "game_reviews", "esports"],
        "default_sources": ["habr", "vc"],  # TODO: add gaming-specific
        "formatter": "news_formatter",
        "media_policy": "source_image",
        "publishing_frequency": "6h",
        "publishing_mode": "approval_required",
    },
    
    "business_news": {
        "profile_key": "business_news",
        "name": "Business News",
        "domain": "business",
        "topics": ["startups", "finance", "market", "companies"],
        "default_sources": ["habr", "vc"],  # TODO: add business-specific
        "formatter": "news_formatter",
        "media_policy": "source_image",
        "publishing_frequency": "6h",
        "publishing_mode": "approval_required",
    },
    
    "general_news": {
        "profile_key": "general_news",
        "name": "General News",
        "domain": "general",
        "topics": ["general"],
        "default_sources": ["habr", "vc", "techcrunch"],
        "formatter": "news_formatter",
        "media_policy": "source_image",
        "publishing_frequency": "6h",
        "publishing_mode": "approval_required",
    },
}


def get_profile_for_domain(domain: str) -> dict:
    """Получить профиль по domain."""
    domain_to_profile = {
        "technology": "technology_news",
        "artificial_intelligence": "ai_news",
        "automotive": "automotive_news",
        "science": "science_news",
        "gaming": "gaming_news",
        "business": "business_news",
        "news": "general_news",
        "general": "general_news",
    }
    profile_key = domain_to_profile.get(domain, "general_news")
    return NEW_PROFILES.get(profile_key, NEW_PROFILES["general_news"])