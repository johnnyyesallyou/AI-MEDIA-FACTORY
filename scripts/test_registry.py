import sys
sys.path.insert(0, "/app")

from engines.source_adapters.manga_registry import MangaRegistry

print("=" * 70)
print("TEST: MangaRegistry (all sources)")
print("=" * 70)

print(f"\nAvailable sources: {MangaRegistry.available_sources()}")

print("\n[1] Fetch from remanga only:")
remanga_items = MangaRegistry.fetch_from("remanga", limit=3)
print(f"  Fetched: {len(remanga_items)}")

print("\n[2] Fetch from mangadex only:")
mangadex_items = MangaRegistry.fetch_from("mangadex", limit=3)
print(f"  Fetched: {len(mangadex_items)}")

print("\n[3] Fetch from ALL sources:")
all_items = MangaRegistry.fetch_all(limit=5)
print(f"  Total fetched: {len(all_items)}")

# Подсчёт по источникам
from collections import Counter
sources_count = Counter(item.source for item in all_items)
print(f"  Breakdown: {dict(sources_count)}")

# Показываем первые 5
print("\n  First 5 items:")
for i, item in enumerate(all_items[:5], 1):
    print(f"    [{i}] [{item.source}] {item.title[:50]} — ch.{item.chapter}")

print("\n✅ Registry works!")
print("=" * 70)