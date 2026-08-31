import sys
sys.path.insert(0, '/app')

from engines.cross_source_enricher import CrossSourceEnricher
from core.database import SessionLocal
from core.models.manga_knowledge import MangaTitle

db = SessionLocal()
title = db.query(MangaTitle).first()

enricher = CrossSourceEnricher()
sources_data = enricher._build_sources_data(title)

print(f"Title: {title.canonical_title[:50]}")
print(f"\nSources data keys: {list(sources_data.keys())}")

for source, data in sources_data.items():
    print(f"\n{source}:")
    print(f"  description: {data.get('description', 'MISSING')[:100] if data.get('description') else 'MISSING'}")
    print(f"  genres: {data.get('genres', 'MISSING')[:5] if data.get('genres') else 'MISSING'}")
    print(f"  cover: {data.get('cover', 'MISSING')[:60] if data.get('cover') else 'MISSING'}")

db.close()