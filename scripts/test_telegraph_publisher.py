import sys
import json
sys.path.insert(0, "/app")

from engines.telegraph.publisher import TelegraphPublisher
from core.database import SessionLocal
from core.models.content_orm import ContentORM

print("=" * 70)
print("TESTING TelegraphPublisher")
print("=" * 70)

# Инициализация
publisher = TelegraphPublisher()

# Проверяем access_token
if not publisher.access_token:
    print("\nCreating new Telegraph account...")
    token = publisher.create_account(
        short_name="AI-Media-Factory",
        author_name="AI Media Factory",
        author_url="https://github.com/yourusername/ai-media-factory"
    )
    print(f"✅ Token: {token[:20]}...")
    
    # Сохраняем токен в .env для будущего использования
    print(f"\n⚠️ Add to .env: TELEGRAPH_ACCESS_TOKEN={token}")
else:
    print(f"\nUsing existing token: {publisher.access_token[:20]}...")

# Берём последний опубликованный манга-пост
db = SessionLocal()
item = db.query(ContentORM).filter(
    ContentORM.status == "published",
    ContentORM.source_url.like("%remanga.org%")
).order_by(ContentORM.published_at.desc()).first()

if not item:
    print("ERROR: No published manga items found")
    sys.exit(1)

print(f"\nTest item: {item.headline}")
print(f"Source URL: {item.source_url}")

# Парсим metadata
metadata = json.loads(item.source_text) if item.source_text else {}
description = metadata.get("manga_description", "No description available")
cover_url = metadata.get("manga_cover_url")
chapter_url = metadata.get("manga_chapter_url", item.source_url)

print(f"Description: {description[:100]}...")
print(f"Cover URL: {cover_url}")
print(f"Chapter URL: {chapter_url}")

# Создаём Telegraph страницу
print("\n" + "="*70)
print("Creating Telegraph page...")
print("="*70)

try:
    result = publisher.publish_manga_page(
        title=item.headline,
        description=description,
        cover_url=cover_url,
        source_url=item.source_url,
        chapter_url=chapter_url
    )
    
    print("\n✅ SUCCESS!")
    print(f"  URL: {result['url']}")
    print(f"  Path: {result['path']}")
    print(f"  Title: {result['title']}")
    
    print("\n" + "="*70)
    print("TEST PASSED")
    print(f"Open in browser: {result['url']}")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    db.close()
