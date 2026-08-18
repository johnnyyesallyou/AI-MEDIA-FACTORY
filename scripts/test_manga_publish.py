import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from backend.automation.jobs.manga_publish_job import MangaPublishJob

print("=" * 70)
print("TESTING MangaPublishJob (limit=1 - ОДИН пост)")
print("=" * 70)

# Проверка перед
db = SessionLocal()
research_count = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.asset_id != None,
    ContentORM.source_url.like("%remanga.org%")
).count()
published_count = db.query(ContentORM).filter(
    ContentORM.status == "published",
    ContentORM.source_url.like("%remanga.org%")
).count()
print(f"\n[1] Before:")
print(f"    Research items with covers: {research_count}")
print(f"    Published manga posts: {published_count}")
db.close()

# Запуск (только 1 пост!)
print("\n[2] Running MangaPublishJob (limit=1)...")
job = MangaPublishJob()
result = job.run(limit=1)
print(f"  Result: {result}")

# Проверка после
db = SessionLocal()
research_after = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.asset_id != None,
    ContentORM.source_url.like("%remanga.org%")
).count()
published_after = db.query(ContentORM).filter(
    ContentORM.status == "published",
    ContentORM.source_url.like("%remanga.org%")
).count()

print(f"\n[3] After:")
print(f"    Research items with covers: {research_after} (-{research_count - research_after})")
print(f"    Published manga posts: {published_after} (+{published_after - published_count})")

# Показываем опубликованный пост
if published_after > published_count:
    print("\n[4] Last published manga post:")
    item = db.query(ContentORM).filter(
        ContentORM.status == "published",
        ContentORM.source_url.like("%remanga.org%")
    ).order_by(ContentORM.published_at.desc()).first()
    
    if item:
        print(f"    Headline: {item.headline}")
        print(f"    Telegram message_id: {item.telegram_message_id}")
        print(f"    Image URL: {item.image_url}")
        print(f"    Published at: {item.published_at}")
        print(f"\n    Draft text:")
        print("    " + "\n    ".join(item.draft_text.split("\n")))
db.close()

print("\n" + "=" * 70)
print("CHECK Telegram channel @manga_new_chapters for the post!")
print("=" * 70)
