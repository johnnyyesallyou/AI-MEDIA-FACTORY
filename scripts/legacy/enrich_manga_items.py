import sys
import json
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from engines.source_adapters.remanga_adapter import ReMangaAdapter

print("=" * 70)
print("ENRICHING EXISTING MANGA RESEARCH ITEMS")
print("=" * 70)

adapter = ReMangaAdapter()
db = SessionLocal()

try:
    # Get all manga research items
    items = db.query(ContentORM).filter(
        ContentORM.status.in_(["research", "published"]),
        ContentORM.source_url.like("%remanga.org%")
    ).all()
    
    print(f"\nFound {len(items)} manga items to enrich")
    
    enriched_count = 0
    failed_count = 0
    cache = {}  # slug -> title_info
    
    for item in items:
        try:
            # Parse existing metadata
            if not item.source_text:
                continue
            
            metadata = json.loads(item.source_text)
            slug = metadata.get("manga_title_slug")
            if not slug:
                continue
            
            # Check if already enriched
            if metadata.get("manga_description"):
                continue
            
            # Get title info (from cache or API)
            if slug not in cache:
                info = adapter.get_title_info(slug)
                cache[slug] = info
            else:
                info = cache[slug]
            
            if not info:
                failed_count += 1
                continue
            
            # Update metadata
            metadata["manga_description"] = info.get("description", "")
            metadata["manga_genres"] = info.get("genres", [])
            metadata["manga_type"] = info.get("type", "")
            metadata["manga_status"] = info.get("status", "")
            metadata["manga_total_chapters"] = info.get("count_chapters", 0)
            
            # Save back
            item.source_text = json.dumps(metadata, ensure_ascii=False)
            enriched_count += 1
            
            print(f"  ✅ {item.headline[:50]}... ({info.get('type')}, {len(info.get('genres', []))} genres)")
        
        except Exception as e:
            failed_count += 1
            print(f"  ❌ Error for {item.headline[:40]}...: {e}")
    
    db.commit()
    
    print("\n" + "=" * 70)
    print(f"RESULT: enriched {enriched_count}, failed {failed_count}")
    print(f"Cache hits: {len(cache)} unique titles")
    print("=" * 70)

finally:
    db.close()
