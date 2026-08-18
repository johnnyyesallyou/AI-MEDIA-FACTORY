import sys
import json
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from engines.asset.manager import AssetManager
from engines.source_adapters.remanga_adapter import ReMangaAdapter
from backend.automation.jobs.manga_publish_job import MangaPublishJob
from datetime import datetime
import uuid

print("=" * 70)
print("FIXED: Manual cover download + publish")
print("=" * 70)

adapter = ReMangaAdapter()
info = adapter.get_title_info("descendants-of-the-hero")

# Берём ОРИГИНАЛЬНУЮ обложку из title info
cover_path = info.get("cover", {}) if isinstance(info.get("cover"), dict) else {}
# info['cover'] is a dict with low/mid/high keys
# Но get_title_info возвращает упрощенную структуру — нужно получить оригинал
# Получаем напрямую через last-chapters API где есть cover
latest = adapter.fetch_latest_chapters(limit=50)
desc_item = next((c for c in latest if c.title_slug == "descendants-of-the-hero"), None)

if desc_item:
    cover_url = desc_item.cover_url
    chapter_url = desc_item.chapter_url
    chapter_number = desc_item.chapter_number
    title_id = desc_item.title_id
    print(f"\nFound in latest: chapter {chapter_number}")
else:
    # fallback на любую обложку
    print("\nNot in latest, using dummy chapter 99 with real cover")
    cover_url = "https://remanga.org/media/titles/descendants-of-the-hero/cover_fa6edf1713d24bda.webp"
    chapter_url = "https://remanga.org/manga/descendants-of-the-hero/1972689"
    chapter_number = "99"
    title_id = "155919"

print(f"Cover URL: {cover_url}")
print(f"Chapter URL: {chapter_url}")

# Метаданные
metadata = {
    "type": "manga_chapter",
    "manga_source": "remanga",
    "manga_title_id": title_id,
    "manga_title_name": "Потомки героя",
    "manga_title_name_en": "Descendants of the hero",
    "manga_title_slug": "descendants-of-the-hero",
    "manga_chapter_number": chapter_number,
    "manga_chapter_id": "1972689",
    "manga_cover_url": cover_url,
    "manga_title_url": "https://remanga.org/manga/descendants-of-the-hero",
    "manga_chapter_url": chapter_url,
    "manga_description": info.get("description", ""),
    "manga_genres": info.get("genres", []),
    "manga_type": info.get("type", ""),
    "manga_status": info.get("status", ""),
    "manga_total_chapters": info.get("count_chapters", 0),
}

db = SessionLocal()
manga_channel = db.query(ChannelORM).filter(
    ChannelORM.name == "Манга — новые главы"
).first()

# Создаём content
content = ContentORM(
    id=str(uuid.uuid4()),
    channel_id=manga_channel.id,
    headline=f"📚 Новая глава: Потомки героя — глава {chapter_number}",
    draft_text=f"**Потомки героя** — глава {chapter_number}",
    source_url=chapter_url,
    source_text=json.dumps(metadata, ensure_ascii=False),
    status="research",
    created_at=datetime.utcnow(),
)
db.add(content)
db.commit()
db.refresh(content)
print(f"\n✅ Content created: {content.id}")

# Скачиваем обложку вручную через AssetManager
print("\n[1] Downloading cover via AssetManager...")
asset_mgr = AssetManager()
asset = asset_mgr.save_from_url(
    image_url=cover_url,
    content_id=content.id,
    prompt="Потомки героя",
    model="manga_cover",
    width=400,
    height=600
)

if asset:
    content.asset_id = asset.id
    content.image_url = asset.public_url
    db.commit()
    print(f"  ✅ Asset saved: {asset.public_url}")
    print(f"  Size: {asset.extra_data.get('file_size_bytes', '?')} bytes")
else:
    print("  ❌ Asset download failed")
    db.close()
    sys.exit(1)

# Публикуем
print("\n[2] Publishing via MangaPublishJob (limit=1)...")
job = MangaPublishJob()
result = job.run(limit=1)
print(f"  Result: {result}")

# Проверяем
content = db.query(ContentORM).filter(ContentORM.id == content.id).first()
print(f"\n[3] Published:")
print(f"  Status: {content.status}")
print(f"  Telegram message_id: {content.telegram_message_id}")
print(f"  Published at: {content.published_at}")

db.close()

print("\n" + "=" * 70)
print("✅ CHECK @manga_new_chapters for the post!")
print("=" * 70)
