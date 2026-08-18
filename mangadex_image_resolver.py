import sys, json, requests, os, uuid, re
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.content_orm import ContentORM

print("=" * 70)
print("MANGADEX IMAGE RESOLVER")
print("=" * 70)

db = SessionLocal()
items = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.asset_id == None
).all()

print(f"Items to process: {len(items)}")

# Группируем по manga_id
UA = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
by_id = {}
for it in items:
    try:
        meta = json.loads(it.source_text)
        mid = meta.get("manga_title_id")
        if mid:
            by_id.setdefault(mid, []).append(it)
    except Exception:
        pass

print(f"Unique manga IDs: {len(by_id)}")

# Batch fetch covers from MangaDex API
COVER_BASE = "https://uploads.mangadex.org/covers"
covers = {}  # manga_id -> cover_url

id_list = list(by_id.keys())
for i in range(0, len(id_list), 100):
    chunk = id_list[i:i+100]
    try:
        r = requests.get("https://api.mangadex.org/manga",
                        params=[("ids[]", m) for m in chunk] + [("includes[]", "cover_art")],
                        headers=UA, timeout=30)
        if r.status_code != 200:
            continue
        for m in r.json().get("data", []):
            manga_id = m.get("id")
            cover_file = None
            for rel in m.get("relationships", []) or []:
                if rel.get("type") == "cover_art":
                    cover_file = (rel.get("attributes") or {}).get("fileName")
                    break
            if cover_file:
                covers[manga_id] = f"{COVER_BASE}/{manga_id}/{cover_file}.512.jpg"
    except Exception as e:
        print(f"  batch err: {e}")

print(f"Covers fetched: {len(covers)}")

# Download covers via AssetManager
from engines.asset.manager import AssetManager
asset_mgr = AssetManager()
downloaded = 0

for manga_id, items_group in by_id.items():
    cover_url = covers.get(manga_id)
    if not cover_url:
        continue
    
    try:
        asset = asset_mgr.save_from_url(
            image_url=cover_url,
            content_id=items_group[0].id,
            prompt="",
            model="mangadex_cover"
        )
        if asset:
            for it in items_group:
                it.asset_id = asset.id
                it.image_url = asset.public_url
                # Обновляем metadata с cover_url
                meta = json.loads(it.source_text)
                meta["manga_cover_url"] = cover_url
                it.source_text = json.dumps(meta, ensure_ascii=False)
            downloaded += 1
    except Exception as e:
        print(f"  download err {manga_id[:8]}: {e}")

db.commit()

# Stats
with_asset = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.asset_id != None
).count()
print(f"\n✅ Downloaded covers for {downloaded} manga groups")
print(f"✅ Items with covers now: {with_asset}")
db.close()
print("=" * 70)