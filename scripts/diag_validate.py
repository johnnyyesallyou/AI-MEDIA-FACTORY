import sys, requests
sys.path.insert(0, "/app")

from engines.publishing.image_resolver import UA

urls = [
    "https://remanga.org/media/titles/manito/cover_5f0f24f949846f1.webp",
    "https://uploads.mangadex.org/covers/80422e14-b9ad-4fda-970f-de370d5fa4e5/cover.jpg",
]

print("=" * 70)
print("DIAGNOSTICS: direct requests")
print("=" * 70)

for url in urls:
    print(f"\nURL: {url[:70]}...")
    try:
        r = requests.get(url, headers=UA, timeout=15, stream=True)
        print(f"  Status: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('content-type')}")
        print(f"  Content-Length: {r.headers.get('content-length', 'N/A')}")
        r.close()
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("\n[2] With Referer header:")
print("=" * 70)

headers_with_referer = {
    **UA,
    "Referer": "https://remanga.org/",
}

for url in urls:
    print(f"\nURL: {url[:70]}...")
    try:
        r = requests.get(url, headers=headers_with_referer, timeout=15, stream=True)
        print(f"  Status: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('content-type')}")
        r.close()
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")

print("=" * 70)