import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://remanga.org/",
}

slug = "descendants-of-the-hero"

print("=" * 70)
print("TEST: Full page URL with Referer")
print("=" * 70)

# ???????? ?????? ???????? ????? API
r1 = requests.get(f"https://remanga.org/api/titles/{slug}/", headers=HEADERS, timeout=15)
content = r1.json().get("content", {})
first_chapter_id = content.get("first_chapter", {}).get("id")

print(f"\nFirst chapter ID: {first_chapter_id}")

r2 = requests.get(f"https://remanga.org/api/titles/chapters/{first_chapter_id}/", headers=HEADERS, timeout=15)
ch_data = r2.json().get("content", {})

pages = ch_data.get("pages", [])
first_page = pages[0]
full_url = first_page[0]["link"] if isinstance(first_page, list) else first_page["link"]

print(f"Full URL: {full_url}")

# ???? ? Referer
r3 = requests.get(full_url, headers=HEADERS, timeout=15)
print(f"\nWith Referer:")
print(f"  Status: {r3.status_code}")
print(f"  Content-Type: {r3.headers.get('content-type', '')}")
print(f"  Size: {len(r3.content)} bytes")

if r3.status_code == 200 and len(r3.content) > 1000:
    print("\n? ACCESSIBLE with Referer!")
    with open("/tmp/test_page.jpeg", "wb") as f:
        f.write(r3.content)
    print("  Saved to /tmp/test_page.jpeg")
else:
    print(f"\n? Still blocked: {r3.text[:200]}")
    
    # ??????? ?????? Referer ????????
    print("\nTrying other Referer variants:")
    
    variants = [
        f"https://remanga.org/manga/{slug}/{first_chapter_id}/",
        f"https://remanga.org/manga/{slug}/",
        "https://remanga.org",
        "",
    ]
    
    for ref in variants:
        h = dict(HEADERS)
        if ref:
            h["Referer"] = ref
        else:
            h.pop("Referer", None)
        
        r = requests.get(full_url, headers=h, timeout=15)
        print(f"  Referer='{ref[:50]}...': status={r.status_code}, size={len(r.content)}B")
        
        if r.status_code == 200 and len(r.content) > 1000:
            print(f"    ? WORKS!")
            break

print("\n" + "=" * 70)
