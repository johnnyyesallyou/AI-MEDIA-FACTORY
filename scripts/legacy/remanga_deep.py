import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ru,en;q=0.9",
}

print("=" * 70)
print("ReManga API: DETAILED JSON ANALYSIS")
print("=" * 70)

r = requests.get("https://api.remanga.org/api/titles/last-chapters/", headers=HEADERS, timeout=20)
data = r.json()

print(f"\nTotal items: {len(data.get('content', []))}")
print(f"Keys in response: {list(data.keys())}")

# ????????? ?????? ??????? ????????
if data.get('content'):
    first = data['content'][0]
    print(f"\n=== FIRST ITEM ===")
    print(f"Keys: {list(first.keys())}")
    print(f"\nAll fields:")
    for k, v in first.items():
        if isinstance(v, (dict, list)):
            print(f"  {k}: ({type(v).__name__}) {str(v)[:200]}")
        else:
            print(f"  {k}: {v}")

# ???? URL ???????
print(f"\n=== ????? ??????? ===")
first = data['content'][0]
for k, v in first.items():
    if 'img' in k.lower() or 'cover' in k.lower() or 'image' in k.lower():
        print(f"  {k}: {v}")

# ??????? ????????? chapters
print(f"\n=== ????????? CHAPTERS ===")
for k, v in first.items():
    if 'chapter' in k.lower():
        print(f"  {k}: {type(v).__name__}")
        if isinstance(v, list) and v:
            print(f"    First chapter keys: {list(v[0].keys()) if isinstance(v[0], dict) else v[0]}")
            print(f"    First chapter: {json.dumps(v[0], ensure_ascii=False)[:300]}")
        elif isinstance(v, dict):
            print(f"    Keys: {list(v.keys())}")

print("\n" + "=" * 70)
