import sys
import json
import re
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from engines.source_adapters.remanga_adapter import ReMangaAdapter

print("=" * 70)
print("ENRICHING MANGA ITEMS (FIXED: use sanitized slug)")
print("=" * 70)

def sanitize_slug(slug: str) -> str:
    """Удаляет артефакты типа <29.04.2026> из slug."""
    if not slug:
        return ""
    # Удаляем <...>
    return re.sub(r'<[^>]+>', '', slug)

adapter = ReMangaAdapter()
db = SessionLocal()

try:
    items = db.query(ContentORM).filter(
        ContentORM.status.in_(["research", "published"]),
        ContentORM.source_url.like("%remanga.org%")
    ).all()
    
    print(f"\nFound {len(items)} manga items")
    
    enriched_count = 0
    failed_count = 0
    skipped_count = 0
    cache = {}
    
    for item in items:
        try:
            if not item.source_text:
                skipped_count += 1
                continue
            
            metadata = json.loads(item.source_text)
            
            # Проверяем, уже ли обогащён
            if metadata.get("manga_description"):
                skipped_count += 1
                continue
            
            # Извлекаем slug из source_url или title_url
            source_url = metadata.get("manga_title_url") or item.source_url
            if not source_url:
                failed_count += 1
                continue
            
            # Парсим slug из URL: https://remanga.org/manga/{slug}
            match = re.search(r'/manga/([^/]+)', source_url)
            if not match:
                failed_count += 1
                continue
            
            raw_slug = match.group(1)
            slug = sanitize_slug(raw_slug)
            
            if not slug:
                failed_count += 1
                continue
            
            # Получаем title info (кэш)
            if slug not in cache:
                info = adapter.get_title_info(slug)
                cache[slug] = info
            else:
                info = cache[slug]
            
            if not info:
                failed_count += 1
                continue
            
            # Обогащаем metadata
            metadata["manga_description"] = info.get("description", "")
            metadata["manga_genres"] = info.get("genres", [])
            metadata["manga_type"] = info.get("type", "")
            metadata["manga_status"] = info.get("status", "")
            metadata["manga_total_chapters"] = info.get("count_chapters", 0)
            
            item.source_text = json.dumps(metadata, ensure_ascii=False)
            enriched_count += 1
            
            genres_preview = info.get("genres", [])[:3]
            print(f"  ✅ {metadata.get('manga_title_name', item.headline)[:40]}")
            print(f"     Type: {info.get('type')}, Genres: {genres_preview}")
        
        except Exception as e:
            failed_count += 1
            print(f"  ❌ Error: {e}")
    
    db.commit()
    
    print("\n" + "=" * 70)
    print(f"RESULT:")
    print(f"  Enriched: {enriched_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Unique slugs cached: {len(cache)}")
    print("=" * 70)

finally:
    db.close()
