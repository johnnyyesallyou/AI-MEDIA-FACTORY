import sys, json, requests
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.content_orm import ContentORM

print("=" * 70)
print("DIAGNOSTICS: MangaDex API coverage")
print("=" * 70)

db = SessionLocal()
items = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.asset_id == None
).all()

by_id = {}
for it in items:
    meta = json.loads(it.source_text)
    mid = meta.get("manga_title_id")
    if mid:
        by_id.setdefault(mid, []).append(it)

print(f"Total items without covers: {len(items)}")
print(f"Unique manga IDs: {len(by_id)}")

# Sample 5 IDs and test individually
UA = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
sample_ids = list(by_id.keys())[:5]

print(f"\nTesting {len(sample_ids)} manga IDs individually:")
for mid in sample_ids:
    try:
        r = requests.get(f"https://api.mangadex.org/manga/{mid}",
                        params=[("includes[]", "cover_art")],
                        headers=UA, timeout=10)
        if r.status_code == 200:
            data = r.json().get("data", {})
            attrs = data.get("attributes", {})
            desc_obj = attrs.get("description", {}) or {}
            desc = desc_obj.get("ru") or desc_obj.get("en") or "NO DESC"
            cover_file = None
            for rel in data.get("relationships", []) or []:
                if rel.get("type") == "cover_art":
                    cover_file = (rel.get("attributes") or {}).get("fileName")
            content_rating = attrs.get("contentRating", "?")
            print(f"  ✅ {mid[:12]}... rating={content_rating}, desc={desc[:40]}, cover={'YES' if cover_file else 'NO'}")
        else:
            print(f"  ❌ {mid[:12]}... status={r.status_code}")
    except Exception as e:
        print(f"  ❌ {mid[:12]}... error={type(e).__name__}")

db.close()
print("=" * 70)