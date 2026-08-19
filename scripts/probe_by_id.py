import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ru,en;q=0.9",
}

print("=" * 70)
print("ReManga API: get title by NUMERIC ID")
print("=" * 70)

test_ids = ["14813", "45102", "155919"]

for tid in test_ids:
    url = f"https://api.remanga.org/api/titles/{tid}/"
    print(f"\n[GET] {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            content = data.get("content", {})
            print(f"  Title: {content.get('rus_name')} ({content.get('dir')})")
            print(f"  Description: {content.get('description', '')[:100]}...")
            print(f"  Genres: {content.get('genres', [])[:5]}")
        else:
            print(f"  Response: {r.text[:150]}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 70)
