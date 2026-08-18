import requests
from bs4 import BeautifulSoup

print("=" * 70)
print("ANALYZE: MangaLib HTML structure")
print("=" * 70)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

r = requests.get("https://mangalib.me/", headers=HEADERS, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

print(f"\nHTML size: {len(r.text)} bytes")

# Ищем все ссылки с /manga/ в href
all_links = soup.find_all("a", href=True)
manga_links = [a for a in all_links if "/manga/" in a.get("href", "")]

print(f"\nAll links: {len(all_links)}")
print(f"Manga links: {len(manga_links)}")

if manga_links:
    print("\nFirst 5 manga links:")
    for i, a in enumerate(manga_links[:5], 1):
        href = a.get("href", "")
        text = a.get_text(strip=True)[:60]
        print(f"  [{i}] {href} -> {text}")
        
        # Смотрим parent элемент
        parent = a.parent
        if parent:
            parent_class = parent.get("class", [])
            print(f"      Parent class: {parent_class}")

# Ищем заголовки
print("\n\nH1-H3 headings:")
for tag in ["h1", "h2", "h3"]:
    headings = soup.find_all(tag)
    print(f"  {tag}: {len(headings)}")
    if headings:
        for h in headings[:3]:
            print(f"    {h.get_text(strip=True)[:60]}")

# Ищем списки/таблицы обновлений
print("\n\nSections with 'update' or 'latest' in class:")
for elem in soup.find_all(class_=True):
    classes = " ".join(elem.get("class", []))
    if "update" in classes.lower() or "latest" in classes.lower():
        print(f"  <{elem.name} class='{classes}'>")
        break

print("\n" + "=" * 70)