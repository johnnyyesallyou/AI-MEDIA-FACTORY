import sys, json, uuid
sys.path.insert(0, "/app")
from datetime import datetime
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from engines.source_adapters import ReMangaAdapter
from engines.chapter_detector import ChapterDetector

print("=" * 70)
print("LOADING NEW MANGA ITEMS")
print("=" * 70)

db = SessionLocal()
detector = ChapterDetector()
channel = db.query(ChannelORM).filter(ChannelORM.name.like("%Манга%")).first()

def create(item):
    headline = f"\U0001f4da \u041d\u043e\u0432\u0430\u044f \u0433\u043b\u0430\u0432\u0430: {item.title_name}"
    if item.chapter_number:
        headline += f" \u2014 \u0433\u043b\u0430\u0432\u0430 {item.chapter_number}"
    
    metadata = {
        "type": "manga_chapter",
        "manga_source": item.source,
        "manga_title_id": item.title_id,
        "manga_title_slug": item.title_slug,
        "manga_title_name": item.title_name,
        "manga_title_name_en": item.title_name_en,
        "manga_chapter_number": item.chapter_number,
        "manga_chapter_id": item.chapter_id,
        "manga_cover_url": item.cover_url,
        "manga_title_url": item.title_url,
        "manga_chapter_url": item.chapter_url,
        "manga_upload_date": item.upload_date.isoformat() if item.upload_date else None,
    }
    
    db.add(ContentORM(
        id=str(uuid.uuid4()),
        channel_id=channel.id,
        headline=headline,
        draft_text=headline,
        source_url=item.chapter_url or item.title_url,
        source_text=json.dumps(metadata, ensure_ascii=False),
        status="research",
        created_at=datetime.utcnow(),
    ))

adapter = ReMangaAdapter()
items = adapter.fetch_latest_chapters(limit=10)
new_items, _ = detector.detect_new_chapters(items, update_state=True)

print(f"Fetched: {len(items)}, New: {len(new_items)}")

for it in new_items:
    create(it)

db.commit()

count = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.asset_id == None
).count()

print(f"\n✅ Created {len(new_items)} new items")
print(f"Total research items without covers: {count}")
db.close()
print("=" * 70)