import sys, json, time, requests
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.manga_knowledge import MangaTitle
from engines.source_adapters import ReMangaAdapter

print("=" * 70)
print("ENRICHMENT: MangaTitle (description + genres)")
print("=" * 70)

db = SessionLocal()
titles = db.query(MangaTitle).filter(
    MangaTitle.description == None,
    MangaTitle.title_slug != None,
).limit(20).all()

print(f"Titles to enrich: {len(titles)}")

adapter = ReMangaAdapter()
enriched = 0

for title in titles:
    slug = title.title_slug
    if not slug:
        continue
    
    try:
        info = adapter.get_title_info(slug)
        if info:
            desc = info.get("description", "")
            genres = info.get("genres", [])
            
            if desc or genres:
                title.description = desc
                if genres:
                    title.genres = genres
                enriched += 1
                print(f"  ✅ {title.canonical_title[:40]}")
    except Exception as e:
        print(f"  ❌ {slug}: {e}")
    
    time.sleep(0.3)

db.commit()
print(f"\n✅ Enriched: {enriched} titles")
db.close()
print("=" * 70)