import requests
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ru,en;q=0.9",
}

print("=" * 70)
print("REVERSE-ENGINEERING ReManga API")
print("=" * 70)

# 1. ???? API endpoints ? HTML ??????? ????????
print("\n[1] ??????????? HTML ??????? ???????? ReManga...")
r = requests.get("https://remanga.org/", headers=HEADERS, timeout=20)
html = r.text

# ???? URL-???????? API
api_patterns = re.findall(r'https?://[^"\'\s]+/api/[^"\'\s]+', html)
unique_api = list(set(api_patterns))[:20]
print(f"  ??????? {len(unique_api)} ?????????? API URL:")
for url in unique_api[:10]:
    print(f"    - {url}")

# ???? JSON ? HTML (embedded data)
json_blocks = re.findall(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', html, re.DOTALL)
if json_blocks:
    print(f"\n  ??????? {len(json_blocks)} ?????? __INITIAL_STATE__")
    print(f"  ?????? ??????? ?????: {len(json_blocks[0])} ????????")
    print(f"  ??????: {json_blocks[0][:300]}...")

# 2. ????????? ?????????? API endpoints
print("\n[2] ??????? ?????????? API endpoints...")
test_endpoints = [
    "https://api.remanga.org/api/titles/last-chapters/",
    "https://api.remanga.org/api/titles/last-chapters?page=1&count=5",
    "https://api.remanga.org/api/titles/updates/",
    "https://api.remanga.org/api/catalog/latest/",
    "https://remanga.org/api/titles/last-chapters/",
    "https://remanga.org/api/catalog/",
]

for url in test_endpoints:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            print(f"  ? {url}")
            print(f"     Status: {r.status_code}, Size: {len(r.content)} bytes")
            if "application/json" in r.headers.get("content-type", ""):
                print(f"     JSON preview: {r.text[:200]}")
        else:
            print(f"  ? {url} ? {r.status_code}")
    except Exception as e:
        print(f"  ?? {url} ? {type(e).__name__}")

print("\n" + "=" * 70)
