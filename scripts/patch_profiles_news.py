import pathlib

p = pathlib.Path("/app/engines/channel_profiles.py")
c = p.read_text(encoding="utf-8")

# Добавляем news profile (ai_news уже есть, но нам нужен более явный "news")
# Проверяем, есть ли "ai_news" — если да, обновляем его
if '"ai_news":' in c:
    # Обновляем существующий ai_news
    old = '''    "ai_news": {
        "theme": "technology",
        "content_type": "news",
        "sources": ["habr", "vc", "openai", "techcrunch", "theverge", "blog.google"],
        "image_policy": {"preferred": "og_image", "fallback": "ai_generated", "style": "news"},
        "source_policy": {"allowed_sources": ["habr", "vc", "openai", "techcrunch", "theverge", "blog.google"]},
        "formatting_profile": {"emoji_header": "📰"},
    },'''

    new = '''    "ai_news": {
        "theme": "technology",
        "content_type": "news",
        "sources": ["habr", "vc", "openai", "techcrunch", "theverge", "blog.google"],
        "image_policy": {
            "preferred": "og_image",
            "fallback": "ai_generated",
            "style": "news",
        },
        "publishing_policy": {
            "require_ru_title": False,
            "strip_non_ru_description": False,
            "telegraph_page": True,
            "inline_buttons": True,
        },
        "formatting_profile": {
            "emoji_header": "📰",
            "max_hashtags": 8,
            "include_description": True,
        },
        "source_policy": {"allowed_sources": ["habr", "vc", "openai", "techcrunch", "theverge", "blog.google"]},
        "enrichment_policy": {"description": True, "cover": True},
    },'''

    if old in c:
        c = c.replace(old, new, 1)
        print("✅ ai_news profile updated")
    else:
        print("ℹ️ ai_news already updated or marker different")

# Обновляем guess_profile_key для news
old2 = '''    if "anime" in name or "аниме" in name:
        if "news" in name or "новости" in name:
            return "anime_news"
        return "anime_release"
    return "ai_news"'''

new2 = '''    if "anime" in name or "аниме" in name:
        if "news" in name or "новости" in name:
            return "anime_news"
        return "anime_release"
    if "manga" in name or "манга" in name:
        return "manga_releases"
    # Default для news-каналов
    return "ai_news"'''

if old2 in c:
    c = c.replace(old2, new2, 1)
    print("✅ guess_profile_key updated")

p.write_text(c, encoding="utf-8")