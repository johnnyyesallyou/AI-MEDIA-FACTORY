import sys, json
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

MIGRATIONS = {
    "24df0f84-46c2-4df4-ab39-d76881b35438": {  # Новости
        "content_type": "news",
        "topic": "technology",
        "profile_key": "ai_news",
    },
    "manga-channel-001": {  # Манга
        "content_type": "manga",
        "topic": "new_chapters",
        "profile_key": "manga_releases",
    },
    "b76c7996-b904-4210-ab1f-c68699d004fb": {  # VK AI Media Factory
        "content_type": "news",
        "topic": "technology",
        "profile_key": "ai_news",
    },
}

db = SessionLocal()
channels = db.query(ChannelORM).all()

for ch in channels:
    if ch.id in MIGRATIONS:
        profile = ch.content_profile or {}
        profile.update(MIGRATIONS[ch.id])
        ch.content_profile = profile
        print(f"[OK] {ch.name}: profile_key={profile['profile_key']}")

db.commit()

print("\n=== Финальное состояние каналов ===")
channels = db.query(ChannelORM).all()
for ch in channels:
    profile = ch.content_profile or {}
    print(f"\n{ch.name}:")
    print(f"  content_type: {profile.get('content_type')}")
    print(f"  topic: {profile.get('topic')}")
    print(f"  profile_key: {profile.get('profile_key')}")
    print(f"  sources: {profile.get('sources')}")
    print(f"  job_type: {profile.get('job_type')}")

db.close()