import requests
from datetime import datetime, timezone

HEADERS = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
NOW = datetime.now(timezone.utc)

print("=" * 70)
print("MANGADEX PROBE v4 (using readableAt)")
print("=" * 70)

print(f"Current time (UTC): {NOW.isoformat()}\n")

# ?????????? readableAt ??? ?????????? ? ??????????
r = requests.get(
    "https://api.mangadex.org/chapter",
    params=[
        ("limit", 10),
        ("order[readableAt]", "desc"),
        ("translatedLanguage[]", "ru"),
        ("contentRating[]", "safe"),
        ("contentRating[]", "suggestive"),
        ("includes[]", "manga"),
    ],
    headers=HEADERS,
    timeout=15,
)

print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(f"Total: {data.get('total')}\n")
    
    for i, ch in enumerate(data.get("data", [])[:10], 1):
        a = ch["attributes"]
        chapter_num = a.get("chapter", "?")
        chapter_title = a.get("title", "")
        readable_at = a.get("readableAt", "?")
        pages = a.get("pages", 0)
        
        # ??????? manga info ? relationships
        manga_id = None
        manga_title = "?"
        for rel in ch.get("relationships", []):
            if rel.get("type") == "manga":
                manga_id = rel.get("id")
                manga_attrs = rel.get("attributes", {}) or {}
                manga_titles = manga_attrs.get("title", {}) or {}
                manga_title = manga_titles.get("ru") or manga_titles.get("en") or "?"
        
        print(f"{i:2d}. Chapter {chapter_num:>5} | {chapter_title[:30]:30s} | {readable_at}")
        print(f"    Manga: {manga_title} (ID: {manga_id})")
        print(f"    pages: {pages}")
        print()
else:
    print(f"Error: {r.status_code}")
    print(r.text[:300])

print("=" * 70)
