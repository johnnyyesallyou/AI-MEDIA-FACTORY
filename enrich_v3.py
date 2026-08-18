import sys
import json
import re
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from engines.source_adapters.remanga_adapter import ReMangaAdapter

print("=" * 70)
print("ENRICHING v3: search fallback + URL fix")
print("=" * 70)

def sanitize_slug(slug: str) -> str:
    return re.sub(r'<[^>]+>', '', slug) if slug else ""

adapter = ReMangaAdapter()
db = SessionLocal()

try:
    items = db.query(ContentORM).filter(
        ContentORM.source_url.like("%remanga.org%")
    ).all()
    
    print(f"\nFound {len(items)} manga items")
    
    enriched = 0
    fixed_urls = 0
    failed = 0
    cache = {}
    
    for item in items:
        try:
            if not item.source_text:
                continue
            
            metadata = json.loads(item.source_text)
            title_name = metadata.get("manga_title_name", "")
            title_id = metadata.get("manga_title_id", "")
            
            # Получаем реальный slug (из кэша или через поиск)
            cache_key = title_id or title_name
            if cache_key in cache:
                real_slug, info = cache[cache_key]
            else:
                # Сначала пробуем sanitized slug
                source_url = metadata.get("manga_title_url") or item.source_url
                match = re.search(r'/manga/([^/]+)', source_url or "")
                raw_slug = match.group(1) if match else ""
                slug = sanitize_slug(raw_slug)
                
                info = adapter.get_title_info(slug) if slug else None
                
                # Fallback: поиск по названию
                if not info and title_name:
                    real = adapter.find_title_slug(title_name, title_id)
                    if real:
                        slug = real
                        info = adapter.get_title_info(real)
                    else:
                        info = None
                else:
                    real_slug_found = slug
                
                if info:
                    real_slug = info_slug = slug
                else:
                    real_slug = None
                
                cache[cache_key] = (real_slug, info)
            
            if not info:
                failed += 1
                print(f"  ❌ {title_name[:40]} - not found")
                continue
            
            # Обогащаем metadata
            metadata["manga_description"] = info.get("description", "")
            metadata["manga_genres"] = info.get("genres", [])
            metadata["manga_type"] = info.get("type", "")
            metadata["manga_status"] = info.get("status", "")
            metadata["manga_total_chapters"] = info.get("count_chapters", 0)
            
            # Исправляем URL если был битый
            if real_slug:
                metadata["manga_title_slug"] = real_slug
                metadata["manga_title_url"] = f"https://remanga.org/manga/{real_slug}"
                
                chapter_id = metadata.get("manga_chapter_id", "")
                if chapter_id:
                    metadata["manga_chapter_url"] = f"https://remanga.org/manga/{real_slug}/{chapter_id}"
                    fixed_urls += 1
            
            item.source_text = json.dumps(metadata, ensure_ascii=False)
            enriched += 1
            
            print(f"  ✅ {title_name[:40]} | slug={real_slug} | {len(info.get('genres', []))} genres")
        
        except Exception as e:
            failed += 1
            print(f"  ❌ Error: {e}")
    
    db.commit()
    
    print("\n" + "=" * 70)
    print(f"RESULT: enriched={enriched}, fixed_urls={fixed_urls}, failed={failed}")
    print("=" * 70)

finally:
    db.close()
