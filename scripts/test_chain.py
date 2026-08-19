import sys
sys.path.insert(0, "/app")

from engines.publishing.image_acquisition import ImageAcquisitionPolicy
from engines.image.unsplash_adapter import UnsplashAdapter
from engines.image.dalle_adapter import DALLEAdapter

print("=" * 70)
print("TEST: Image Fallback Chain (Sprint 38)")
print("=" * 70)

policy = ImageAcquisitionPolicy()

class FakeContent:
    headline = "📰 Тестовая новость про космос"
    draft_text = "Текст"

content = FakeContent()

# 1. Доступность адаптеров (без ключей)
print("\n[1] Adapter availability (no API keys):")
print(f"  Unsplash available: {policy.unsplash.available}")
print(f"  DALL-E available: {policy.dalle.available}")

# 2. Graceful degradation — поиск без ключа
print("\n[2] Unsplash search without key:")
result = policy.unsplash.get_best_image("space technology")
print(f"  Result: {result} (None expected)")
assert result is None

# 3. Fallback chain: unsplash(skip) → dalle(skip) → pollinations
print("\n[3] Fallback chain (news + ai_generated):")
r = policy.acquire(content, real_url=None, profile={
    "content_type": "news",
    "image_policy": {"preferred": "og_image", "fallback": "ai_generated"},
})
print(f"  source: {r.source}")
print(f"  url: {(r.url or 'None')[:80]}")
assert r.source == "ai", "Should fall through to pollinations"
print("  ✅ Chain falls through to pollinations")

# 4. Real image всегда приоритет
print("\n[4] Real image priority:")
r2 = policy.acquire(content, real_url="https://example.com/img.jpg", profile={
    "content_type": "news",
    "image_policy": {"fallback": "ai_generated"},
})
assert r2.source == "real"
print("  ✅ Real image wins")

# 5. Manga — без изменений (никакого AI/stock)
print("\n[5] Manga policy unchanged:")
r3 = policy.acquire(content, real_url=None, profile={
    "content_type": "chapter_release",
    "image_policy": {"fallback": "none"},
})
assert r3.source == "none"
print("  ✅ Manga still NO fallback")

print("\n" + "=" * 70)
print("FALLBACK CHAIN TEST PASSED ✅")
print("=" * 70)