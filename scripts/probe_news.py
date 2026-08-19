import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM

print("=" * 70)
print("PROBE: Regular news items (non-manga)")
print("=" * 70)

db = SessionLocal()

# News items without asset_id (????? ???????)
news_no_asset = db.query(ContentORM).filter(
    ContentORM.status.in_(["research", "approved"]),
    ContentORM.asset_id == None,
    ~ContentORM.source_url.like("%remanga.org%"),
    ~ContentORM.source_url.like("%mangadex.org%")
).limit(20).all()

print(f"\nNews items without asset_id: {len(news_no_asset)}")

for i, item in enumerate(news_no_asset[:10], 1):
    print(f"\n{i}. {item.headline[:60]}")
    print(f"   Status: {item.status}")
    print(f"   Source URL: {item.source_url[:80] if item.source_url else 'None'}")
    print(f"   Image URL: {item.image_url}")
    print(f"   Created: {item.created_at}")

db.close()

print("\n" + "=" * 70)
