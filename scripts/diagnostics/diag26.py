import sys
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.manga_knowledge import MangaTitle

db = SessionLocal()

print("=" * 70)
print("DIAGNOSTICS: external_ids + sources_data")
print("=" * 70)

titles = db.query(MangaTitle).all()
for t in titles:
    ext = t.external_ids or {}
    src = t.sources_data or {}
    has_desc = "✓" if t.description else "✗"
    slug = t.title_slug or "(no slug)"
    print(f"\n[{has_desc}] {t.canonical_title[:50]}")
    print(f"    slug: {slug}")
    print(f"    external_ids: {ext}")
    print(f"    sources_data keys: {list(src.keys()) if src else '(empty)'}")
    print(f"    cover: {(t.cover_url or 'None')[:50]}")

print("\n" + "=" * 70)
db.close()