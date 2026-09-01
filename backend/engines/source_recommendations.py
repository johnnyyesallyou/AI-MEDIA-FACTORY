"""Sprint 68.3: Source Recommendation — реальные URLs для research."""
from typing import Dict, List, Any


# Маппинг theme/niche → рекомендуемые источники с реальными URLs
THEME_SOURCE_URLS: Dict[str, List[Dict[str, Any]]] = {
    # Technology
    "technology": [
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "type": "rss"},
        {"name": "Ars Technica", "url": "https://arstechnica.com/feed/", "type": "rss"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "type": "rss"},
    ],
    "ai": [
        {"name": "MIT Technology Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed", "type": "rss"},
        {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "type": "rss"},
        {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "type": "rss"},
        {"name": "Papers With Code", "url": "https://paperswithcode.com/latest", "type": "web"},
    ],
    "gaming": [
        {"name": "IGN", "url": "https://feeds.feedburner.com/ign/games-all", "type": "rss"},
        {"name": "GameSpot", "url": "https://www.gamespot.com/feeds/mashup/", "type": "rss"},
        {"name": "PC Gamer", "url": "https://www.pcgamer.com/rss/", "type": "rss"},
    ],
    
    # Entertainment
    "entertainment": [
        {"name": "Reddit r/funny", "url": "https://www.reddit.com/r/funny/.rss", "type": "rss"},
        {"name": "BuzzFeed", "url": "https://www.buzzfeed.com/index.xml", "type": "rss"},
    ],
    "manga": [
        {"name": "MangaDex", "url": "https://mangadex.org/rss", "type": "rss"},
        {"name": "Anime News Network", "url": "https://www.animenewsnetwork.com/all/rss.xml", "type": "rss"},
        {"name": "MyAnimeList News", "url": "https://myanimelist.net/rss/news.xml", "type": "rss"},
    ],
    "anime": [
        {"name": "Crunchyroll News", "url": "https://www.crunchyroll.com/news/rss.xml", "type": "rss"},
        {"name": "Anime News Network", "url": "https://www.animenewsnetwork.com/all/rss.xml", "type": "rss"},
    ],
    "movies": [
        {"name": "IMDb News", "url": "https://www.imdb.com/news/rss", "type": "rss"},
        {"name": "Rotten Tomatoes", "url": "https://www.rottentomatoes.com/rss", "type": "rss"},
    ],
    "cats": [
        {"name": "Reddit r/cats", "url": "https://www.reddit.com/r/cats/.rss", "type": "rss"},
        {"name": "Reddit r/Catloaf", "url": "https://www.reddit.com/r/Catloaf/.rss", "type": "rss"},
        {"name": "Imgur Cats", "url": "https://imgur.com/t/cats/rss", "type": "rss"},
    ],
    
    # Knowledge
    "science": [
        {"name": "Nature", "url": "https://www.nature.com/nature.rss", "type": "rss"},
        {"name": "Science Daily", "url": "https://www.sciencedaily.com/rss/all.xml", "type": "rss"},
        {"name": "NASA Breaking News", "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss", "type": "rss"},
    ],
    "education": [
        {"name": "EdSurge", "url": "https://www.edsurge.com/news/rss", "type": "rss"},
        {"name": "Khan Academy Blog", "url": "https://blog.khanacademy.org/feed/", "type": "rss"},
    ],
    
    # Business/Finance
    "business": [
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "type": "rss"},
        {"name": "VentureBeat", "url": "https://venturebeat.com/feed/", "type": "rss"},
        {"name": "Product Hunt", "url": "https://www.producthunt.com/feed", "type": "rss"},
    ],
    "finance": [
        {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "type": "rss"},
        {"name": "CNBC", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", "type": "rss"},
    ],
    "crypto": [
        {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "type": "rss"},
        {"name": "Cointelegraph", "url": "https://cointelegraph.com/rss", "type": "rss"},
        {"name": "Reddit r/CryptoCurrency", "url": "https://www.reddit.com/r/CryptoCurrency/.rss", "type": "rss"},
    ],
    
    # Lifestyle
    "fitness": [
        {"name": "Reddit r/fitness", "url": "https://www.reddit.com/r/fitness/.rss", "type": "rss"},
        {"name": "Men's Health", "url": "https://www.menshealth.com/rss/all.xml", "type": "rss"},
    ],
    "cooking": [
        {"name": "Reddit r/cooking", "url": "https://www.reddit.com/r/cooking/.rss", "type": "rss"},
        {"name": "Serious Eats", "url": "https://www.seriouseats.com/recipes/rss", "type": "rss"},
    ],
    "travel": [
        {"name": "Reddit r/travel", "url": "https://www.reddit.com/r/travel/.rss", "type": "rss"},
        {"name": "Lonely Planet", "url": "https://www.lonelyplanet.com/news/rss", "type": "rss"},
    ],
    
    # General
    "news": [
        {"name": "Reuters", "url": "https://www.reutersagency.com/feed/", "type": "rss"},
        {"name": "AP News", "url": "https://apnews.com/index.rss", "type": "rss"},
    ],
    "general": [
        {"name": "Reddit r/all", "url": "https://www.reddit.com/r/all/.rss", "type": "rss"},
    ],
}


def get_source_urls(niche: str, theme: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Получить реальные URLs источников для темы/niche."""
    # Сначала niche, потом theme, fallback на general
    sources = (
        THEME_SOURCE_URLS.get(niche) or
        THEME_SOURCE_URLS.get(theme) or
        THEME_SOURCE_URLS.get("general", [])
    )
    return sources[:limit]