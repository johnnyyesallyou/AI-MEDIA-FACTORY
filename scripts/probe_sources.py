import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "ru,en;q=0.9",
}

targets = [
    ("zazaza_home", "https://a.zazaza.me/"),
    ("zazaza_list", "https://a.zazaza.me/list"),
    ("remanga_home", "https://remanga.org/"),
    ("remanga_api_catalog", "https://api.remanga.org/api/catalog/"),
    ("remanga_api_chapters", "https://api.remanga.org/api/titles/chapters/"),
]

print("=" * 70)
print("SOURCE CONNECTIVITY PROBE (from backend container)")
print("=" * 70)

for name, url in targets:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        ct = r.headers.get("content-type", "")[:40]
        print(f"\n[{name}]")
        print(f"  status: {r.status_code}")
        print(f"  size: {len(r.content)} bytes")
        print(f"  content-type: {ct}")

        if name == "zazaza_home" and r.status_code == 200:
            has_updates = "????????? ??????????" in r.text
            has_calendar = "?????????" in r.text
            print(f"  has_updates_block: {has_updates}")
            print(f"  has_calendar: {has_calendar}")

        if name.startswith("remanga_api") and r.status_code == 200:
            print(f"  json_preview: {r.text[:200]}")

    except Exception as e:
        print(f"\n[{name}]")
        print(f"  ERROR: {type(e).__name__}: {str(e)[:150]}")

print("\n" + "=" * 70)
print("PROBE COMPLETED")
print("=" * 70)
