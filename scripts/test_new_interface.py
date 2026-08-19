import sys
sys.path.insert(0, "/app")

from engines.source_adapters.remanga_adapter import ReMangaAdapter

print("=" * 70)
print("TEST: ReMangaAdapter.fetch_latest_chapters_manga()")
print("=" * 70)

adapter = ReMangaAdapter()
items = adapter.fetch_latest_chapters_manga(limit=3)

print(f"\nFetched {len(items)} MangaItems")

for i, item in enumerate(items, 1):
    print(f"\n[{i}] {item.title} — глава {item.chapter}")
    print(f"    source: {item.source}")
    print(f"    language: {item.language}")
    print(f"    url: {item.url[:60]}")
    print(f"    cover_url: {item.cover_url[:60] if item.cover_url else 'None'}")
    print(f"    title_slug: {item.title_slug}")

print("\n✅ New interface works!")
print("=" * 70)