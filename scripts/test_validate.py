import sys
sys.path.insert(0, "/app")

from engines.publishing.image_resolver import PublicationImageResolver

r = PublicationImageResolver()

tests = [
    ("Valid ReManga cover", "https://remanga.org/media/titles/manito/cover_5f0f24f949846f1.webp", True),
    ("Valid MangaDex cover", "https://uploads.mangadex.org/covers/80422e14-b9ad-4fda-970f-de370d5fa4e5/cover.jpg", True),
    ("Broken URL", "https://remanga.org/media/titles/nonexistent-xyz/cover.webp", False),
    ("Not image", "https://remanga.org/", False),
    ("None", None, False),
]

print("=" * 70)
print("TEST: Image validation")
print("=" * 70)

for name, url, expected in tests:
    result = r.is_valid_image_url(url)
    status = "✅" if result == expected else "❌"
    print(f"{status} {name}: {result} (expected {expected})")

print("=" * 70)