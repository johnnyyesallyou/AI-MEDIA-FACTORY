import sys
sys.path.insert(0, "/app")

from engines.source_adapters.anilist_adapter import AniListAdapter

print("=" * 70)
print("TEST: AniListAdapter")
print("=" * 70)

adapter = AniListAdapter()

print("\n[1] Trending anime:")
trending = adapter.fetch_trending_anime(limit=5)
print(f"  Fetched: {len(trending)}")
for i, anime in enumerate(trending[:3], 1):
    print(f"  [{i}] {anime.title}")
    print(f"      English: {anime.title_english}")
    print(f"      Episodes: {anime.episodes}")
    print(f"      Status: {anime.status}")
    print(f"      Genres: {anime.genres[:3]}")
    print(f"      Cover: {(anime.cover_url or 'None')[:70]}")

print("\n[2] Currently airing:")
airing = adapter.fetch_currently_airing(limit=5)
print(f"  Fetched: {len(airing)}")
for i, anime in enumerate(airing[:2], 1):
    print(f"  [{i}] {anime.title} ({anime.season} {anime.season_year})")

print("\n" + "=" * 70)