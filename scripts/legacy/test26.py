import sys, json
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.manga_knowledge import MangaTitle
from backend.automation.jobs.manga_enrichment_job import MangaEnrichmentJob

print("=" * 70)
print("TEST: Cross-source Enrichment")
print("=" * 70)

db = SessionLocal()
before = db.query(MangaTitle).filter(
    (MangaTitle.description == None) | (MangaTitle.description == "")
).count()
total = db.query(MangaTitle).count()
print(f"\nBefore: {before}/{total} titles without description")
db.close()

job = MangaEnrichmentJob()
result = job.run(limit=20)
print(f"\nJob result: {result}")

db = SessionLocal()
after = db.query(MangaTitle).filter(
    (MangaTitle.description == None) | (MangaTitle.description == "")
).count()
with_sources = db.query(MangaTitle).filter(
    MangaTitle.sources_data != None,
    MangaTitle.sources_data != {},
).count()
print(f"After: {after}/{total} without description")
print(f"Titles with sources_data: {with_sources}")

# Пример объединённого тайтла
t = db.query(MangaTitle).filter(MangaTitle.sources_data != {}).first()
if t:
    print(f"\nExample: {t.canonical_title}")
    print(f"  sources: {list((t.sources_data or {}).keys())}")
    print(f"  description: {(t.description or '')[:80]}...")
    print(f"  genres: {(t.genres or [])[:6]}")
db.close()
print("=" * 70)