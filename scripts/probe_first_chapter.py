import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

slug = "descendants-of-the-hero"

print("=" * 70)
print("RE:MANGA FIRST CHAPTER PAGES PROBE")
print("=" * 70)

# 1. ???????? ?????? ?????????? ? ?????? (? chapters)
print(f"\n[1] /api/titles/{slug}/")
r = requests.get(f"https://remanga.org/api/titles/{slug}/", headers=HEADERS, timeout=15)
print(f"  Status: {r.status_code}")

data = r.json()
content = data.get("content", {})

print(f"  content keys: {list(content.keys())[:20]}")
print(f"  id: {content.get('id')}")
print(f"  main_name: {content.get('main_name')}")

# ???? chapters
chapters = content.get("chapters") or content.get("branches") or []
print(f"  chapters count: {len(chapters)}")

if chapters:
    print(f"\n  First chapter keys: {list(chapters[0].keys())}")
    print(f"  First chapter sample: {json.dumps(chapters[0], ensure_ascii=False)[:300]}")
    
    # ????????? ?? ?????? ?????
    def get_chapter_num(ch):
        num = ch.get("chapter") or ch.get("number") or "999"
        try:
            return float(num)
        except (ValueError, TypeError):
            return 999.0
    
    sorted_chapters = sorted(chapters, key=get_chapter_num)
    first_chapter = sorted_chapters[0]
    
    print(f"\n  First chapter:")
    print(f"    chapter: {first_chapter.get('chapter')}")
    print(f"    id: {first_chapter.get('id')}")
    print(f"    is_paid: {first_chapter.get('is_paid')}")
    print(f"    upload_date: {first_chapter.get('upload_date')}")
    
    # 2. ???????? ???????? ?????? ?????
    chapter_id = first_chapter.get("id")
    print(f"\n[2] /api/titles/chapters/{chapter_id}/")
    
    r2 = requests.get(f"https://remanga.org/api/titles/chapters/{chapter_id}/", headers=HEADERS, timeout=15)
    print(f"  Status: {r2.status_code}")
    
    if r2.status_code == 200:
        ch_data = r2.json().get("content", {})
        print(f"  content keys: {list(ch_data.keys())}")
        
        pages = ch_data.get("pages", [])
        print(f"  pages count: {len(pages)}")
        
        # ?????????? ?????? 5 ???????
        print(f"\n  First 5 pages:")
        for i, p in enumerate(pages[:5], 1):
            if isinstance(p, dict):
                page_url = p.get("link") or p.get("url")
                print(f"    {i}. {page_url[:80]}")
                print(f"       keys: {list(p.keys())}")
                print(f"       is_paid: {p.get('is_paid')}")
            else:
                print(f"    {i}. {str(p)[:80]}")
        
        # 3. ????????? ??????????? ?????? ????????
        if pages:
            first_page = pages[0]
            page_url = first_page.get("link") or first_page.get("url") if isinstance(first_page, dict) else first_page
            
            if page_url:
                print(f"\n[3] Testing page accessibility:")
                print(f"  URL: {page_url[:100]}")
                
                r3 = requests.get(page_url, headers=HEADERS, timeout=15)
                print(f"  Status: {r3.status_code}")
                print(f"  Content-Type: {r3.headers.get('content-type', '')[:50]}")
                print(f"  Size: {len(r3.content)} bytes")
                
                if r3.status_code == 200 and len(r3.content) > 1000:
                    print("\n  ? First chapter pages accessible!")
                else:
                    print("\n  ? Pages NOT accessible")

print("\n" + "=" * 70)
