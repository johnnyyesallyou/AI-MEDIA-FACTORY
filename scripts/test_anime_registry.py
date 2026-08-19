import sys
sys.path.insert(0, "/app")

from engines.source_adapters.anime_registry import AnimeRegistry

print("=" * 70)
print("TEST: AnimeRegistry")
print("=" * 70)

print(f"\nAvailable sources: {AnimeRegistry.available_sources()}")

print("\n[1] Fetch trending:")
trending = AnimeRegistry.fetch_trending(limit=5)
print(f"  Fetched: {len(trending)}")
for i, anime in enumerate(trending[:2], 1):
    print(f"  [{i}] {anime.title} ({anime.status})")

print("\n[2] Fetch currently airing:")
airing = AnimeRegistry.fetch_currently_airing(limit=5)
print(f"  Fetched: {len(airing)}")
for i, anime in enumerate(airing[:2], 1):
    print(f"  [{i}] {anime.title} ({anime.season} {anime.season_year})")

print("\n" + "=" * 70)