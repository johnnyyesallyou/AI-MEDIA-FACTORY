import sys
import json
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from engines.source_adapters.remanga_adapter import ReMangaAdapter
from engines.manga_image_resolver import MangaImageResolver
from engines.url_shortener import URLShortener
from backend.automation.jobs.manga_publish_job import MangaPublishJob
from datetime import datetime
import uuid

print("=" * 70)
print("PUBLISHING FULL POST: description + genres + SHORT URL")
print("=" * 70)

# Берём популярный тайтл "Потомки героя" (descendants-of-the-hero) - уже обогащён
adapter = ReMangaAdapter()
info = adapter.get_title_info("descendants-of-the-hero")

if not info:
    print("ERROR: Cannot fetch title info")
    sys.exit(1)

print(f"\nTitle: Потомки героя")
print(f"Type: {info['type']}")
print(f"Genres: {info['genres']}")
print(f"Description: {info['description'][:100]}...")

# Получаем последнюю главу
chapters = adapter.fetch_latest_chapters(limit=20)
descendants_chapters = [c for c in chapters if c.title_slug == "descendants-of-the-hero"]

if not descendants_chapters:
    print("No chapters found for descendants-of-the-hero in latest")
    print("Using fake chapter 99 for test")
    descendants_chapters = [c for c in chapters if c.title_slug != "descendants-of-the-hero"][0:1]
    descendants_chapters[0].title_name = "Потомки героя"
    descendants_chapters[0].title_name_en = "Descendants of the hero"
    descendants_chapters[0].title_slug = "descendants-of-the-hero"
    descendants_chapters[0].chapter_number = "99"
    descendants_chapters[0].chapter_id = "999999"
    descendants_chapters[0].title_url = "https://remanga.org/manga/descendants-of-the-hero"

# Берём первый
item = descendants_chapters[0]
print(f"\nChapter: {item.chapter_number}")
print(f"Original URL: {item.chapter_url}")

# Short URL test
shortener = URLShortener()
short = shortener.shorten(item.chapter_url)
print(f"Short URL: {short}")

# Создаём metadata (обогащённый)
metadata = {
    "type": "manga_chapter",
    "manga_source": item.source,
    "manga_title_id": item.title_id,
    "manga_title_name": item.title_name,
    "manga_title_name_en": item.title_name_en,
    "manga_title_slug": item.title_slug,
    "manga_chapter_number": item.chapter_number,
    "manga_chapter_id": item.chapter_id,
    "manga_cover_url": item.cover_url,
    "manga_title_url": item.title_url,
    "manga_chapter_url": item.chapter_url,
    # Обогащение
    "manga_description": info.get("description", ""),
    "manga_genres": info.get("genres", []),
    "manga_type": info.get("type", ""),
    "manga_status": info.get("status", ""),
    "manga_total_chapters": info.get("count_chapters", 0),
}

# Создаём content в БД
db = SessionLocal()
manga_channel = db.query(ChannelORM).filter(
    ChannelORM.name == "Манга — новые главы"
).first()

content = ContentORM(
    id=str(uuid.uuid4()),
    channel_id=manga_channel.id,
    headline=f"📚 Новая глава: {item.title_name} — глава {item.chapter_number}",
    draft_text=f"**{item.title_name}** — глава {item.chapter_number}",
    source_url=item.chapter_url,
    source_text=json.dumps(metadata, ensure_ascii=False),
    status="research",
    created_at=datetime.utcnow(),
)

db.add(content)
db.commit()
db.refresh(content)
print(f"\n✅ Content created: {content.id}")

# Скачиваем обложку
print("\n[1] Downloading cover via MangaImageResolver...")
resolver = MangaImageResolver()
resolver.resolve_all_research(limit=1)

# Проверяем что обложка загружена
content = db.query(ContentORM).filter(ContentORM.id == content.id).first()
print(f"  asset_id: {content.asset_id}")
print(f"  image_url: {content.image_url}")

if not content.asset_id:
    print("  ❌ Cover download failed!")
    sys.exit(1)

# Публикуем
print("\n[2] Publishing via MangaPublishJob (limit=1)...")
job = MangaPublishJob()
result = job.run(limit=1)
print(f"  Result: {result}")

# Проверяем публикацию
content = db.query(ContentORM).filter(ContentORM.id == content.id).first()
print(f"\n[3] Published post:")
print(f"  Status: {content.status}")
print(f"  Telegram message_id: {content.telegram_message_id}")
print(f"  Published at: {content.published_at}")
print(f"\n  Draft text (preview of what was sent):")
print("  " + "\n  ".join(content.draft_text.split("\n")))

db.close()

print("\n" + "=" * 70)
print("CHECK @manga_new_chapters for the new post with SHORT URL!")
print("=" * 70)
