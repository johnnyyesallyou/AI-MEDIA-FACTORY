import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

slug = "descendants-of-the-hero"

print("=" * 70)
print("DEBUG: ReManga API raw responses")
print("=" * 70)

# 1. title info ??? referer
r = requests.get(f"https://remanga.org/api/titles/{slug}/", headers=HEADERS, timeout=15)
print(f"\n[1] /api/titles/{slug}/ (no referer)")
print(f"  Status: {r.status_code}")
print(f"  Raw: {r.text[:400]}")

# 2. title info ? referer
h2 = dict(HEADERS)
h2["Referer"] = f"https://remanga.org/manga/{slug}/"
r2 = requests.get(f"https://remanga.org/api/titles/{slug}/", headers=h2, timeout=15)
print(f"\n[2] /api/titles/{slug}/ (with referer)")
print(f"  Status: {r2.status_code}")
print(f"  Raw: {r2.text[:400]}")

# 3. last-chapters raw
r3 = requests.get("https://remanga.org/api/titles/last-chapters/", headers=HEADERS, timeout=15)
print(f"\n[3] /api/titles/last-chapters/")
print(f"  Status: {r3.status_code}")
print(f"  Raw: {r3.text[:400]}")

# 4. ??????? HTML ???????? ?????? (????? ???? SSR ? JSON)
r4 = requests.get(f"https://remanga.org/manga/{slug}/", headers=HEADERS, timeout=15)
print(f"\n[4] HTML /manga/{slug}/")
print(f"  Status: {r4.status_code}")
print(f"  Has __NEXT_DATA__: {'__NEXT_DATA__' in r4.text}")
print(f"  Has window.__data: {'__data' in r4.text}")

# ???? JSON ? HTML
import re
m = re.search(r'chapters["\']?\s*[:=]', r4.text)
print(f"  Has 'chapters' in HTML: {bool(m)}")

print("\n" + "=" * 70)
