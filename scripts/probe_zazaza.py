import requests

print("=" * 70)
print("PROBE: ZazaZa")
print("=" * 70)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru,en;q=0.9",
}

# 1. Главная страница
print("\n[1] Main page")
for domain in ["zazazamanga.com", "zazaza.net", "zazaza.ru"]:
    url = f"https://{domain}/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        print(f"  {domain}: status={r.status_code}, url={r.url[:60]}, size={len(r.text)}")
        if r.status_code == 200:
            # Ищем API endpoints
            if "api" in r.text.lower() or "fetch" in r.text.lower() or "axios" in r.text.lower():
                print(f"    → Возможный SPA (есть API/fetch/axios в коде)")
            if "<title>" in r.text:
                import re
                title = re.search(r"<title>(.*?)</title>", r.text)
                if title:
                    print(f"    Title: {title.group(1)}")
            break
    except Exception as e:
        print(f"  {domain}: {type(e).__name__}")

# 2. Проверяем типичные API endpoints
print("\n[2] API endpoints probe")
api_urls = [
    "/api/updates",
    "/api/latest",
    "/api/chapters",
    "/updates",
    "/rss",
    "/feed",
]

for url in api_urls:
    for domain in ["zazazamanga.com", "zazaza.net"]:
        full_url = f"https://{domain}{url}"
        try:
            r = requests.get(full_url, headers=HEADERS, timeout=10)
            if r.status_code in [200, 301, 302]:
                print(f"  {full_url}: status={r.status_code}, size={len(r.text)}")
                if "json" in r.headers.get("content-type", ""):
                    print(f"    → JSON response!")
                    print(f"    First 200 chars: {r.text[:200]}")
        except Exception:
            pass

print("\n" + "=" * 70)