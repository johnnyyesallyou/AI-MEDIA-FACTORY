import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from engines.source_image_resolver import SourceImageResolver

print("=" * 70)
print("TESTING SourceImageResolver (first 5 news)")
print("=" * 70)

db = SessionLocal()

# ????? ?????? 5 news items
items = db.query(ContentORM).filter(
    ContentORM.status == "approved",
    ContentORM.asset_id == None,
    ContentORM.source_url != None,
    ~ContentORM.source_url.like("%remanga.org%"),
    ~ContentORM.source_url.like("%mangadex.org%")
).limit(5).all()

print(f"\nTesting {len(items)} news items:")

resolver = SourceImageResolver()
success_count = 0

for i, item in enumerate(items, 1):
    print(f"\n{i}. {item.headline[:50]}...")
    print(f"   Source: {item.source_url[:80]}")
    
    try:
        asset_id = resolver.resolve_and_save(item.id, item.source_url)
        
        if asset_id:
            # ????????? content
            db.refresh(item)
            print(f"   ? Saved! asset_id={asset_id[:20]}...")
            print(f"   image_url: {item.image_url}")
            success_count += 1
        else:
            print(f"   ? No image found")
    except Exception as e:
        print(f"   ? Error: {type(e).__name__}: {e}")

db.commit()
db.close()

print("\n" + "=" * 70)
print(f"RESULT: {success_count}/{len(items)} images extracted")
print("=" * 70)
