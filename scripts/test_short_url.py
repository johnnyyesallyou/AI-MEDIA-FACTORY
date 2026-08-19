import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from backend.automation.jobs.manga_publish_job import MangaPublishJob

print("=" * 70)
print("TEST: Publishing with SHORT URL")
print("=" * 70)

# Создаём тестовый item вручную
db = SessionLocal()
from engines.source_adapters.remanga_adapter import ReMangaAdapter

adapter = ReMangaAdapter()
items = adapter.fetch_latest_chapters(limit=1)

if not items:
    print("No chapters fetched!")
    sys.exit(1)

item = items[0]
print(f"\nTest manga: {item.title_name}")
print(f"Chapter: {item.chapter_number}")
print(f"Original URL: {item.chapter_url}")
print(f"URL length: {len(item.chapter_url)}")

# Укорачиваем
from engines.url_shortener import URLShortener
shortener = URLShortener()
short_url = shortener.shorten(item.chapter_url)

print(f"\nShort URL: {short_url}")
print(f"Short URL length: {len(short_url)}")
print(f"Chars saved: {len(item.chapter_url) - len(short_url)}")

# Проверяем что short URL работает
import requests
print(f"\nTesting short URL redirect...")
r = requests.get(short_url, timeout=10, allow_redirects=False)
location = r.headers.get("location", "")
print(f"  Status: {r.status_code}")
print(f"  Location: {location[:80]}...")

if r.status_code in [301, 302] and "remanga.org" in location:
    print("\n✅ Short URL works correctly!")
else:
    print("\n❌ Short URL redirect issue")

db.close()

print("\n" + "=" * 70)
print("Short URL test completed")
print("=" * 70)
