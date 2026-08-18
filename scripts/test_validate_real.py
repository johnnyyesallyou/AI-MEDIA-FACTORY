import sys
sys.path.insert(0, "/app")

from engines.publishing.image_resolver import PublicationImageResolver

r = PublicationImageResolver()

# Реальные URL из БД
tests = [
    ("MangaDex cover (needs Referer)", "https://uploads.mangadex.org/covers/80422e14-b9ad-4fda-970f-de370d5fa4e5/2e5b8d5c-3a84-4e28-8e9e-1c8b8d5f6d44.jpg", True),
    ("ReManga cover (real from DB)", "https://remanga.org/media/titles/world-of-leadale/cover_123456.webp", True),  # заменим на реальный
    ("Broken URL", "https://remanga.org/media/titles/nonexistent-xyz/cover.webp", False),
    ("Not image", "https://remanga.org/", False),
    ("None", None, False),
]

print("=" * 70)
print("TEST: Image validation (with Referer fallback)")
print("=" * 70)

for name, url, expected in tests:
    result = r.is_valid_image_url(url)
    status = "✅" if result == expected else "❌"
    print(f"{status} {name}: {result} (expected {expected})")

print("=" * 70)