import sys, json, time, requests
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from engines.asset.manager import AssetManager

print("=" * 70)
print("MANGADEX ENRICHMENT (individual requests)")
print("=" * 70)

db = SessionLocal()
items = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.source_url.like("%mangadex.org%")
).all()

print(f"MangaDex items: {len(items)}")

UA = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
COVER_BASE = "https://uploads.mangadex.org/covers"
asset_mgr = AssetManager()

enriched = 0
covers_downloaded = 0

# Группируем по manga_id
by_id = {}
for it in items:
    meta = json.loads(it.source_text)
    mid = meta.get("manga_title_id")
    if mid:
        by_id.setdefault(mid, []).append(it)

print(f"Unique manga IDs: {len(by_id)}")

# Индивидуальные запросы
for manga_id, items_group in by_id.items():
    try:
        r = requests.get(
            f"https://api.mangadex.org/manga/{manga_id}",
            params=[("includes[]", "cover_art")],
            headers=UA,
            timeout=10
        )
        
        if r.status_code != 200:
            continue
        
        data = r.json().get("data", {})
        attrs = data.get("attributes", {})
        
        # Description
        desc_obj = attrs.get("description", {}) or {}
        desc = desc_obj.get("ru") or desc_obj.get("en") or ""
        
        # Tags
        tags = []
        for t in attrs.get("tags", []) or []:
            name = (t.get("attributes") or {}).get("name", {}).get("en")
            if name:
                tags.append(name)
        
        # Cover
        cover_file = None
        for rel in data.get("relationships", []) or []:
            if rel.get("type") == "cover_art":
                cover_file = (rel.get("attributes") or {}).get("fileName")
                break
        
        cover_url = f"{COVER_BASE}/{manga_id}/{cover_file}.512.jpg" if cover_file else None
        
        # Обновляем все items этой манги
        for it in items_group:
            meta = json.loads(it.source_text)
            
            # Enrichment
            if desc and not meta.get("manga_description"):
                meta["manga_description"] = desc
                enriched += 1
            
            if tags and not meta.get("manga_genres"):
                meta["manga_genres"] = tags
            
            meta["manga_type"] = "Манга"
            it.source_text = json.dumps(meta, ensure_ascii=False)
            
            # Cover download
            if it.asset_id is None and cover_url:
                try:
                    asset = asset_mgr.save_from_url(
                        image_url=cover_url,
                        content_id=it.id,
                        prompt="",
                        model="mangadex_cover"
                    )
                    if asset:
                        it.asset_id = asset.id
                        it.image_url = asset.public_url
                        meta["manga_cover_url"] = cover_url
                        it.source_text = json.dumps(meta, ensure_ascii=False)
                        covers_downloaded += 1
                except Exception as e:
                    pass
        
        time.sleep(0.5)  # Rate limit
        
    except Exception as e:
        print(f"  Error for {manga_id[:12]}: {e}")
        continue

db.commit()

with_asset = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.asset_id != None,
    ContentORM.source_url.like("%mangadex.org%")
).count()

print(f"\n✅ Enriched: {enriched}")
print(f"✅ Covers downloaded: {covers_downloaded}")
print(f"✅ MangaDex items with covers: {with_asset}")

total_with_asset = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.asset_id != None
).count()
print(f"✅ Total items with covers (ReManga + MangaDex): {total_with_asset}")

db.close()
print("=" * 70)