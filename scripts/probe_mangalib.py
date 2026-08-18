import requests
from bs4 import BeautifulSoup

print("=" * 70)
print("PROBE: MangaLib")
print("=" * 70)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# MangaLib domains
domains = [
    "mangalib.me",
    "mangalib.org",
    "libmanga.com",
]

print("\n[1] Domain availability")
working = None
for domain in domains:
    try:
        r = requests.get(f"https://{domain}/", headers=HEADERS, timeout=15, allow_redirects=True)
        print(f"  {domain}: status={r.status_code}, url={r.url[:60]}, size={len(r.text)}")
        if r.status_code == 200:
            working = domain
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("title")
            if title:
                print(f"    Title: {title.get_text(strip=True)[:60]}")
    except Exception as e:
        print(f"  {domain}: {type(e).__name__}: {str(e)[:50]}")

if working:
    print(f"\n[2] Working domain: {working}")
    
    # Check for updates section
    try:
        r = requests.get(f"https://{working}/updates", headers=HEADERS, timeout=15)
        print(f"  /updates: {r.status_code}, size={len(r.text)}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            # Ищем ссылки на мангу
            links = soup.find_all("a", href=True)
            manga_links = [a for a in links if "/manga/" in a.get("href", "") or "/read/" in a.get("href", "")]
            print(f"    Manga links: {len(manga_links)}")
            if manga_links:
                print(f"    First 3:")
                for a in manga_links[:3]:
                    print(f"      {a.get('href')[:60]} -> {a.get_text(strip=True)[:50]}")
    except Exception as e:
        print(f"  /updates: {type(e).__name__}")

print("\n" + "=" * 70)