import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from core.models.anime_knowledge import AnimeTitle, AnimeEpisode

db = SessionLocal()

# Ищем anime channel
channel = db.query(ChannelORM).filter(
    ChannelORM.name.like("%Аниме%") | ChannelORM.name.like("%Anime%")
).first()

if not channel:
    print("❌ Anime channel not found!")
    db.close()
    exit()

print(f"✅ Channel: {channel.name}")
print(f"   ID: {channel.id}")
print(f"   is_connected: {channel.is_connected}")

# Ищем anime episode
episode = db.query(AnimeEpisode).first()
if not episode:
    print("❌ No anime episodes found!")
    db.close()
    exit()

print(f"\n✅ Episode: {episode.id}")
print(f"   anime_title_id: {episode.anime_title_id}")

# Пытаемся создать ContentORM
from datetime import datetime
import uuid
import json

title = db.query(AnimeTitle).filter(AnimeTitle.id == episode.anime_title_id).first()

metadata = {
    "type": "anime_release",
    "anime_source": episode.source,
    "anime_title_id": title.id,
    "anime_title_canonical": title.canonical_title,
    "anime_episode_number": episode.episode_number,
    "anime_episode_id": episode.id,
    "anime_cover_url": title.cover_url,
}

try:
    content = ContentORM(
        id=str(uuid.uuid4()),
        channel_id=channel.id,
        headline=f"🎬 Test: {title.canonical_title}",
        draft_text="Test",
        source_url="",
        source_text=json.dumps(metadata, ensure_ascii=False),
        anime_episode_id=episode.id,
        status="research",
        created_at=datetime.utcnow(),
    )
    db.add(content)
    db.commit()
    print(f"\n✅ ContentORM created: {content.id}")
    print(f"   anime_episode_id: {content.anime_episode_id}")
except Exception as e:
    db.rollback()
    print(f"\n❌ Failed to create ContentORM: {e}")

db.close()