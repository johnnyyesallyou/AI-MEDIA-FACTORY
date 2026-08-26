import sys, logging
sys.path.insert(0, '/app')

logging.basicConfig(level=logging.INFO)

from engines.cross_source_enricher import CrossSourceEnricher
from core.database import SessionLocal
from core.models.manga_knowledge import MangaTitle

db = SessionLocal()

# Берём первый тайтл без description
title = db.query(MangaTitle).filter(
    (MangaTitle.description == None) | (MangaTitle.description == "")
).first()

if not title:
    print("No titles without description")
else:
    print(f"Enriching: {title.canonical_title[:50]}")
    
    enricher = CrossSourceEnricher()
    enricher.enrich(title)
    
    print(f"\nAfter enrichment:")
    print(f"  description: {title.description[:100] if title.description else 'STILL EMPTY'}")
    print(f"  genres: {title.genres[:5] if title.genres else 'EMPTY'}")
    print(f"  cover: {title.cover_url[:60] if title.cover_url else 'EMPTY'}")
    
    db.commit()

db.close()