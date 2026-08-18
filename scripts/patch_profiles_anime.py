import pathlib

p = pathlib.Path("/app/engines/channel_profiles.py")
c = p.read_text(encoding="utf-8")

# Добавляем anime_release профиль
old = '''    "anime_news": {
        "theme": "anime",
        "content_type": "news",
        "sources": ["anime_news"],
        "image_policy": {"preferred": "anime_visual", "fallback": "ai_generated", "style": "anime"},
        "formatting_profile": {"emoji_header": "🎬"},
    },'''

new = '''    "anime_news": {
        "theme": "anime",
        "content_type": "news",
        "sources": ["anime_news"],
        "image_policy": {"preferred": "anime_visual", "fallback": "ai_generated", "style": "anime"},
        "formatting_profile": {"emoji_header": "🎬"},
    },
    "anime_release": {
        "theme": "anime",
        "content_type": "anime_release",
        "sources": ["anilist"],
        "image_policy": {"preferred": "anime_cover", "fallback": "none", "style": "anime"},
        "publishing_policy": {
            "require_ru_title": False,
            "strip_non_ru_description": False,
            "telegraph_page": True,
            "inline_buttons": True,
        },
        "formatting_profile": {
            "emoji_header": "🎬",
            "max_hashtags": 15,
            "include_description": True,
        },
        "source_policy": {"allowed_sources": ["anilist"]},
        "enrichment_policy": {"description": True, "genres": True, "cover": True},
    },'''

if old in c and "anime_release" not in c:
    c = c.replace(old, new, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ anime_release profile added")
else:
    print("ℹ️ Already added or marker not found")

# Обновляем guess_profile_key
old2 = '''    if "anime" in name or "аниме" in name:
        return "anime_news"'''

new2 = '''    if "anime" in name or "аниме" in name:
        if "news" in name or "новости" in name:
            return "anime_news"
        return "anime_release"'''

if old2 in c:
    c = c.replace(old2, new2, 1)
    p.write_text(c, encoding="utf-8")
    print("✅ guess_profile_key updated")