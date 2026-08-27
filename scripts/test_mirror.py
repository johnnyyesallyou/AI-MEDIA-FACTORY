import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Реальные URL из шага 51.94
test_urls = [
    "https://img.reimg.org/images/157218/ddd4c8397c75cfe61c2dbcd07c580929/ad7db87fa8155677e344499f9059542b.webp",
    "https://img.reimg.org/images/157218/ddd4c8397c75cfe61c2dbcd07c580929/d3228d160c14117291ec610c7935cf51.webp",
]

for url in test_urls:
    try:
        r = requests.get(url, headers=UA, timeout=10, stream=True)
        print(f"URL: {url[:80]}...")
        print(f"  Status: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('content-type')}")
        print(f"  Content-Length: {r.headers.get('content-length')}")
        print(f"  Is image: {'image' in r.headers.get('content-type', '')}")
        print()
        r.close()
    except Exception as e:
        print(f"  Error: {e}")
        print()