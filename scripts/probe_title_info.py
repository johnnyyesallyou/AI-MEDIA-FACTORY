import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ru,en;q=0.9",
}

print("=" * 70)
print("ReManga TITLE INFO API PROBE")
print("=" * 70)

# ??????? ???????? ?????? ?????????? ? ??????
test_slugs = ["i-come-from-game", "descendants-of-the-hero"]

for slug in test_slugs:
    url = f"https://api.remanga.org/api/titles/{slug}/"
    print(f"\n[GET] {url}")
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"  Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            content = data.get("content", {})
            
            print(f"\n  Keys: {list(content.keys())}")
            
            # ???? ????????
            for key in ["description", "desc", "summary", "annotation"]:
                if content.get(key):
                    desc = content[key]
                    print(f"\n  [{key}] ({len(desc)} chars):")
                    print(f"    {desc[:300]}...")
                    break
            
            # ???? ?????/????
            for key in ["genres", "tags", "categories"]:
                if content.get(key):
                    genres = content[key]
                    print(f"\n  [{key}]:")
                    if isinstance(genres, list) and genres:
                        if isinstance(genres[0], dict):
                            names = [g.get("name", g.get("rus_name", "")) for g in genres[:25]]
                        else:
                            names = genres[:25]
                        print(f"    {names}")
                    break
            
            # ???? ?????? ???????? ????
            for key in ["type", "status", "rating", "branches_count", "count_chapters"]:
                if key in content:
                    print(f"  {key}: {content[key]}")
        else:
            print(f"  Response: {r.text[:200]}")
    
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {str(e)[:150]}")

print("\n" + "=" * 70)
