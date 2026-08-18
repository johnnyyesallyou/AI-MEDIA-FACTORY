import sys
sys.path.insert(0, "/app")

from engines.publishing.image_acquisition import ImageAcquisitionPolicy

print("=" * 70)
print("TEST: ImageAcquisitionPolicy")
print("=" * 70)

policy = ImageAcquisitionPolicy()

class FakeContent:
    headline = "Тестовая новость про ИИ"
    draft_text = "Текст новости"

content = FakeContent()

# 1. MANGA без cover → NONE (НЕ AI!)
r1 = policy.acquire(content, real_url=None, profile={
    "content_type": "chapter_release",
    "image_policy": {"preferred": "manga_cover", "fallback": "none"},
})
print(f"\n[1] MANGA без cover: source={r1.source}, url={r1.url}")
assert r1.source == "none" and r1.url is None, "Manga must NOT use AI!"
print("    ✅ AI fallback запрещён для manga")

# 2. ANIME без cover → NONE (НЕ AI!)
r2 = policy.acquire(content, real_url=None, profile={
    "content_type": "anime_release",
    "image_policy": {"preferred": "anime_cover", "fallback": "none"},
})
print(f"\n[2] ANIME без cover: source={r2.source}, url={r2.url}")
assert r2.source == "none", "Anime must NOT use AI!"
print("    ✅ AI fallback запрещён для anime")

# 3. NEWS с реальной картинкой → REAL
r3 = policy.acquire(content, real_url="https://example.com/img.jpg", profile={
    "content_type": "news",
    "image_policy": {"preferred": "og_image", "fallback": "ai_generated"},
})
print(f"\n[3] NEWS с og:image: source={r3.source}")
assert r3.source == "real", "News with og:image must use real!"
print("    ✅ Реальная картинка — приоритет")

# 4. NEWS без картинки + fallback=ai_generated → AI (Pollinations URL)
r4 = policy.acquire(content, real_url=None, profile={
    "content_type": "news",
    "image_policy": {"preferred": "og_image", "fallback": "ai_generated", "style": "news"},
})
print(f"\n[4] NEWS без og:image + ai fallback: source={r4.source}")
print(f"    url: {(r4.url or 'None')[:80]}")
print(f"    prompt: {(r4.prompt or 'None')[:80]}")
assert r4.source == "ai" and r4.url, "News should get AI fallback!"
print("    ✅ AI fallback работает (controlled)")

# 5. NEWS без картинки + fallback=none → NONE
r5 = policy.acquire(content, real_url=None, profile={
    "content_type": "news",
    "image_policy": {"preferred": "og_image", "fallback": "none"},
})
print(f"\n[5] NEWS без og:image + fallback=none: source={r5.source}")
assert r5.source == "none"
print("    ✅ Fallback=none уважается")

print("\n" + "=" * 70)
print("ALL POLICY TESTS PASSED ✅")
print("=" * 70)