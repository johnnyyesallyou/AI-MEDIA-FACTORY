import sys, json, time
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.content_orm import ContentORM

print("=" * 70)
print("RE:MANGA FULL ENRICHMENT + IMAGES")
print("=" * 70)

db = SessionLocal()
items = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.source_url.like("%remanga.org%")
).all()

print(f"ReManga items: {len(items)}")

from engines.source_adapters import ReMangaAdapter
from engines.asset.manager import AssetManager

adapter = ReMangaAdapter()
asset_mgr = AssetManager()

enriched = 0
covers_downloaded = 0

for it in items:
    meta = json.loads(it.source_text)
    slug = meta.get("manga_title_slug")
    if not slug:
        continue
    
    # Enrichment
    if not meta.get("manga_description"):
        try:
            info = adapter.get_title_info(slug)
            if info:
                meta["manga_description"] = info.get("description", "")
                meta["manga_genres"] = info.get("genres", [])
                meta["manga_type"] = info.get("type", "")
                it.source_text = json.dumps(meta, ensure_ascii=False)
                enriched += 1
        except Exception as e:
            pass
        time.sleep(0.3)
    
    # Cover download
    if it.asset_id is None and meta.get("manga_cover_url"):
        try:
            cover_url = meta["manga_cover_url"]
            asset = asset_mgr.save_from_url(
                image_url=cover_url,
                content_id=it.id,
                prompt="",
                model="remanga_cover"
            )
            if asset:
                it.asset_id = asset.id
                it.image_url = asset.public_url
                covers_downloaded += 1
        except Exception as e:
            pass

db.commit()

with_asset = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.asset_id != None,
    ContentORM.source_url.like("%remanga.org%")
).count()

print(f"\n✅ Enriched: {enriched}")
print(f"✅ Covers downloaded: {covers_downloaded}")
print(f"✅ ReManga items with covers: {with_asset}")
db.close()
print("=" * 70)