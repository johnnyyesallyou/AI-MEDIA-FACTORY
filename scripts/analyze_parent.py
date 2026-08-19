import requests
from bs4 import BeautifulSoup
import re

print("=" * 70)
print("ANALYZE: parent structure of chapter-link")
print("=" * 70)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ru,en;q=0.9",
}

r = requests.get("https://readmanga.me/", headers=HEADERS, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

updates_div = soup.find("div", class_="feed-latest-updates")
chapter_links = updates_div.find_all("a", class_="chapter-link")

print(f"\nFirst 3 chapters (full parent HTML):")
for i, link in enumerate(chapter_links[:3], 1):
    print(f"\n[{i}] Chapter link: {link.get('href')}")
    
    # Поднимаемся до article или до родительского блока-карточки
    parent = link
    for _ in range(10):
        if parent.parent and parent.parent.name:
            parent = parent.parent
            classes = " ".join(parent.get("class", []))
            if "card" in classes or "tile" in classes or "item" in classes or "feed-latest-updates-item" in classes:
                break
        else:
            break
    
    print(f"  Parent tag: {parent.name}")
    print(f"  Parent classes: {' '.join(parent.get('class', []))}")
    
    # Ищем img
    img = parent.find("img")
    if img:
        cover = img.get("data-src") or img.get("src")
        print(f"  Cover URL: {cover}")
    else:
        print(f"  Cover: NOT FOUND")
        # Может быть в lazy-loaded
        lazy = parent.find(attrs={"data-background-image": True})
        if lazy:
            print(f"  Lazy cover: {lazy.get('data-background-image')}")
    
    # Ищем title (h3, h4, .title)
    title_elem = parent.find(["h3", "h4", "h5"]) or parent.find(class_=lambda c: c and "title" in c.lower())
    if title_elem:
        print(f"  Title: {title_elem.get_text(strip=True)[:60]}")

print("\n" + "=" * 70)