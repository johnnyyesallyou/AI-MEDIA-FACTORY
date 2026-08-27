import sys, json
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from sqlalchemy.orm.attributes import flag_modified

MIGRATIONS = {
    "24df0f84-46c2-4df4-ab39-d76881b35438": {  # Новости
        "content_type": "news",
        "topic": "technology",
        "profile_key": "ai_news",
    },
    "35a85a18-7a61-4386-9d96-c64fac0fa217": {  # Anime (уже обновлён)
        "content_type": "anime",
        "topic": "news",
        "profile_key": "anime_news",
    },
    "manga-channel-001": {  # Манга
        "content_type": "manga",
        "topic": "new_chapters",
        "profile_key": "manga_releases",
    },
    "b76c7996-b904-4210-ab1f-c68699d004fb": {  # VK
        "content_type": "news",
        "topic": "technology",
        "profile_key": "ai_news",
    },
}

db = SessionLocal()
channels = db.query(ChannelORM).all()

print("=== Применение миграции с flag_modified ===\n")
for ch in channels:
    if ch.id in MIGRATIONS:
        # Получаем текущий profile или создаём новый dict
        profile = ch.content_profile.copy() if ch.content_profile else {}
        profile.update(MIGRATIONS[ch.id])
        
        # Переназначаем значение И флагуем как modified
        ch.content_profile = profile
        flag_modified(ch, "content_profile")  # КРИТИЧНО для JSONB!
        
        print(f"[OK] {ch.name}:")
        print(f"  profile_key: {profile['profile_key']}")
        print(f"  content_type: {profile['content_type']}")
        print(f"  topic: {profile['topic']}")
        print()

db.commit()
print("[OK] Commit завершён\n")

# Проверка
print("=== Финальная проверка ===\n")
channels = db.query(ChannelORM).all()
for ch in channels:
    profile = ch.content_profile or {}
    print(f"{ch.name}:")
    print(f"  profile_key: {profile.get('profile_key')}")
    print(f"  content_type: {profile.get('content_type')}")
    print(f"  topic: {profile.get('topic')}")
    print(f"  sources: {profile.get('sources')}")
    print()

db.close()