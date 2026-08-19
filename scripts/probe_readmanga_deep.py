import requests
from bs4 import BeautifulSoup

print("=" * 70)
print("PROBE: ReadManga (deep)")
print("=" * 70)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru,en;q=0.9",
}

domains = [
    "readmanga.live",
    "readmanga.io",
    "readmanga.today",
    "readmanga.me",
    "mangalib.me",
    "mintmanga.live",
    "mintmanga.com",
]

print("\n[1] Domain availability")
for domain in domains:
    try:
        r = requests.get(f"https://{domain}/", headers=HEADERS, timeout=15, allow_redirects=True)
        print(f"  ✅ {domain}: status={r.status_code}, size={len(r.text)}")
        if r.status_code == 200:
            # Проверяем структуру
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("title")
            if title:
                print(f"      Title: {title.get_text(strip=True)[:60]}")
            # Ищем блоки обновлений
            updates = soup.find_all(class_=lambda c: c and ("update" in c.lower() or "latest" in c.lower() or "new" in c.lower()))
            print(f"      Update blocks: {len(updates)}")
            break
    except Exception as e:
        print(f"  ❌ {domain}: {type(e).__name__}")

print("\n[2] RSS feeds")
rss_urls = [
    "https://readmanga.live/rss",
    "https://readmanga.live/rss.xml",
    "https://mangalib.me/rss",
    "https://mintmanga.live/rss",
]
for url in rss_urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200 and ("xml" in r.headers.get("content-type", "") or "<?xml" in r.text[:100]):
            print(f"  ✅ {url}: {r.status_code}")
            print(f"      First 300 chars: {r.text[:300]}")
        else:
            print(f"  ❌ {url}: {r.status_code} ({r.headers.get('content-type','')})")
    except Exception as e:
        print(f"  ❌ {url}: {type(e).__name__}")

print("\n[3] API endpoints")
api_urls = [
    "https://readmanga.live/api/updates",
    "https://readmanga.live/api/latest",
    "https://readmanga.live/site/index",
    "https://mintmanga.live/site/index",
]
for url in api_urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            print(f"  ✅ {url}: {r.status_code}, size={len(r.text)}")
        else:
            print(f"  ❌ {url}: {r.status_code}")
    except Exception as e:
        print(f"  ❌ {url}: {type(e).__name__}")

print("\n" + "=" * 70)