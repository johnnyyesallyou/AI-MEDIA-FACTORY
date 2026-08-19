"""Hermetic tests for ImageAcquisitionPolicy (Sprint 33/38)."""
import pytest

try:
    from engines.publishing.image_acquisition import ImageAcquisitionPolicy
except Exception as e:  # pragma: no cover
    pytest.skip(f"image_acquisition not importable here: {e}", allow_module_level=True)


class FakeContent:
    headline = "Тестовая новость"
    draft_text = "текст"


def test_real_image_priority():
    p = ImageAcquisitionPolicy()
    r = p.acquire(FakeContent(), real_url="https://example.com/img.jpg",
                  profile={"content_type": "news", "image_policy": {"fallback": "ai_generated"}})
    assert r.source == "real"


def test_manga_no_fallback():
    p = ImageAcquisitionPolicy()
    r = p.acquire(FakeContent(), real_url=None,
                  profile={"content_type": "chapter_release", "image_policy": {"fallback": "none"}})
    assert r.source == "none"


def test_news_fallback_chain_without_keys():
    p = ImageAcquisitionPolicy()
    r = p.acquire(FakeContent(), real_url=None,
                  profile={"content_type": "news", "image_policy": {"fallback": "ai_generated"}})
    # Без API-ключей цепочка доходит до pollinations (source="ai")
    assert r.source == "ai"