import requests
from datetime import datetime, timezone

HEADERS = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
NOW = datetime.now(timezone.utc)

print("=" * 70)
print("MANGADEX API PROBE v3 (fixes)")
print("=" * 70)

# 1. ?????? ? RU ?????????? (?????? ?? ?????)
print("\n[1] GET /manga?availableTranslatedLanguage[ru]=ru:")
r = requests.get(
    "https://api.mangadex.org/manga",
    params=[
        ("limit", 5),
        ("order[latestUploadedChapter]", "desc"),
        ("availableTranslatedLanguage[]", "ru"),
        ("contentRating[]", "safe"),
        ("contentRating[]", "suggestive"),
        ("includes[]", "cover_art"),
    ],
    headers=HEADERS,
    timeout=15,
)
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"  Total: {data.get('total')}")
    
    # MangaDex ?????????? ?????????????? ?????
    for item in data.get("data", [])[:5]:
        attrs = item["attributes"]
        titles = attrs.get("title", {}) or {}
        alt_titles = attrs.get("altTitles", []) or []
        
        # ???????? ??? ????????? ????????
        title_ru = titles.get("ru")
        title_en = titles.get("en")
        title_ja = titles.get("ja")
        
        # ???? ??? ????????? title ? ???? ? altTitles
        if not (title_ru or title_en):
            for alt in alt_titles:
                if isinstance(alt, dict):
                    if "ru" in alt:
                        title_ru = alt["ru"]
                    if "en" in alt:
                        title_en = alt["en"]
        
        # ???????
        cover = None
        for rel in item.get("relationships", []):
            if rel.get("type") == "cover_art":
                cover = rel.get("attributes", {}).get("fileName")
        cover_url = f"https://uploads.mangadex.org/covers/{item['id']}/{cover}.512.jpg" if cover else None
        
        # ????????
        desc = attrs.get("description", {}) or {}
        desc_ru = desc.get("ru") or desc.get("en") or ""
        
        # ????
        tags = [t.get("attributes", {}).get("name", {}).get("en") for t in (attrs.get("tags") or [])]
        
        print(f"\n  ID: {item['id']}")
        print(f"    Title RU: {title_ru}")
        print(f"    Title EN: {title_en}")
        print(f"    Title JA: {title_ja}")
        print(f"    Rating: {attrs.get('contentRating')}")
        print(f"    Status: {attrs.get('status')}")
        print(f"    Cover: {cover_url[:80] if cover_url else None}...")
        print(f"    Desc (100 chars): {desc_ru[:100]}...")
        print(f"    Tags: {tags[:5]}")
else:
    print(f"  Response: {r.text[:300]}")

# 2. RU ????? ? ?????????? ???????????
print("\n\n[2] GET /chapter (RU + manga include + date filter):")
r2 = requests.get(
    "https://api.mangadex.org/chapter",
    params=[
        ("limit", 10),
        ("order[publishAt]", "desc"),
        ("translatedLanguage[]", "ru"),
        ("contentRating[]", "safe"),
        ("contentRating[]", "suggestive"),
        ("includes[]", "manga"),
        ("includes[]", "scanlation_group"),
    ],
    headers=HEADERS,
    timeout=15,
)
print(f"  Status: {r2.status_code}")
if r2.status_code == 200:
    data2 = r2.json()
    valid_chapters = []
    for ch in data2.get("data", [])[:15]:
        a = ch["attributes"]
        
        # ????????? ??????? (publishAt <= NOW)
        publish_str = a.get("publishAt") or ""
        try:
            pub_dt = datetime.fromisoformat(publish_str.replace("Z", "+00:00"))
            if pub_dt > NOW:
                continue  # ?????????? ??????? (?????)
        except Exception:
            continue
        
        # ??????? manga info ? relationships
        manga_id = None
        manga_title = None
        for rel in ch.get("relationships", []):
            if rel.get("type") == "manga":
                manga_id = rel.get("id")
                manga_attrs = rel.get("attributes", {}) or {}
                manga_titles = manga_attrs.get("title", {}) or {}
                manga_title = manga_titles.get("ru") or manga_titles.get("en") or "?"
        
        valid_chapters.append({
            "chapter_num": a.get("chapter"),
            "chapter_title": a.get("title"),
            "manga_id": manga_id,
            "manga_title": manga_title,
            "publishAt": publish_str,
            "pages": a.get("pages"),
            "chapter_id": ch.get("id"),
        })
    
    print(f"  Total from API: {data2.get('total')}, valid: {len(valid_chapters)}")
    for ch in valid_chapters[:5]:
        print(f"\n  Chapter {ch['chapter_num']} | '{ch['chapter_title']}'")
        print(f"    Manga ID: {ch['manga_id']}")
        print(f"    Manga title: {ch['manga_title']}")
        print(f"    publishAt: {ch['publishAt']}")
        print(f"    pages: {ch['pages']}")
else:
    print(f"  Response: {r2.text[:300]}")

print("\n" + "=" * 70)
