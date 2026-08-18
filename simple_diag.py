import sys
sys.path.insert(0, "/app")

import requests

print("=" * 70)
print("SIMPLE DIAGNOSTICS: ReManga API")
print("=" * 70)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

# 1. Raw API call
print("\n[1] GET /api/titles/last-chapters/")
try:
    r = requests.get("https://remanga.org/api/titles/last-chapters/", headers=HEADERS, timeout=15)
    print(f"  Status: {r.status_code}")
    
    data = r.json()
    print(f"  Keys: {list(data.keys())}")
    
    # Определяем где лежат главы
    chapters = data.get("content") or data.get("data") or data.get("results") or []
    print(f"  Chapters count: {len(chapters)}")
    
    if chapters:
        first = chapters[0]
        print(f"\n  First chapter keys: {list(first.keys())[:15]}")
        print(f"  rus_name: {first.get('rus_name', 'None')}")
        print(f"  chapter: {first.get('chapter', 'None')}")
        print(f"  chapter_id: {first.get('chapter_id', first.get('id', 'None'))}")
        print(f"  branch: {first.get('branch', first.get('branches', 'None'))}")
    else:
        print(f"  Raw response (first 300 chars): {r.text[:300]}")

except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

print("\n" + "=" * 70)