import sys
sys.path.insert(0, "/app")

from engines.source_adapters.manga_registry import MangaRegistry

print("=" * 70)
print("TEST: MangaRegistry (3 sources)")
print("=" * 70)

print(f"Available sources: {MangaRegistry.available_sources()}")

print("\n[1] Fetch from readmanga:")
rm_items = MangaRegistry.fetch_from("readmanga", limit=5)
print(f"  Fetched: {len(rm_items)}")

print("\n[2] Fetch from ALL sources:")
all_items = MangaRegistry.fetch_all(limit=5)
print(f"  Total: {len(all_items)}")

# Breakdown
from collections import Counter
breakdown = Counter(item.source for item in all_items)
print(f"  Breakdown: {dict(breakdown)}")

print("\n[3] Deduplication:")
dedup = MangaRegistry.fetch_with_dedup(limit=5)
print(f"  After dedup: {len(dedup)} items")

# Первые 5
print("\n[4] First 5 from all sources:")
for i, item in enumerate(all_items[:5], 1):
    print(f"  [{i}] [{item.source}] {item.title[:50]} — ch.{item.chapter}")

print("=" * 70)