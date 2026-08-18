import sys, json, requests
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.content_orm import ContentORM

print("=" * 70)
print("ENRICHMENT v2 (with altTitles)")
print("=" * 70)

db = SessionLocal()
items = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.source_url.like("%mangadex.org%")
).all()

UA = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
by_id = {}
for it in items:
    meta = json.loads(it.source_text)
    if not meta.get("manga_description"):
        by_id.setdefault(meta.get("manga_title_id"), []).append(it)

print(f"Items without description: {sum(len(v) for v in by_id.values())}")
print(f"Unique manga IDs: {len(by_id)}")

updated = 0
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
            attrs = m.get("attributes", {}) or {}
            
            # Description (ru -> en -> altTitles)
            desc_obj = attrs.get("description", {}) or {}
            desc = desc_obj.get("ru") or desc_obj.get("en") or ""
            
            # AltTitles (для названий если нет description)
            alt_titles = attrs.get("altTitles", []) or []
            
            # Tags
            tags = []
            for t in attrs.get("tags", []) or []:
                name = (t.get("attributes") or {}).get("name", {}).get("en")
                if name:
                    tags.append(name)
            
            for it in by_id.get(manga_id, []):
                meta = json.loads(it.source_text)
                if desc:
                    meta["manga_description"] = desc
                if tags:
                    meta["manga_genres"] = tags
                meta["manga_type"] = "Манга"
                it.source_text = json.dumps(meta, ensure_ascii=False)
                updated += 1
    except Exception as e:
        print(f"  batch err: {e}")

db.commit()
print(f"\n✅ Enriched: {updated} items")
db.close()
print("=" * 70)