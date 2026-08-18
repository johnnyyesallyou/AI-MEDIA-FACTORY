import sys, json, requests
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.content_orm import ContentORM

print("=" * 70)
print("EXTENDED PROBE: hosting + MangaDex EN fallback")
print("=" * 70)

UA_BROWSER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
UA_BOT = {"User-Agent": "AI-Media-Factory/1.0"}

# 1x1 PNG
png = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082"
)

# --- catbox с User-Agent ---
print("\n[1] catbox.moe (with User-Agent)")
try:
    r = requests.post(
        "https://catbox.moe/user/api.php",
        data={"reqtype": "fileupload"},
        files={"fileToUpload": ("test.png", png, "image/png")},
        headers=UA_BROWSER,
        timeout=60
    )
    print(f"  status={r.status_code} response={r.text[:80]}")
except Exception as e:
    print(f"  ERROR: {e}")

# --- catbox без User-Agent ---
print("\n[2] catbox.moe (no User-Agent)")
try:
    r = requests.post(
        "https://catbox.moe/user/api.php",
        data={"reqtype": "fileupload"},
        files={"fileToUpload": ("test.png", png, "image/png")},
        timeout=60
    )
    print(f"  status={r.status_code} response={r.text[:80]}")
except Exception as e:
    print(f"  ERROR: {e}")

# --- Telegraph upload (image) ---
print("\n[3] Telegraph upload (image)")
try:
    r = requests.post(
        "https://telegra.ph/upload",
        files={"file": ("test.png", png, "image/png")},
        headers=UA_BROWSER,
        timeout=60
    )
    print(f"  status={r.status_code} response={r.text[:120]}")
except Exception as e:
    print(f"  ERROR: {e}")

# --- Imgur anonymous (без API key) ---
print("\n[4] Imgur anonymous upload")
try:
    import base64
    b64 = base64.b64encode(png).decode()
    r = requests.post(
        "https://api.imgur.com/3/image",
        data={"image": b64, "type": "base64"},
        headers={"Authorization": "Client-ID 546c25a59c58ad7"},  # public anonymous client id
        timeout=60
    )
    print(f"  status={r.status_code} response={r.text[:120]}")
except Exception as e:
    print(f"  ERROR: {e}")

# --- Telegraph upload (ReManga image via URL) ---
print("\n[5] Telegraph upload from ReManga URL (external)")
try:
    r = requests.post(
        "https://telegra.ph/upload",
        data={"url": "https://remanga.org/media/titles/descendants-of-the-hero/cover_5f24f949fbd248d5.webp"},
        headers=UA_BROWSER,
        timeout=60
    )
    print(f"  status={r.status_code} response={r.text[:200]}")
except Exception as e:
    print(f"  ERROR: {e}")

# --- MangaDex: первая EN глава (fallback) ---
print("\n[6] MangaDex: first EN chapter (fallback)")
db = SessionLocal()
it = db.query(ContentORM).filter(
    ContentORM.source_url.like("%mangadex.org%"),
    ContentORM.source_text.like("%manga_title_id%")
).first()
db.close()

if it:
    mid = json.loads(it.source_text).get("manga_title_id")
    print(f"  Manga ID: {mid[:20]}...")
    
    r = requests.get("https://api.mangadex.org/chapter",
                    params=[("manga[]", mid),
                            ("translatedLanguage[]", "ru"),
                            ("translatedLanguage[]", "en"),
                            ("order[chapter]", "asc"),
                            ("limit", "5"),
                            ("includes[]", "scanlation_group")],
                    headers=UA_BOT, timeout=15)
    data = r.json().get("data", [])
    print(f"  Found {len(data)} chapters")
    
    if data:
        # Ищем RU, иначе EN
        ru_ch = next((c for c in data if c["attributes"].get("translatedLanguage") == "ru"), None)
        en_ch = next((c for c in data if c["attributes"].get("translatedLanguage") == "en"), None)
        
        chosen = ru_ch or en_ch
        if chosen:
            lang = chosen["attributes"].get("translatedLanguage")
            ch_id = chosen["id"]
            print(f"  Using {lang.upper()} chapter: {ch_id[:20]}...")
            
            r2 = requests.get(f"https://api.mangadex.org/at-home/server/{ch_id}", headers=UA_BOT, timeout=15)
            d = r2.json()
            base = d.get("baseUrl")
            h = d["chapter"]["hash"]
            files = d["chapter"]["data"][:2]
            print(f"  baseUrl: {base[:60]}")
            print(f"  pages: {len(d['chapter']['data'])}")
            
            for f in files[:1]:
                url = f"{base}/data/{h}/{f}"
                img = requests.get(url, headers=UA_BOT, timeout=30)
                print(f"  page: status={img.status_code} size={len(img.content)}")

print("\n" + "=" * 70)