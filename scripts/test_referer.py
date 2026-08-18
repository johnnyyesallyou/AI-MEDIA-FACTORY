import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://remanga.org/",
}

test_url = "https://img.reimg.org/images/155919/6001076eb9b32a609fbc206a37b321c1/57245b716670e5f0e8e0e8e0e8e0e8e0.jpeg"

print("=" * 70)
print("TEST: Page download with Referer")
print("=" * 70)

print(f"\nURL: {test_url[:80]}...")
print(f"Referer: {HEADERS['Referer']}")

r = requests.get(test_url, headers=HEADERS, timeout=15)

print(f"\nStatus: {r.status_code}")
print(f"Content-Type: {r.headers.get('content-type', '')}")
print(f"Size: {len(r.content)} bytes")

if r.status_code == 200 and len(r.content) > 1000:
    print("\n? Page accessible with Referer!")
    
    # ????????? ??? ????????
    with open("/tmp/test_page.jpeg", "wb") as f:
        f.write(r.content)
    print("  Saved to /tmp/test_page.jpeg")
else:
    print("\n? Still blocked")
    print(f"Response: {r.text[:200]}")

print("\n" + "=" * 70)
