import requests
from bs4 import BeautifulSoup
import re

print("=" * 70)
print("ANALYZE: readmanga.me chapter structure")
print("=" * 70)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ru,en;q=0.9",
}

r = requests.get("https://readmanga.me/", headers=HEADERS, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

# Ищем блоки feed-latest-updates
updates_div = soup.find("div", class_="feed-latest-updates")
if not updates_div:
    print("❌ feed-latest-updates not found")
    exit()

# Находим все chapter-link
chapter_links = updates_div.find_all("a", class_="chapter-link")
print(f"\nTotal chapter-links: {len(chapter_links)}")

print("\nFirst 5 chapter entries (detailed):")
for i, link in enumerate(chapter_links[:5], 1):
    print(f"\n[{i}]")
    
    # URL
    href = link.get("href", "")
    print(f"  href: {href}")
    
    # Извлекаем slug и chapter из URL
    # Паттерн: /read/slug/vol/chapter
    match = re.search(r'/read/([^/]+)/v(\d+)/(\d+)', href)
    if match:
        slug, vol, ch = match.groups()
        print(f"  parsed: slug={slug}, vol={vol}, chapter={ch}")
    else:
        print(f"  parsed: (no match)")
    
    # Parent structure
    parent = link.parent
    print(f"  parent: <{parent.name} class='{' '.join(parent.get('class', []))}'>")
    
    # Ищем заголовок манги (обычно в родителе или рядом)
    title_elem = None
    for ancestor in link.parents:
        h4 = ancestor.find("h4")
        if h4:
            title_elem = h4
            break
        # Или ищем в sibling
        if ancestor.name == "div":
            title_elem = ancestor.find("h4")
            if title_elem:
                break
    
    if title_elem:
        title_text = title_elem.get_text(strip=True)
        print(f"  title: {title_text[:60]}")
    
    # Ищем cover (img тег)
    img = link.find("img")
    if img:
        cover_url = img.get("src") or img.get("data-src")
        print(f"  cover: {cover_url[:80] if cover_url else 'None'}")
    
    # Ищем дату
    date_elem = None
    for ancestor in link.parents:
        date_span = ancestor.find("span", class_=lambda c: c and "date" in c.lower())
        if date_span:
            date_elem = date_span
            break
        time_elem = ancestor.find("time")
        if time_elem:
            date_elem = time_elem
            break
    
    if date_elem:
        date_text = date_elem.get("datetime") or date_elem.get_text(strip=True)
        print(f"  date: {date_text}")
    
    # Полный HTML для понимания
    print(f"  HTML snippet: {str(link)[:200]}")

print("\n" + "=" * 70)