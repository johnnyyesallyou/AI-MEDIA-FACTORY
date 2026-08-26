import pathlib

# === FIX 1: manga_research_job.py — убрать вызов .merge() ===
p1 = pathlib.Path("/app/backend/automation/jobs/manga_research_job.py")
c1 = p1.read_text(encoding="utf-8")

# Ищем блок с self.enricher.merge()
# Заменяем на enricher.enrich(title) который делает merge внутри
old_pattern = '''                    # Обогащаем данные из всех источников
                    sources_data = self.enricher._build_sources_data(title)
                    desc, genres, cover = self.enricher.merge(sources_data)
                    
                    if desc:
                        title.description = desc
                    if genres:
                        title.genres = genres
                    if cover:
                        title.cover_url = cover'''

new_pattern = '''                    # Обогащаем через новый API (enrich сам делает merge внутри)
                    self.enricher.enrich(title)'''

if old_pattern in c1:
    c1 = c1.replace(old_pattern, new_pattern, 1)
    p1.write_text(c1, encoding="utf-8")
    print("[OK] FIX 1: manga_research_job.py — .merge() → .enrich()")
else:
    print("[?] FIX 1: pattern not found, checking alternatives...")

# === FIX 2: channel_profiles.py — anime_news content_type ===
p2 = pathlib.Path("/app/engines/channel_profiles.py")
c2 = p2.read_text(encoding="utf-8")

# Меняем content_type с "news" на "anime" для anime_news
c2 = c2.replace(
    '''    "anime_news": {
        "theme": "anime",
        "content_type": "news",''',
    '''    "anime_news": {
        "theme": "anime",
        "content_type": "anime",  # Sprint 51: не news, чтобы не попадал под AI fallback'''
)

# Меняем image_policy.fallback на "none" (только реальные картинки)
c2 = c2.replace(
    '''        "image_policy": {
            "mode": "source_first",
            "preferred": "anime_visual",
            "fallback": "ai_generated",
            "style": "anime"
        },''',
    '''        "image_policy": {
            "mode": "source_first",
            "preferred": "anime_visual",
            "fallback": "none",  # Sprint 51: только реальные key visual из AniList
            "style": "anime"
        },'''
)

# Включаем RU-фильтры
c2 = c2.replace(
    '''        "publishing_policy": {
            "platform": "telegram",
            "min_interval_seconds": 2.5,
            "max_per_minute": 24,
            "require_ru_title": False,
            "strip_non_ru_description": False,''',
    '''        "publishing_policy": {
            "platform": "telegram",
            "min_interval_seconds": 2.5,
            "max_per_minute": 24,
            "require_ru_title": True,   # Sprint 51: только RU тайтлы
            "strip_non_ru_description": True,  # Sprint 51: убираем EN описания'''
)

p2.write_text(c2, encoding="utf-8")
print("[OK] FIX 2-4: channel_profiles.py — content_type=anime, fallback=none, RU-only")
