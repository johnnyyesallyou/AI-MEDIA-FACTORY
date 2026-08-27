import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
REFERER = {"Referer": "https://remanga.org/"}

slug = "the-law-of-talio"  # реальный slug из предыдущих тестов
headers = {**UA, **REFERER}

print(f"=== Testing ReManga API for slug: {slug} ===\n")

# Step 1: title info
r1 = requests.get(f"https://remanga.org/api/titles/{slug}/", headers=headers, timeout=10)
print(f"1. Title API: status={r1.status_code}")
if r1.status_code == 200:
    data = r1.json()
    content = data.get("content", {})
    print(f"   Content keys: {list(content.keys())[:10]}")
    
    first_chapter = content.get("first_chapter")
    print(f"   first_chapter: {first_chapter}")
    
    if first_chapter:
        chapter_id = first_chapter.get("id") if isinstance(first_chapter, dict) else first_chapter
        print(f"   chapter_id: {chapter_id}")
        
        # Step 2: chapter pages
        r2 = requests.get(f"https://remanga.org/api/titles/chapters/{chapter_id}/", headers=headers, timeout=10)
        print(f"\n2. Chapter API: status={r2.status_code}")
        if r2.status_code == 200:
            pages = r2.json().get("content", {}).get("pages", [])
            print(f"   Pages count: {len(pages)}")
            if pages:
                print(f"   First page structure: {pages[0]}")
        else:
            print(f"   Error: {r2.text[:200]}")
else:
    print(f"   Error: {r1.text[:200]}")

# Fallback: chapters endpoint
print(f"\n3. Fallback: chapters endpoint")
r3 = requests.get(f"https://remanga.org/api/titles/{slug}/chapters", headers=headers, timeout=10)
print(f"   Status: {r3.status_code}")
if r3.status_code == 200:
    chapters = r3.json().get("content", [])
    print(f"   Chapters count: {len(chapters)}")
    if chapters:
        print(f"   Last chapter: {chapters[-1].get('id')} - chapter {chapters[-1].get('chapter')}")