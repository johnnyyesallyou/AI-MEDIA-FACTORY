"""Channel Templates - Sprint 46.2.

Пресеты для создания канала одним кликом:
- 📰 News: Habr/VC/TechCrunch, 30 min, real photo
- 🍥 Anime: AniList, 60 min, key visual
- 📚 Manga: ReManga/MangaDex/ReadManga, 30 min, cover
"""

TEMPLATES = {
    "news": {
        "name": "News Channel",
        "description": "Автоматический новостной канал",
        "platform": "telegram",
        "language_search": "en",
        "language_publish": "ru",
        "style_profile": "news",
        "timezone": "UTC",
        "sources": [
            {"name": "Habr RSS", "source_type": "hacker_news", "url": "https://habr.com/ru/rss/articles/", "priority": 5},
            {"name": "VC.ru RSS", "source_type": "rss", "url": "https://vc.ru/rss", "priority": 4},
        ],
        "schedule": {
            "cron_expression": "0 */2 * * *",  # каждые 2 часа
            "timezone": "UTC",
            "max_posts_per_day": 12,
            "auto_publish": True,
            "is_active": True,
        },
        "image_policy": {
            "source": "real",
            "fallback": "ai_generated",
        }
    },
    "anime": {
        "name": "Anime Channel",
        "description": "Автоматический аниме-канал",
        "platform": "telegram",
        "language_search": "en",
        "language_publish": "ru",
        "style_profile": "minimal",
        "timezone": "UTC",
        "sources": [
            {"name": "AniList", "source_type": "arxiv", "url": "https://anilist.co/api/v2/graphql", "priority": 5},
        ],
        "schedule": {
            "cron_expression": "0 */1 * * *",  # каждый час
            "timezone": "UTC",
            "max_posts_per_day": 24,
            "auto_publish": True,
            "is_active": True,
        },
        "image_policy": {
            "source": "real",
            "fallback": "none",  # AI запрещён для anime
        }
    },
    "manga": {
        "name": "Manga Channel",
        "description": "Автоматический манга-канал",
        "platform": "telegram",
        "language_search": "en",
        "language_publish": "ru",
        "style_profile": "minimal",
        "timezone": "UTC",
        "sources": [
            {"name": "ReManga", "source_type": "custom_blog", "url": "https://remanga.org/api/", "priority": 5},
            {"name": "MangaDex", "source_type": "custom_blog", "url": "https://api.mangadex.org/", "priority": 4},
        ],
        "schedule": {
            "cron_expression": "0 */2 * * *",  # каждые 2 часа
            "timezone": "UTC",
            "max_posts_per_day": 12,
            "auto_publish": True,
            "is_active": True,
        },
        "image_policy": {
            "source": "real",
            "fallback": "none",  # AI запрещён для manga
        }
    }
}


def get_template(template_id: str):
    """Возвращает шаблон по ID."""
    return TEMPLATES.get(template_id)


def list_templates():
    """Возвращает список всех шаблонов."""
    return [
        {"id": tid, "name": t["name"], "description": t["description"]}
        for tid, t in TEMPLATES.items()
    ]