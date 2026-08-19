import requests

sources = {
    "ReManga": "https://remanga.org/api/titles/?ordering=-id&count=1",
    "MangaDex": "https://api.mangadex.org/manga?limit=1",
    "AniList": ("POST", "https://graphql.anilist.co", {"query": "{ Media(type: ANIME) { id } }"}),
    "Habr": "https://habr.com/ru/rss/articles/?fl=ru",
    "ReadManga": "https://readmanga.io",
}

print("SOURCE CONNECTIVITY TEST (from container)")
print("=" * 70)

for name, url in sources.items():
    print(f"\n[{name}]")
    try:
        if isinstance(url, tuple):
            method, endpoint, payload = url
            if method == "POST":
                r = requests.post(endpoint, json=payload, timeout=5)
        else:
            r = requests.get(url, timeout=5)
        
        print(f"  Status: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('content-type', 'N/A')}")
        print(f"  Length: {len(r.content)} bytes")
        
        if r.status_code in (200, 301, 302):
            print(f"  ✓ Accessible")
        else:
            print(f"  ✗ Unexpected status")
            
    except Exception as e:
        print(f"  ✗ {type(e).__name__}: {e}")

print("\n" + "=" * 70)