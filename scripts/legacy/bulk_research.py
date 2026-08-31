import sys, json, uuid
sys.path.insert(0, "/app")
from datetime import datetime
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from engines.source_adapters import ReMangaAdapter, MangaDexAdapter
from engines.chapter_detector import ChapterDetector

print("=" * 70)
print("BULK RESEARCH: stocking 100+ manga items")
print("=" * 70)

db = SessionLocal()
detector = ChapterDetector()

channel = db.query(ChannelORM).filter(ChannelORM.id == "manga-channel-001").first()
if not channel:
    channel = db.query(ChannelORM).filter(ChannelORM.is_active == True).first()
print(f"Channel: {channel.name}")

def create_research_item(item):
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
    
    content = ContentORM(
        id=str(uuid.uuid4()),
        channel_id=channel.id,
        headline=headline,
        draft_text=headline,
        source_url=item.chapter_url or item.title_url,
        source_text=json.dumps(metadata, ensure_ascii=False),
        status="research",
        created_at=datetime.utcnow(),
    )
    db.add(content)

total = 0

# ReManga: 1 страница (20 глав)
try:
    items = ReMangaAdapter().fetch_latest_chapters(limit=20)
    new_items, _ = detector.detect_new_chapters(items, update_state=True)
    print(f"remanga: fetched={len(items)} new={len(new_items)}")
    for it in new_items:
        create_research_item(it)
        total += 1
except Exception as e:
    print(f"remanga error: {e}")

# MangaDex: 2 страницы (offset 0 и 100)
adapter = MangaDexAdapter()
for off in [0, 100]:
    try:
        items = adapter.fetch_latest_chapters(limit=50, offset=off)
        new_items, _ = detector.detect_new_chapters(items, update_state=True)
        print(f"mangadex offset={off}: fetched={len(items)} new={len(new_items)}")
        for it in new_items:
            create_research_item(it)
            total += 1
    except Exception as e:
        print(f"mangadex offset={off} error: {e}")

db.commit()

research_count = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.source_url.like("%remanga.org%") | ContentORM.source_url.like("%mangadex.org%")
).count()

print(f"\nCreated: {total} research items")
print(f"Total manga research in DB: {research_count}")
db.close()
print("=" * 70)