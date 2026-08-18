import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

print("=" * 70)
print("RE:MANGA CHAPTER PAGES PROBE")
print("=" * 70)

# 1. ????? ????????? ?????
r = requests.get("https://remanga.org/api/titles/last-chapters/", headers=HEADERS, timeout=15)
print(f"\n[1] last-chapters status: {r.status_code}")
chapters = r.json().get("data", [])

if not chapters:
    print("No chapters!")
    exit(1)

ch = chapters[0]
print(f"  First chapter keys: {list(ch.keys())}")
print(f"  Title: {ch.get('rus_name')}")

chapter_id = ch.get("chapter_id") or ch.get("id")
print(f"  chapter_id: {chapter_id}")

# 2. ???????? ?????? ????? ?? ??????????
r2 = requests.get(
    f"https://remanga.org/api/titles/chapters/{chapter_id}/",
    headers=HEADERS,
    timeout=15
)
print(f"\n[2] chapter detail status: {r2.status_code}")

if r2.status_code == 200:
    data = r2.json().get("data", {})
    print(f"  data keys: {list(data.keys())}")
    
    pages = data.get("pages", [])
    print(f"  pages count: {len(pages)}")
    
    # ?????????? ????????? ?????? ???????
    for i, p in enumerate(pages[:6], 1):
        if isinstance(p, dict):
            print(f"\n  Page {i}:")
            print(f"    keys: {list(p.keys())}")
            print(f"    link: {str(p.get('link'))[:100]}")
            print(f"    is_paid: {p.get('is_paid')}")
            print(f"    is_banned: {p.get('is_banned')}")
        else:
            print(f"\n  Page {i}: {str(p)[:100]}")
else:
    print(f"  Response: {r2.text[:300]}")

# 3. ????????? ??????????? ?????? ???????? ??? ???????????
if r2.status_code == 200:
    pages = r2.json().get("data", {}).get("pages", [])
    if pages:
        first_page = pages[0]
        page_url = first_page.get("link") if isinstance(first_page, dict) else first_page
        
        if page_url:
            print(f"\n[3] Testing page accessibility (no auth):")
            print(f"  URL: {page_url[:100]}")
            
            r3 = requests.get(page_url, headers=HEADERS, timeout=15)
            print(f"  Status: {r3.status_code}")
            print(f"  Content-Type: {r3.headers.get('content-type', '')[:50]}")
            print(f"  Size: {len(r3.content)} bytes")
            
            if r3.status_code == 200 and len(r3.content) > 1000:
                print("\n  ? Page accessible without auth!")
            else:
                print("\n  ? Page NOT accessible (hotlink protection?)")

print("\n" + "=" * 70)
