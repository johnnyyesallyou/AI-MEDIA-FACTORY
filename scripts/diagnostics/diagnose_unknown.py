import sys, json
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.content_orm import ContentORM

print("=" * 70)
print("DIAGNOSTICS: Unknown titles")
print("=" * 70)

db = SessionLocal()
items = db.query(ContentORM).filter(
    ContentORM.headline.like("%Unknown%")
).all()

print(f"Items with 'Unknown' in headline: {len(items)}")

for it in items[:5]:
    meta = json.loads(it.source_text)
    print(f"\n  Headline: {it.headline}")
    print(f"  manga_title_name: {meta.get('manga_title_name')}")
    print(f"  manga_title_name_en: {meta.get('manga_title_name_en')}")
    print(f"  manga_title_id: {meta.get('manga_title_id', '')[:20]}")
    print(f"  asset_id: {it.asset_id}")
    print(f"  image_url: {it.image_url}")

db.close()
print("=" * 70)