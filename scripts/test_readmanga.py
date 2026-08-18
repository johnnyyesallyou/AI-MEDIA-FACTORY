import sys
sys.path.insert(0, "/app")

from engines.source_adapters.readmanga_adapter import ReadMangaAdapter

print("=" * 70)
print("TEST: ReadMangaAdapter")
print("=" * 70)

adapter = ReadMangaAdapter()
items = adapter.fetch_latest_chapters(limit=5)

print(f"\nFetched {len(items)} MangaItems")

for i, item in enumerate(items, 1):
    print(f"\n[{i}] {item.title}")
    print(f"    chapter: {item.chapter}")
    print(f"    slug: {item.title_slug}")
    print(f"    url: {item.url}")
    print(f"    cover: {(item.cover_url or 'None')[:70]}")

print("\n" + "=" * 70)