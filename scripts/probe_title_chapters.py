import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

print("=" * 70)
print("RE:MANGA TITLE CHAPTERS PROBE")
print("=" * 70)

# ?????????? ????????? ??????? ?????
slug = "descendants-of-the-hero"
print(f"\nSlug: {slug}")

# 1. ???????? ?????????? ? ??????
r = requests.get(f"https://remanga.org/api/titles/{slug}/", headers=HEADERS, timeout=15)
print(f"\n[1] title info status: {r.status_code}")

if r.status_code == 200:
    data = r.json().get("data", {})
    print(f"  data keys: {list(data.keys())[:15]}")
    
    title_id = data.get("id")
    print(f"  title_id: {title_id}")
    print(f"  rus_name: {data.get('rus_name')}")
    
    # ???? ?????? ????
    chapters = data.get("chapters", [])
    print(f"  chapters count: {len(chapters)}")
    
    if chapters:
        print(f"  First chapter keys: {list(chapters[0].keys())}")
        
        # ????????? ?? ?????? ????? (????? ??????)
        sorted_chapters = sorted(chapters, key=lambda c: float(c.get('chapter', 999)))
        
        first_chapter = sorted_chapters[0]
        print(f"\n  First chapter:")
        print(f"    chapter: {first_chapter.get('chapter')}")
        print(f"    id: {first_chapter.get('id')}")
        print(f"    is_paid: {first_chapter.get('is_paid')}")
        print(f"    upload_date: {first_chapter.get('upload_date')}")
        
        # 2. ???????? ???????? ?????? ?????
        chapter_id = first_chapter.get("id")
        print(f"\n[2] Fetching pages for chapter {chapter_id}...")
        
        r2 = requests.get(
            f"https://remanga.org/api/titles/chapters/{chapter_id}/",
            headers=HEADERS,
            timeout=15
        )
        print(f"  Status: {r2.status_code}")
        
        if r2.status_code == 200:
            chapter_data = r2.json().get("data", {})
            print(f"  chapter_data keys: {list(chapter_data.keys())}")
            
            pages = chapter_data.get("pages", [])
            print(f"  pages count: {len(pages)}")
            
            # ?????????? ?????? 5 ???????
            print(f"\n  First 5 pages:")
            for i, p in enumerate(pages[:5], 1):
                if isinstance(p, dict):
                    page_url = p.get("link")
                    print(f"    {i}. {page_url[:80]}...")
                    print(f"       is_paid: {p.get('is_paid')}, is_banned: {p.get('is_banned')}")
                else:
                    print(f"    {i}. {str(p)[:80]}")
            
            # 3. ????????? ??????????? ?????? ????????
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
                        print("\n  ? First chapter pages accessible without auth!")
                    else:
                        print("\n  ? Pages NOT accessible")
        
else:
    print(f"  Response: {r.text[:300]}")

print("\n" + "=" * 70)
