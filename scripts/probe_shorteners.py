import requests
import urllib.parse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

print("=" * 70)
print("URL SHORTENER PROBE")
print("=" * 70)

# ???????? URL ? ??????????? ?????????
test_url = "https://remanga.org/manga/<29.04.2026>red-storm-2--the-return-of-the-king/1972903"

shorteners = [
    ("clck.ru", f"https://clck.ru/up?site={urllib.parse.quote(test_url, safe='')}"),
    ("tinyurl.com", f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(test_url, safe='')}"),
    ("is.gd", f"https://is.gd/create.php?format=simple&url={urllib.parse.quote(test_url, safe='')}"),
]

for name, url in shorteners:
    print(f"\n[{name}]")
    print(f"  GET: {url[:80]}...")
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=False)
        print(f"  Status: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('content-type', '')[:40]}")
        
        if r.status_code == 200:
            short_url = r.text.strip()
            print(f"  Short URL: {short_url}")
            print(f"  Length: {len(test_url)} -> {len(short_url)} chars")
            
            # ????????? ??? ???????? ?????? ????????
            if short_url.startswith("http"):
                try:
                    r2 = requests.get(short_url, headers=HEADERS, timeout=10, allow_redirects=False)
                    location = r2.headers.get("location", "")
                    print(f"  Redirect: {r2.status_code} -> {location[:60]}...")
                except Exception as e:
                    print(f"  Redirect test failed: {e}")
        else:
            print(f"  Response: {r.text[:200]}")
    
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
