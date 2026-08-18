import sys
sys.path.insert(0, "/app")

from engines.source_adapters import MangaDexAdapter

print("=" * 70)
print("TESTING MangaDexAdapter")
print("=" * 70)

adapter = MangaDexAdapter()

print("\n[1] Testing connection...")
if adapter.test_connection():
    print("  Connection successful")
else:
    print("  Connection failed")
    sys.exit(1)

print("\n[2] Fetching latest chapters (limit=10)...")
items = adapter.fetch_latest_chapters(limit=10)
print(f"  Fetched {len(items)} chapters")

print("\n[3] First 5 chapters:")
for i, item in enumerate(items[:5], 1):
    print(f"\n  Chapter {i}:")
    print(f"    Source: {item.source}")
    print(f"    Title: {item.title_name}")
    print(f"    Title EN: {item.title_name_en}")
    print(f"    Chapter: {item.chapter_number}")
    print(f"    Chapter URL: {item.chapter_url}")
    print(f"    Cover: {item.cover_url[:70] if item.cover_url else 'None'}...")
    print(f"    Upload: {item.upload_date}")

print("\n" + "=" * 70)
if len(items) > 0:
    print("TEST PASSED")
else:
    print("TEST FAILED")
print("=" * 70)
