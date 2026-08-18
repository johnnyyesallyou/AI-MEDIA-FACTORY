import sys
import json
sys.path.insert(0, "/app")

from engines.source_adapters import ReMangaAdapter

print("=" * 70)
print("TESTING ReMangaAdapter")
print("=" * 70)

adapter = ReMangaAdapter()

print("\n[1] Testing connection...")
if adapter.test_connection():
    print("  Connection successful")
else:
    print("  Connection failed")
    sys.exit(1)

print("\n[2] Fetching latest chapters (limit=5)...")
try:
    items = adapter.fetch_latest_chapters(limit=5)
    print(f"  Fetched {len(items)} chapters")

    print("\n[3] First 3 chapters:")
    for i, item in enumerate(items[:3], 1):
        print(f"\n--- Chapter {i} ---")
        print(f"  Source: {item.source}")
        print(f"  Title: {item.title_name}")
        print(f"  Title EN: {item.title_name_en}")
        print(f"  Chapter: {item.chapter_number}")
        print(f"  Title URL: {item.title_url}")
        print(f"  Chapter URL: {item.chapter_url}")
        if item.cover_url:
            print(f"  Cover URL: {item.cover_url[:80]}...")
        print(f"  Upload Date: {item.upload_date}")

    print("\n" + "=" * 70)
    print("TEST PASSED")
    print("=" * 70)

except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
