import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from engines.source_image_resolver import SourceImageResolver

print("=" * 70)
print("APPLYING SourceImageResolver to ALL news items")
print("=" * 70)

db = SessionLocal()

# ??? news items ??? asset_id
items = db.query(ContentORM).filter(
    ContentORM.status == "approved",
    ContentORM.asset_id == None,
    ContentORM.source_url != None,
    ~ContentORM.source_url.like("%remanga.org%"),
    ~ContentORM.source_url.like("%mangadex.org%")
).all()

print(f"\nFound {len(items)} news items without images")

resolver = SourceImageResolver()
success = 0
failed = 0

for i, item in enumerate(items, 1):
    headline = item.headline[:50] if item.headline else "(no headline)"
    source = item.source_url[:70] if item.source_url else "None"
    
    try:
        asset_id = resolver.resolve_and_save(item.id, item.source_url)
        
        if asset_id:
            success += 1
            print(f"  [{i:2d}/{len(items)}] ? {headline}")
        else:
            failed += 1
            print(f"  [{i:2d}/{len(items)}] ? No image: {headline}")
    except Exception as e:
        failed += 1
        print(f"  [{i:2d}/{len(items)}] ? Error: {type(e).__name__}: {e}")

db.close()

print("\n" + "=" * 70)
print(f"RESULT: {success}/{len(items)} images extracted, {failed} failed")
print("=" * 70)
