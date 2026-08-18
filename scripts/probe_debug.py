import requests
from datetime import datetime, timezone

HEADERS = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
NOW = datetime.now(timezone.utc)

print("=" * 70)
print("DEBUG: MangaDex publishAt values")
print("=" * 70)

print(f"Current time (UTC): {NOW.isoformat()}")

# ??????????? 20 ???? ??? ??????? ????
r = requests.get(
    "https://api.mangadex.org/chapter",
    params=[
        ("limit", 20),
        ("order[publishAt]", "desc"),
        ("translatedLanguage[]", "ru"),
        ("contentRating[]", "safe"),
        ("contentRating[]", "suggestive"),
        ("includes[]", "manga"),
    ],
    headers=HEADERS,
    timeout=15,
)

print(f"\nStatus: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(f"Total: {data.get('total')}\n")
    
    print("RAW publishAt values:")
    print("-" * 70)
    
    for i, ch in enumerate(data.get("data", [])[:20], 1):
        a = ch["attributes"]
        publish_str = a.get("publishAt", "?")
        readable_str = a.get("readableAt", "?")
        chapter_num = a.get("chapter", "?")
        pages = a.get("pages", 0)
        
        # ?????????? ?????? ???????????? NOW
        try:
            pub_dt = datetime.fromisoformat(publish_str.replace("Z", "+00:00"))
            delta = pub_dt - NOW
            status = "FUTURE" if delta.total_seconds() > 0 else "PAST"
            delta_str = f"{delta.days:+d}d {delta.seconds//3600:+d}h"
        except Exception as e:
            status = "PARSE_ERR"
            delta_str = str(e)[:30]
        
        print(f"{i:2d}. Chapter {chapter_num:>5} | {publish_str} | {status} ({delta_str})")
        print(f"    readableAt: {readable_str} | pages: {pages}")
    
    print("-" * 70)
    
    # ????????? readableAt vs publishAt
    print("\nreadableAt vs publishAt:")
    past_chapters = [ch for ch in data.get("data", [])[:20] 
                     if datetime.fromisoformat(ch['attributes']['publishAt'].replace("Z", "+00:00")) <= NOW]
    print(f"  Chapters with publishAt <= NOW: {len(past_chapters)}/{min(20, len(data.get('data', [])))}")
    
    readable_chapters = [ch for ch in data.get("data", [])[:20]
                         if ch['attributes'].get('readableAt') and ch['attributes']['readableAt'] <= NOW.isoformat()]
    print(f"  Chapters with readableAt <= NOW: {len(readable_chapters)}/{min(20, len(data.get('data', [])))}")
else:
    print(f"Response: {r.text[:300]}")

print("\n" + "=" * 70)
