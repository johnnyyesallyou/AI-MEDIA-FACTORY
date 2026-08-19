import requests

print("=" * 70)
print("PROBE: Anime APIs")
print("=" * 70)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

# 1. AniList GraphQL (публичный, без OAuth)
print("\n[1] AniList GraphQL API")
try:
    query = """
    query {
      Page(page: 1, perPage: 5) {
        media(type: ANIME, sort: TRENDING_DESC) {
          id
          title {
            romaji
            english
            native
          }
          episodes
          status
          genres
          coverImage {
            large
          }
        }
      }
    }
    """
    r = requests.post(
        "https://graphql.anilist.co",
        json={"query": query},
        headers=HEADERS,
        timeout=15,
    )
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        media_list = data.get("data", {}).get("Page", {}).get("media", [])
        print(f"  ✅ Fetched {len(media_list)} anime")
        for anime in media_list[:2]:
            title = anime.get("title", {}).get("romaji") or anime.get("title", {}).get("english")
            print(f"    - {title} ({anime.get('episodes')} episodes)")
    else:
        print(f"  ❌ Failed: {r.text[:200]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# 2. Kitsu API (JSON:API)
print("\n[2] Kitsu API")
try:
    r = requests.get(
        "https://kitsu.io/api/edge/anime",
        params={"filter[text]": "attack on titan", "page[limit]": 3},
        headers=HEADERS,
        timeout=15,
    )
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        anime_list = data.get("data", [])
        print(f"  ✅ Fetched {len(anime_list)} anime")
        for anime in anime_list[:2]:
            attrs = anime.get("attributes", {})
            title = attrs.get("canonicalTitle") or attrs.get("titles", {}).get("en")
            print(f"    - {title} ({attrs.get('episodeCount')} episodes)")
    else:
        print(f"  ❌ Failed: {r.text[:200]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# 3. MyAnimeList (проверяем доступность)
print("\n[3] MyAnimeList API")
try:
    r = requests.get("https://api.myanimelist.net/v2/anime", headers=HEADERS, timeout=10)
    print(f"  Status: {r.status_code}")
    if r.status_code == 401:
        print("  ⚠️ Requires OAuth (client_id needed)")
    elif r.status_code == 200:
        print("  ✅ Public access")
    else:
        print(f"  ❌ Failed: {r.text[:200]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# 4. Anime News Network RSS
print("\n[4] Anime News Network RSS")
try:
    r = requests.get("https://www.animenewsnetwork.com/news/rss.xml", timeout=10)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200 and "xml" in r.headers.get("content-type", ""):
        print(f"  ✅ RSS feed available ({len(r.text)} bytes)")
    else:
        print(f"  ❌ Not RSS: {r.headers.get('content-type')}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 70)