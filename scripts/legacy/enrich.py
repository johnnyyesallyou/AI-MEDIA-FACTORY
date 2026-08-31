import sys, json, time, requests
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.content_orm import ContentORM

print("=" * 70)
print("ENRICHMENT: adding description/genres/type")
print("=" * 70)

db = SessionLocal()
items = db.query(ContentORM).filter(ContentORM.status == "research").all()
remanga = [i for i in items if "remanga.org" in (i.source_url or "")]
mangadex = [i for i in items if "mangadex.org" in (i.source_url or "")]
print(f"research: {len(items)} (remanga={len(remanga)}, mangadex={len(mangadex)})")

# --- ReManga enrichment ---
from engines.source_adapters import ReMangaAdapter
adapter = ReMangaAdapter()
updated_r = 0
for it in remanga:
    meta = json.loads(it.source_text)
    if meta.get("manga_description"):
        continue
    slug = meta.get("manga_title_slug")
    if not slug:
        continue
    try:
        info = adapter.get_title_info(slug)
        if info:
            meta["manga_description"] = info.get("description", "")
            meta["manga_genres"] = info.get("genres", [])
            meta["manga_type"] = info.get("type", "")
            it.source_text = json.dumps(meta, ensure_ascii=False)
            updated_r += 1
    except Exception as e:
        print(f"  err {slug}: {e}")
    time.sleep(0.3)
db.commit()
print(f"remanga enriched: {updated_r}/{len(remanga)}")

# --- MangaDex enrichment (batch) ---
UA = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
by_id = {}
for it in mangadex:
    meta = json.loads(it.source_text)
    if not meta.get("manga_description"):
        by_id.setdefault(meta.get("manga_title_id"), []).append(it)

updated_m = 0
id_list = [k for k in by_id.keys() if k]
for i in range(0, len(id_list), 100):
    chunk = id_list[i:i+100]
    try:
        r = requests.get("https://api.mangadex.org/manga",
                         params=[("ids[]", m) for m in chunk] + [("includes[]", "cover_art")],
                         headers=UA, timeout=30)
        if r.status_code != 200:
            continue
        for m in r.json().get("data", []):
            attrs = m.get("attributes", {}) or {}
            desc_obj = attrs.get("description", {}) or {}
            desc = desc_obj.get("ru") or desc_obj.get("en") or ""
            tags = [ (t.get("attributes", {}).get("name", {}).get("en")) for t in (attrs.get("tags") or []) ]
            for it in by_id.get(m.get("id"), []):
                meta = json.loads(it.source_text)
                meta["manga_description"] = desc
                meta["manga_genres"] = [t for t in tags if t]
                meta["manga_type"] = "\u041c\u0430\u043d\u0433\u0430"
                it.source_text = json.dumps(meta, ensure_ascii=False)
                updated_m += 1
    except Exception as e:
        print(f"  batch err: {e}")
db.commit()
print(f"mangadex enriched: {updated_m}")
db.close()
print("=" * 70)