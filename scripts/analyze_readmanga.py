import requests
from bs4 import BeautifulSoup

print("=" * 70)
print("ANALYZE: readmanga.me HTML structure")
print("=" * 70)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ru,en;q=0.9",
}

r = requests.get("https://readmanga.me/", headers=HEADERS, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

print(f"\nPage size: {len(r.text)} bytes")
print(f"Title: {soup.find('title').get_text(strip=True)}")

# Ищем все ссылки
all_links = soup.find_all("a", href=True)
print(f"Total links: {len(all_links)}")

# Ищем ссылки на главы/мангу
manga_links = [a for a in all_links if "/read/" in a.get("href", "") or a.get("href", "").count("/") >= 2]
print(f"Manga/read links: {len(manga_links)}")

if manga_links:
    print("\nFirst 10 manga links:")
    for i, a in enumerate(manga_links[:10], 1):
        href = a.get("href", "")
        text = a.get_text(strip=True)[:60]
        parent = a.parent
        parent_class = " ".join(parent.get("class", [])) if parent else ""
        print(f"  [{i}] {href}")
        print(f"       text: {text}")
        print(f"       parent: <{parent.name} class='{parent_class}'>")

# Ищем блоки с классами update/latest/new
print("\n\nLooking for update containers:")
for pattern in ["update", "latest", "new", "chapter", "recent"]:
    containers = soup.find_all(class_=lambda c: c and pattern in c.lower())
    if containers:
        print(f"\n  Pattern '{pattern}': {len(containers)} elements")
        for c in containers[:3]:
            cls = " ".join(c.get("class", []))
            print(f"    <{c.name} class='{cls}'>")

# Ищем h3, h4 заголовки
print("\n\nHeadings (h2, h3, h4):")
for tag in ["h2", "h3", "h4"]:
    headings = soup.find_all(tag)
    if headings:
        print(f"  {tag}: {len(headings)}")
        for h in headings[:3]:
            text = h.get_text(strip=True)[:60]
            parent_class = " ".join(h.parent.get("class", [])) if h.parent else ""
            print(f"    '{text}' (parent: <{h.parent.name} class='{parent_class[:40]}'>)")

print("\n" + "=" * 70)