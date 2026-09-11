"""Sprint 76.1: Source Discovery — scoring, recommendations, RSS validation.

Проверяет:
1. Детерминированный скоринг источника (0..100) под content_type/topic/language.
2. Рекомендации: только релевантные источники, сортировка по score desc.
3. RSS/Atom валидацию (с инжектируемым fetch, без сети).
4. API endpoints /sources/discover/recommend и /sources/discover/validate.
"""
from unittest.mock import patch

from engines.source_registry import SOURCES
from engines.source_scoring import SourceDiscoveryEngine, SourceScore
from engines.source_validation import validate_feed


# ---------------------------------------------------------------------------
# Source scoring engine
# ---------------------------------------------------------------------------

def test_score_unsupported_content_type_is_zero():
    # remanga поддерживает только manga -> news должен дать 0
    defn = SOURCES["remanga"]
    score = SourceDiscoveryEngine.score_source(defn, "news")
    assert score.score == 0.0
    assert "unsupported" in score.reason


def test_score_manga_gives_high_score():
    defn = SOURCES["remanga"]
    score = SourceDiscoveryEngine.score_source(
        defn, "manga", topic="new_chapters", language="ru",
    )
    assert isinstance(score, SourceScore)
    assert score.source_id == "remanga"
    # content_type(40) + topic(20) + language(10) + capabilities(20) + rate(+)
    assert 70.0 <= score.score <= 100.0
    # manga-relevant capabilities
    assert "chapters" in score.matched_capabilities


def test_score_matches_all_manga_capabilities():
    defn = SOURCES["mangadex"]
    score = SourceDiscoveryEngine.score_source(defn, "manga")
    relevant = ("chapters", "covers", "descriptions", "genres")
    assert set(relevant).issubset(set(score.matched_capabilities))


def test_score_language_bonus_only_when_language_supported():
    # язык 'ja' есть у mangadex, у remanga нет -> mangadex должен быть выше
    mangadex = SourceDiscoveryEngine.score_source(SOURCES["mangadex"], "manga", language="ja")
    remanga = SourceDiscoveryEngine.score_source(SOURCES["remanga"], "manga", language="ja")
    assert mangadex.score > remanga.score


def test_recommend_only_relevant_sorted_desc():
    results = SourceDiscoveryEngine.recommend("manga")
    assert results, "должен быть хотя бы один источник для manga"
    for r in results:
        assert r.score > 0
        assert "manga" in SOURCES[r.source_id].content_types
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True), "сортировка по убыванию score"


def test_recommend_top_k():
    results = SourceDiscoveryEngine.recommend("manga", top_k=1)
    assert len(results) == 1


def test_recommend_knows_about_discovery():
    assert len(SOURCES) > 0


# ---------------------------------------------------------------------------
# Feed validation (unit, fetch injected — no network)
# ---------------------------------------------------------------------------

RSS_BODY = """<?xml version="1.0"?><rss version="2.0"><channel>
<title>Tech Digest</title><item><title>A</title></item><item><title>B</title></item>
</channel></rss>"""

ATOM_BODY = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>Atom Feed</title>
<entry><title>E1</title></entry></feed>"""

HTML_BODY = """<!doctype html><html><head><title>Webpage</title></head></html>"""


def test_validate_rss_ok():
    v = validate_feed("https://example.com/rss", fetch=lambda url: RSS_BODY)
    assert v.is_valid is True
    assert v.feed_type == "rss"
    assert v.title == "Tech Digest"
    assert v.item_count == 2


def test_validate_atom_ok():
    v = validate_feed("https://example.com/atom", fetch=lambda url: ATOM_BODY)
    assert v.is_valid is True
    assert v.feed_type == "atom"
    assert v.title == "Atom Feed"
    assert v.item_count == 1


def test_validate_html_not_a_feed():
    v = validate_feed("https://example.com/page", fetch=lambda url: HTML_BODY)
    assert v.is_valid is False
    assert v.feed_type == "html"
    assert v.error is not None


def test_validate_network_error_invalid():
    def boom(url):
        raise ConnectionError("refused")
    v = validate_feed("https://example.com/down", fetch=boom)
    assert v.is_valid is False
    assert v.feed_type == "none"
    assert "refused" in v.error


def test_validate_uses_httpx_when_no_fetch():
    # без fetch должен идти путь httpx.get; мокаем его, чтобы не ходить в сеть
    fake_resp = type("R", (), {"text": RSS_BODY, "raise_for_status": lambda self: None})()
    with patch("httpx.get", return_value=fake_resp) as fake_get:
        v = validate_feed("https://example.com/rss")
    fake_get.assert_called_once()
    assert v.is_valid is True
# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

def _client():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


def test_discover_recommend_endpoint():
    client = _client()
    resp = client.get("/api/v1/sources/discover/recommend", params={"content_type": "manga"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["content_type"] == "manga"
    assert data["results"], "должны быть рекомендации"
    scores = [r["score"] for r in data["results"]]
    assert scores == sorted(scores, reverse=True)


def test_discover_recommend_endpoint_top_k():
    client = _client()
    resp = client.get(
        "/api/v1/sources/discover/recommend",
        params={"content_type": "manga", "top_k": 2},
    )
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 2


def test_discover_validate_endpoint():
    client = _client()
    # мокаем validate_feed (endpoint импортирует её из engines.source_validation),
    # чтобы не ходить в сеть
    with patch("engines.source_validation.validate_feed") as m:
        m.side_effect = lambda url: validate_feed(url, fetch=lambda u: RSS_BODY)
        resp = client.post(
            "/api/v1/sources/discover/validate",
            json={"urls": ["https://example.com/rss"]},
        )
    assert resp.status_code == 200
    data = resp.json()["results"][0]
    assert data["is_valid"] is True
    assert data["feed_type"] == "rss"
    assert data["item_count"] == 2


def test_discover_validate_empty_list():
    client = _client()
    resp = client.post("/api/v1/sources/discover/validate", json={"urls": []})
    assert resp.status_code == 200
    assert resp.json()["results"] == []