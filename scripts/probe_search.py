import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ru,en;q=0.9",
}

print("=" * 70)
print("ReManga SEARCH API PROBE")
print("=" * 70)

# ??????? ?????? search endpoints
endpoints = [
    ("https://api.remanga.org/api/search/", {"query": "?????"}),
    ("https://api.remanga.org/api/titles/", {"search": "?????"}),
    ("https://api.remanga.org/api/titles/?search=?????", {}),
]

for url, params in endpoints:
    print(f"\n[GET] {url} params={params}")
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            content = data.get("content", [])
            if isinstance(content, list) and content:
                first = content[0]
                print(f"  Found {len(content)} results")
                print(f"  First: {first.get('rus_name')} | dir={first.get('dir')}")
            elif isinstance(content, dict):
                print(f"  Keys: {list(content.keys())[:10]}")
        else:
            print(f"  Response: {r.text[:150]}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 70)
