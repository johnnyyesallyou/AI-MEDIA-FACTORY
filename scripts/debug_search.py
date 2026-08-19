import sys
import json
sys.path.insert(0, "/app")

from engines.source_adapters.remanga_adapter import ReMangaAdapter

print("=" * 70)
print("DEBUG: Search для проблемных тайтлов")
print("=" * 70)

adapter = ReMangaAdapter()

test_queries = [
    "Акула",
    "Shark",
    "Красная буря",
    "Красная буря 2",
    "Red Storm",
    "Red Storm 2",
]

for query in test_queries:
    print(f"\n[SEARCH] '{query}':")
    results = adapter.search_title(query, limit=5)
    
    if not results:
        print(f"  ❌ Nothing found")
    else:
        print(f"  ✅ Found {len(results)} results:")
        for r in results[:3]:
            print(f"    - {r['rus_name']} | dir={r['dir']}")

print("\n" + "=" * 70)
