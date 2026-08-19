import requests
from bs4 import BeautifulSoup

print("=" * 70)
print("ANALYZE: ReadManga title page structure")
print("=" * 70)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ru,en;q=0.9",
}

slug = "34223"  # Сильнейшая служанка культа
url = f"https://readmanga.me/{slug}"
r = requests.get(url, headers=HEADERS, timeout=20)
soup = BeautifulSoup(r.text, "html.parser")

print(f"\nURL: {url}")
print(f"Status: {r.status_code}")
print(f"Title: {soup.find('title').get_text(strip=True) if soup.find('title') else 'N/A'}")

# 1. Description
print("\n[1] Description candidates:")
desc_patterns = ["description", "summary", "about", "annotation", "synopsis", "desc"]
for pattern in desc_patterns:
    elements = soup.find_all(class_=lambda c: c and pattern in " ".join(c).lower())
    if elements:
        print(f"  Class matching '{pattern}': {len(elements)}")
        for el in elements[:2]:
            cls = " ".join(el.get("class", []))
            text = el.get_text(strip=True)[:100]
            print(f"    <{el.name} class='{cls[:60]}'>")
            print(f"    text: {text}")

# Проверяем meta теги
meta_desc = soup.find("meta", attrs={"name": "description"})
if meta_desc:
    print(f"\n  Meta description: {meta_desc.get('content', '')[:100]}")

# 2. Genres
print("\n[2] Genre candidates:")
genre_patterns = ["genre", "tag", "category", "element"]
for pattern in genre_patterns:
    elements = soup.find_all(class_=lambda c: c and pattern in " ".join(c).lower())
    if elements:
        print(f"  Class matching '{pattern}': {len(elements)}")
        for el in elements[:3]:
            cls = " ".join(el.get("class", []))
            text = el.get_text(strip=True)[:60]
            print(f"    <{el.name} class='{cls[:60]}'> text='{text}'")

# Проверяем ссылки с genre
genre_links = soup.find_all("a", href=lambda h: h and "/genre/" in str(h))
if genre_links:
    print(f"\n  Links with /genre/: {len(genre_links)}")
    for a in genre_links[:5]:
        print(f"    {a.get('href')} -> {a.get_text(strip=True)}")

# 3. Cover
print("\n[3] Cover candidates:")
cover_imgs = soup.find_all("img", class_=lambda c: c and "cover" in " ".join(c).lower())
if cover_imgs:
    print(f"  img with 'cover' class: {len(cover_imgs)}")
    for img in cover_imgs[:3]:
        src = img.get("data-src") or img.get("src")
        cls = " ".join(img.get("class", []))
        print(f"    <img class='{cls[:50]}'> src={src}")

# Проверяем все большие картинки
big_imgs = [img for img in soup.find_all("img") if img.get("width") or img.get("height")]
if big_imgs:
    print(f"\n  All sized imgs: {len(big_imgs)}")
    for img in big_imgs[:3]:
        src = img.get("data-src") or img.get("src")
        print(f"    {img.get('width')}x{img.get('height')} src={src}")

print("\n" + "=" * 70)