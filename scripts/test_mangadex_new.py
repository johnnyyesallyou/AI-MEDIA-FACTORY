import sys
sys.path.insert(0, "/app")

from engines.source_adapters.mangadex_adapter import MangaDexAdapter

print("=" * 70)
print("TEST: MangaDexAdapter.fetch_latest_chapters_manga()")
print("=" * 70)

adapter = MangaDexAdapter()
items = adapter.fetch_latest_chapters_manga(limit=3)

print(f"\nFetched {len(items)} MangaItems")

for i, item in enumerate(items, 1):
    print(f"\n[{i}] {item.title} — глава {item.chapter}")
    print(f"    source: {item.source}")
    print(f"    language: {item.language}")
    print(f"    url: {item.url[:70] if item.url else 'None'}")
    print(f"    cover_url: {(item.cover_url or 'None')[:70]}")
    print(f"    title_slug: {item.title_slug}")

print("\n✅ New interface works!")
print("=" * 70)