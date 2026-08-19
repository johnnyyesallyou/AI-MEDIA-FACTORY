import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.manga_knowledge import MangaTitle
from engines.publishing.image_resolver import PublicationImageResolver

db = SessionLocal()
r = PublicationImageResolver()

print("=" * 70)
print("TEST: Image validation (real URLs from DB)")
print("=" * 70)

# Берём реальные URL из БД
mangadex_url = db.query(MangaTitle.cover_url).filter(
    MangaTitle.cover_url.like("%mangadex%")
).first()
remanga_url = db.query(MangaTitle.cover_url).filter(
    MangaTitle.cover_url.like("%remanga%")
).first()

tests = []
if mangadex_url:
    tests.append(("MangaDex cover (DB)", mangadex_url[0], True))
if remanga_url:
    tests.append(("ReManga cover (DB)", remanga_url[0], True))
tests.append(("Broken URL", "https://remanga.org/media/titles/nonexistent-xyz/cover.webp", False))
tests.append(("Not image", "https://remanga.org/", False))
tests.append(("None", None, False))

passed = 0
for name, url, expected in tests:
    result = r.is_valid_image_url(url)
    ok = result == expected
    status = "✅" if ok else "❌"
    if ok:
        passed += 1
    print(f"{status} {name}: {result} (expected {expected})")
    print(f"     URL: {url}")

print(f"\nPassed: {passed}/{len(tests)}")
print("=" * 70)
db.close()