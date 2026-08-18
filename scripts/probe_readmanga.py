import requests

print("=" * 70)
print("PROBE: ReadManga API")
print("=" * 70)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# 1. Главная страница с последними главами
print("\n[1] Main page (last updates)")
try:
    r = requests.get("https://readmanga.io/", headers=HEADERS, timeout=15, allow_redirects=True)
    print(f"  Status: {r.status_code}")
    print(f"  URL: {r.url[:80]}")
    print(f"  Size: {len(r.text)} bytes")
    
    # Ищем главы в HTML
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Ищем ссылки на главы
    chapter_links = soup.find_all("a", href=True)
    manga_links = [a for a in chapter_links if "/manga/" in a.get("href", "")]
    print(f"  Manga links found: {len(manga_links)}")
    
    if manga_links:
        print("\n  First 3 links:")
        for a in manga_links[:3]:
            href = a.get("href")
            text = a.get_text(strip=True)[:50]
            print(f"    {href} -> {text}")
    
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

# 2. RSS если есть
print("\n[2] RSS feed")
for rss_url in ["https://readmanga.io/rss", "https://readmanga.io/rss.xml"]:
    try:
        r = requests.get(rss_url, headers=HEADERS, timeout=10)
        print(f"  {rss_url}: status={r.status_code}")
        if r.status_code == 200 and len(r.text) > 100:
            print(f"    Size: {len(r.text)}")
            print(f"    First 200 chars: {r.text[:200]}")
            break
    except Exception as e:
        print(f"  {rss_url}: {type(e).__name__}")

print("\n" + "=" * 70)