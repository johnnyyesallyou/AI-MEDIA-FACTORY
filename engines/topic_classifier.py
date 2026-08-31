"""Sprint 65.1: Deterministic topic classifier with synonyms.

Используется как fallback когда LLM недоступна.
"""
from typing import List, Dict
from core.models.wizard_intelligence import ChannelIntent


# Synonyms для каждой тематики
DOMAIN_SYNONYMS: Dict[str, List[str]] = {
    # Technology
    "technology": [
        "технологии", "технологий", "technology", "tech",
        "айти", "it", "программирование", "programming",
        "software", "софт", "разработка", "development",
        "код", "code", "компьютер", "computer", "гаджеты", "gadgets"
    ],
    
    # AI
    "artificial_intelligence": [
        "искусственный интеллект", "ии", "ai", "artificial intelligence",
        "нейросети", "нейросеть", "neural network", "machine learning",
        "машинное обучение", "ml", "deep learning", "llm", "gpt",
        "chatgpt", "openai", "anthropic", "claude"
    ],
    
    # Automotive
    "automotive": [
        "автомобили", "авто", "cars", "car", "automotive",
        "машина", "машины", "автопром", "tesla", "тесла",
        "электромобили", "electric cars", "bmw", "mercedes",
        "audi", "toyota", "тест-драйв", "test drive",
        "авто новости", "car news", "automotive news"
    ],
    
    # Science
    "science": [
        "наука", "science", "научный", "scientific",
        "биология", "biology", "физика", "physics",
        "химия", "chemistry", "космос", "space", "астрономия", "astronomy",
        "исследования", "research", "открытия", "discoveries"
    ],
    
    # Gaming
    "gaming": [
        "игры", "games", "gaming", "гейминг",
        "видеоигры", "video games", "видеоигр", "игра",
        "консоль", "console", "playstation", "xbox", "nintendo", "steam",
        "pc gaming", "esports", "киберспорт", "cybersport",
        "геймер", "gamer", "игровой", "игровые"
    ],
    
    # Business
    "business": [
        "бизнес", "business", "предпринимательство", "entrepreneurship",
        "финансы", "finance", "экономика", "economics",
        "стартапы", "startups", "инвестиции", "investments",
        "рынок", "market", "компании", "companies"
    ],
    
    # Crypto
    "cryptocurrency": [
        "крипта", "криптовалюта", "crypto", "cryptocurrency",
        "биткоин", "bitcoin", "btc", "эфир", "ethereum", "eth",
        "блокчейн", "blockchain", "defi", "nft", "web3"
    ],
    
    # Movies
    "movies": [
        "кино", "cinema", "movies", "фильмы", "movie",
        "сериалы", "series", "netflix", "обзоры", "reviews",
        "рецензии", "critics", "трейлеры", "trailers"
    ],
    
    # Manga
    "manga": [
        "манга", "manga", "комиксы", "comics",
        "глава", "chapter", "том", "volume"
    ],
    
    # Anime
    "anime": [
        "аниме", "anime", "мультсериал", "анимация", "animation"
    ],
    
    # News (general)
    "news": [
        "новости", "news", "события", "events",
        "актуальное", "breaking", "лента", "feed"
    ],
}

TOPIC_SYNONYMS: Dict[str, List[str]] = {
    "car_news": ["авто новости", "car news", "automotive news", "новости авто"],
    "new_models": ["новые модели", "new models", "новинки", "премьера"],
    "electric_cars": ["электромобили", "electric cars", "ev", "электрокар"],
    "reviews": ["обзоры", "reviews", "тест-драйв", "test drive"],
    
    "ai_news": ["новости ии", "ai news", "новости нейросетей"],
    "llm": ["llm", "языковые модели", "language models"],
    "ai_products": ["ai продукты", "ai products", "ai сервисы"],
    
    "biology": ["биология", "biology", "животные", "animals", "растения", "plants"],
    "physics": ["физика", "physics", "квантовая", "quantum"],
    "space": ["космос", "space", "астрономия", "astronomy"],
    
    "new_games": ["новые игры", "new games", "релизы", "releases"],
    "game_reviews": ["обзоры игр", "game reviews", "рецензии"],
    
    "startups": ["стартапы", "startups", "startup"],
    "finance": ["финансы", "finance", "деньги", "money"],
}


def classify_intent(description: str, name: str = "") -> ChannelIntent:
    """Классифицирует описание пользователя в ChannelIntent."""
    text = f"{description} {name}".lower()
    
    # Domain scoring
    domain_scores = {}
    for domain, synonyms in DOMAIN_SYNONYMS.items():
        score = sum(1 for syn in synonyms if syn in text)
        if score > 0:
            domain_scores[domain] = score
    
    if not domain_scores:
        return ChannelIntent(
            raw_description=description,
            domain="general",
            topic="general",
            confidence=0.3,
            reasoning="No keywords matched, using general profile"
        )
    
    # Best domain
    best_domain = max(domain_scores, key=domain_scores.get)
    best_score = domain_scores[best_domain]
    
    # Confidence: учитываем уникальность matches
    # Если много общих слов (news, информация) - снижаем confidence
    unique_keywords = sum(1 for domain in domain_scores if domain_scores[domain] == best_score)
    if unique_keywords > 1:
        # Несколько domains с одинаковым score - снижаем confidence
        confidence = min(best_score / 4.0, 0.7)
    else:
        confidence = min(best_score / 2.0, 1.0)
    
    # Topic scoring (for best domain)
    topic_scores = {}
    for topic, synonyms in TOPIC_SYNONYMS.items():
        if best_domain in topic or topic.startswith(best_domain.split("_")[0]):
            score = sum(1 for syn in synonyms if syn in text)
            if score > 0:
                topic_scores[topic] = score
    
    best_topic = max(topic_scores, key=topic_scores.get) if topic_scores else best_domain
    
    # Subtopics
    subtopics = [t for t, s in topic_scores.items() if s > 0][:3]
    
    # Content type inference
    content_types = []
    if best_domain in ["manga", "anime"]:
        content_types = [best_domain]
    elif best_domain in ["news", "technology", "automotive", "science", "business", "artificial_intelligence"]:
        content_types = ["news"]
    
    # Frequency inference
    frequency = "daily"
    if any(w in text for w in ["ежечасно", "hourly", "breaking"]):
        frequency = "hourly"
    elif any(w in text for w in ["еженедельно", "weekly"]):
        frequency = "weekly"
    
    return ChannelIntent(
        raw_description=description,
        domain=best_domain,
        topic=best_topic,
        subtopics=subtopics,
        content_goal="information" if best_domain != "gaming" else "entertainment",
        language="ru",
        content_frequency=frequency,
        suggested_content_types=content_types,
        confidence=confidence,
        reasoning=f"Matched {domain_scores[best_domain]} keywords for domain '{best_domain}'"
    )