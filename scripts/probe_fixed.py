import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

slug = "descendants-of-the-hero"

print("=" * 70)
print("RE:MANGA FIRST CHAPTER - FIXED PROBE")
print("=" * 70)

# 1. ???????? title info
r = requests.get(f"https://remanga.org/api/titles/{slug}/", headers=HEADERS, timeout=15)
print(f"\n[1] /api/titles/{slug}/")
print(f"  Status: {r.status_code}")

content = r.json().get("content", {})
print(f"  main_name: {content.get('main_name')}")
print(f"  title_id: {content.get('id')}")

# ????????? first_chapter
first_chapter_info = content.get("first_chapter")
print(f"\n  first_chapter: {json.dumps(first_chapter_info, ensure_ascii=False)[:300] if first_chapter_info else 'None'}")

# 2. ?????????? ID ?????? ?????
first_chapter_id = None

if isinstance(first_chapter_info, dict):
    first_chapter_id = first_chapter_info.get("id")
    print(f"\n  ? first_chapter.id = {first_chapter_id}")
elif isinstance(first_chapter_info, int):
    first_chapter_id = first_chapter_info
    print(f"\n  ? first_chapter (direct) = {first_chapter_id}")

if not first_chapter_id:
    print("  ? first_chapter not found, trying branches[0]")
    branches = content.get("branches", [])
    if branches:
        first_chapter_id = branches[0].get("id")
        print(f"  Using branch_id = {first_chapter_id}")

# 3. ???????? ???????? ?????? ?????
print(f"\n[2] /api/titles/chapters/{first_chapter_id}/")
r2 = requests.get(f"https://remanga.org/api/titles/chapters/{first_chapter_id}/", headers=HEADERS, timeout=15)
print(f"  Status: {r2.status_code}")

ch_data = r2.json().get("content", {})
print(f"  chapter number: {ch_data.get('chapter')}")
print(f"  tome: {ch_data.get('tome')}")
print(f"  is_paid: {ch_data.get('is_paid')}")
print(f"  upload_date: {ch_data.get('upload_date')}")

pages = ch_data.get("pages", [])
print(f"  pages count: {len(pages)}")

# 4. ????????? URL ??????? (pages - ?????? ???????)
print(f"\n[3] Extracting page URLs (first 5):")
page_urls = []

for i, page_item in enumerate(pages[:5], 1):
    # page_item ????? ???? ??????? [{'id': 1, 'link': '...'}]
    if isinstance(page_item, list) and page_item:
        page_obj = page_item[0]
        if isinstance(page_obj, dict):
            url = page_obj.get("link")
            height = page_obj.get("height")
            width = page_obj.get("width")
            page_urls.append(url)
            print(f"  {i}. {url[:80]}")
            print(f"     size: {width}x{height}")
    elif isinstance(page_item, dict):
        url = page_item.get("link")
        page_urls.append(url)
        print(f"  {i}. {url[:80]}")

# 5. ????????? ??????????? ?????? 3 ???????
print(f"\n[4] Testing page accessibility (first 3 pages):")
success_count = 0

for i, url in enumerate(page_urls[:3], 1):
    if not url:
        continue
    
    try:
        r3 = requests.get(url, headers=HEADERS, timeout=15)
        print(f"  Page {i}: status={r3.status_code}, size={len(r3.content)}B, type={r3.headers.get('content-type', '')[:30]}")
        
        if r3.status_code == 200 and len(r3.content) > 1000:
            success_count += 1
    except Exception as e:
        print(f"  Page {i}: ERROR {e}")

print(f"\n  Success: {success_count}/3 pages accessible")

if success_count == 3:
    print("\n? ALL PAGES ACCESSIBLE - can create preview!")
else:
    print("\n?? Some pages blocked")

print("\n" + "=" * 70)
