import requests
from datetime import datetime, timezone

HEADERS = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
NOW = datetime.now(timezone.utc)

print("=" * 70)
print("MANGADEX PROBE v5 (defensive None handling)")
print("=" * 70)

print(f"Current time (UTC): {NOW.isoformat()}\n")

r = requests.get(
    "https://api.mangadex.org/chapter",
    params=[
        ("limit", 15),
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
    
    def safe_get(d, *keys, default=None):
        """?????????? ?????????? ????????? ????????."""
        for k in keys:
            if d is None:
                return default
            d = d.get(k) if isinstance(d, dict) else None
        return d if d is not None else default
    
    for i, ch in enumerate(data.get("data", [])[:15], 1):
        a = ch.get("attributes", {}) or {}
        chapter_num = a.get("chapter") or "?"
        chapter_title = a.get("title") or ""
        readable_at = a.get("readableAt") or "?"
        pages = a.get("pages") or 0
        
        # ??????? manga info ? relationships (? ??????? ?? None)
        manga_id = None
        manga_title = "?"
        for rel in ch.get("relationships", []) or []:
            if rel.get("type") == "manga":
                manga_id = rel.get("id")
                manga_attrs = rel.get("attributes") or {}  # ?????? ?? None
                manga_titles = manga_attrs.get("title") or {}  # ?????? ?? None
                manga_title = (
                    manga_titles.get("ru") or 
                    manga_titles.get("en") or 
                    manga_titles.get("ja") or
                    "?"
                )
                break
        
        # ??????????? title ??? ??????
        title_short = (chapter_title or "")[:30]
        
        print(f"{i:2d}. Ch.{chapter_num:>5} | {title_short:30s} | {readable_at[:19]}")
        print(f"    Manga: {manga_title} | pages: {pages}")
        print()
else:
    print(f"Error: {r.status_code}")
    print(r.text[:300])

print("=" * 70)
