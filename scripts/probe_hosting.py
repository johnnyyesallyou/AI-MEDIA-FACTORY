import sys, json, requests
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.content_orm import ContentORM

print("=" * 70)
print("PROBE: preview hosting + MangaDex pages")
print("=" * 70)

png = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082"
)

try:
    r = requests.post("https://catbox.moe/user/api.php",
                      data={"reqtype": "fileupload"},
                      files={"fileToUpload": ("test.png", png, "image/png")},
                      timeout=60)
    print(f"catbox: status={r.status_code} url={r.text[:60]}")
except Exception as e:
    print(f"catbox: ERROR {type(e).__name__}")

try:
    r2 = requests.post("https://0x0.st", files={"file": ("test.png", png, "image/png")}, timeout=60)
    print(f"0x0: status={r2.status_code} url={r2.text[:60]}")
except Exception as e:
    print(f"0x0: ERROR {type(e).__name__}")

UA = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
db = SessionLocal()
it = db.query(ContentORM).filter(
    ContentORM.source_url.like("%mangadex.org%"),
    ContentORM.source_text.like("%manga_title_id%")
).first()
db.close()

mid = json.loads(it.source_text).get("manga_title_id")
print(f"\nManga ID: {mid}")

r = requests.get("https://api.mangadex.org/chapter",
                 params=[("manga[]", mid), ("translatedLanguage[]", "ru"),
                         ("order[chapter]", "asc"), ("limit", "1")],
                 headers=UA, timeout=15)
data = r.json().get("data", [])
if data:
    ch_id = data[0]["id"]
    print(f"First RU chapter: {ch_id}")
    
    r2 = requests.get(f"https://api.mangadex.org/at-home/server/{ch_id}", headers=UA, timeout=15)
    d = r2.json()
    base = d.get("baseUrl")
    h = d["chapter"]["hash"]
    files = d["chapter"]["data"][:1]
    print(f"baseUrl: {base[:60]}")
    
    for f in files:
        url = f"{base}/data/{h}/{f}"
        img = requests.get(url, timeout=30)
        print(f"page: status={img.status_code} size={len(img.content)} type={img.headers.get('content-type','')[:30]}")
else:
    print("No RU chapter found")

print("=" * 70)