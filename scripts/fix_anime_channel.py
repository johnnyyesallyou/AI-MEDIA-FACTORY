import sys, json
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

db = SessionLocal()
anime = db.query(ChannelORM).filter(ChannelORM.id == "35a85a18-7a61-4386-9d96-c64fac0fa217").first()

if anime:
    print(f"Канал: {anime.name}")
    print(f"  Текущий content_profile: {anime.content_profile}")
    
    # Обновляем content_profile: правильные sources
    profile = anime.content_profile or {}
    profile["sources"] = ["anilist", "myanimelist"]
    profile["content_type"] = "anime"
    profile["topic"] = "news"
    profile["profile_key"] = "anime_news"
    
    anime.content_profile = profile
    db.commit()
    
    print(f"\n  Обновлённый content_profile:")
    print(f"    sources: {profile['sources']}")
    print(f"    content_type: {profile['content_type']}")
    print(f"    topic: {profile['topic']}")
    print(f"    profile_key: {profile['profile_key']}")
else:
    print("[!] Anime канал не найден")

db.close()