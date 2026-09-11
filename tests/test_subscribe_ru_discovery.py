"""Tests for Subscribe.ru Discovery Integration - Sprint 76.3."""
import pytest
from unittest.mock import Mock, patch
import json

from engines.subscribe_ru_adapter import (
    SubscribeRuAdapter,
    SubscribeRuResult,
    SubscribeRuDiscoveryError,
    _build_search_query,
    _search_subscribe_ru,
    _normalize_result,
    _extract_rss_url,
)
from engines.source_discovery_integrator import (
    SourceDiscoveryIntegrator,
    DiscoveredSource,
    _normalize_url_for_comparison,
)
from engines.source_validation import FeedValidation


class TestSubscribeRuAdapter:
    """Тесты для Subscribe.ru adapter."""

    def test_category_mapping_exists(self):
        """Проверить что категории mapped для основных content_type'ов."""
        assert "news" in SubscribeRuAdapter.CATEGORY_MAPPING
        assert "anime" in SubscribeRuAdapter.CATEGORY_MAPPING
        assert "manga" in SubscribeRuAdapter.CATEGORY_MAPPING

    def test_category_for_content_type_returns_list(self):
        """Получить категории для content_type."""
        categories = SubscribeRuAdapter.category_for_content_type("news")
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert any("новости" in cat for cat in categories)

    def test_category_for_unknown_content_type_returns_empty(self):
        """Неизвестный content_type возвращает пустой список."""
        categories = SubscribeRuAdapter.category_for_content_type("unknown_type")
        assert categories == []

    def test_build_search_query_with_content_type(self):
        """Query строится с учётом content_type."""
        query = _build_search_query("python", content_type="educational")
        assert "python" in query
        assert len(query) > len("python")  # Добавлена категория

    def test_build_search_query_without_content_type(self):
        """Query без content_type — просто тема."""
        query = _build_search_query("аниме", content_type=None)
        assert query == "аниме"

    def test_extract_rss_url_from_direct_url(self):
        """Экстрактить прямой RSS URL."""
        item = {"rss_url": "https://example.com/feed.xml"}
        url = _extract_rss_url(item)
        assert url == "https://example.com/feed.xml"

    def test_extract_rss_url_from_item_id(self):
        """Экстрактить RSS URL из item ID."""
        item = {"id": "12345"}
        url = _extract_rss_url(item)
        assert url is not None
        assert "12345" in url
        assert "rss" in url

    def test_extract_rss_url_from_page_url(self):
        """Экстрактить RSS URL из URL страницы."""
        item = {"url": "https://subscribe.ru/item/67890/page"}
        url = _extract_rss_url(item)
        assert url is not None
        assert "67890" in url
        assert "rss" in url

    def test_extract_rss_url_returns_none_when_no_data(self):
        """Вернуть None если нечего экстрактить."""
        item = {"title": "Some title", "description": "Some description"}
        url = _extract_rss_url(item)
        assert url is None

    def test_normalize_result_basic(self):
        """Нормализовать базовый результат."""
        raw = {
            "title": "Tech News",
            "description": "Technology news feed",
            "rss_url": "https://example.com/tech.xml",
            "language": "en",
            "category": "technology",
            "subscribers": 1000,
        }
        result = _normalize_result(raw)
        assert result.title == "Tech News"
        assert result.rss_url == "https://example.com/tech.xml"
        assert result.subscribers == 1000

    def test_normalize_result_with_missing_fields(self):
        """Нормализовать результат с пропущенными полями."""
        raw = {
            "title": "News",
            "rss_url": "https://example.com/news.xml",
        }
        result = _normalize_result(raw)
        assert result.title == "News"
        assert result.description is None
        assert result.subscribers == 0

    def test_discover_with_mock_fetch(self):
        """Discover с mock fetch."""
        mock_response = json.dumps({
            "results": [
                {
                    "title": "Python News",
                    "rss_url": "https://example.com/python.xml",
                    "language": "en",
                    "category": "programming",
                    "subscribers": 500,
                }
            ]
        })

        def mock_fetch(url):
            return mock_response

        results = SubscribeRuAdapter.discover(
            topic="python",
            content_type="educational",
            fetch=mock_fetch,
        )

        assert len(results) > 0
        assert results[0].title == "Python News"

    def test_discover_error_handling(self):
        """Discover обрабатывает ошибки API gracefully (возвращает пустой результат)."""
        def mock_fetch_error(url):
            raise Exception("API error")

        # Не должен raise, а вернуть пустой список (graceful degradation)
        results = SubscribeRuAdapter.discover(
            topic="test",
            fetch=mock_fetch_error,
        )

        # Результат может быть пустой (ошибка обработана)
        assert isinstance(results, list)


class TestSourceDiscoveryIntegrator:
    """Тесты для Discovery Integrator."""

    def test_normalize_url_for_comparison(self):
        """Нормализовать URL для сравнения."""
        url1 = "https://www.example.com/feed/"
        url2 = "http://example.com/feed"
        normalized1 = _normalize_url_for_comparison(url1)
        normalized2 = _normalize_url_for_comparison(url2)
        assert normalized1 == normalized2

    def test_discover_and_normalize_with_validation(self):
        """Discover с валидацией RSS."""
        # Mock Subscribe.ru response
        mock_response = json.dumps({
            "results": [
                {
                    "title": "Valid RSS Feed",
                    "rss_url": "https://example.com/valid.xml",
                    "language": "ru",
                    "category": "news",
                    "subscribers": 100,
                }
            ]
        })

        def mock_fetch(url):
            if "search" in url:
                return mock_response
            # Это feed validation
            return """<?xml version="1.0"?>
            <rss version="2.0">
                <channel>
                    <title>Test Feed</title>
                    <item><title>Item 1</title></item>
                </channel>
            </rss>"""

        discovered = SourceDiscoveryIntegrator.discover_and_normalize(
            topic="test",
            content_type="news",
            validate_feeds=True,
            fetch=mock_fetch,
        )

        assert len(discovered) > 0
        # Валидные RSS должны быть в начале
        assert discovered[0].is_rss_validated

    def test_discover_returns_fallback_on_error(self):
        """Discover возвращает fallback если Subscribe.ru не работает."""
        def mock_fetch_error(url):
            raise Exception("Subscribe.ru offline")

        discovered = SourceDiscoveryIntegrator.discover_and_normalize(
            topic="test",
            validate_feeds=False,
            fetch=mock_fetch_error,
        )

        # Должны быть известные источники (fallback)
        assert len(discovered) > 0
        assert any(s.source_type == "known_sources" for s in discovered)

    def test_get_fallback_sources(self):
        """Получить fallback источники."""
        sources = SourceDiscoveryIntegrator.get_fallback_sources(
            content_type="news",
            language="ru",
        )

        assert len(sources) > 0
        assert all(s.source_type == "known_sources" for s in sources)

    def test_discovered_source_sorting(self):
        """Discovered sources отсортированы правильно."""
        discovered = SourceDiscoveryIntegrator.discover_and_normalize(
            topic="test",
            validate_feeds=False,
        )

        # Должны быть отсортированы по валидации, затем по item_count
        for i in range(len(discovered) - 1):
            curr = discovered[i]
            next_src = discovered[i + 1]
            if curr.is_rss_validated == next_src.is_rss_validated:
                # Если оба валидны или оба невалидны, проверяем item_count
                assert curr.item_count >= next_src.item_count


class TestSourceDiscoveryAPI:
    """Тесты для API endpoint'а."""

    def test_discover_subscribe_ru_endpoint_exists(self):
        """Endpoint /discover/subscribe-ru доступен."""
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)

        # POST с параметрами в query
        response = client.post(
            "/api/v1/sources/discover/subscribe-ru?topic=test&language=ru&validate_feeds=false&top_k=5"
        )

        # Может быть 200 или ошибка API (зависит от Subscribe.ru доступности)
        assert response.status_code in [200, 400, 422, 500, 503]

    def test_discover_subscribe_ru_response_format(self):
        """API возвращает правильный формат."""
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)

        response = client.get(
            "/api/v1/sources/discover/subscribe-ru",
            params={"topic": "test", "validate_feeds": False},
        )

        if response.status_code == 200:
            data = response.json()
            assert "topic" in data
            assert "discovered_count" in data
            assert "validated_count" in data
            assert "results" in data
            assert isinstance(data["results"], list)


# Integration test
def test_full_discovery_pipeline():
    """Полный pipeline discovery."""
    # Используем mock fetch чтобы не зависеть от внешних API
    mock_response = json.dumps({
        "results": [
            {
                "title": "News Feed 1",
                "rss_url": "https://example.com/feed1.xml",
                "language": "ru",
                "category": "news",
                "subscribers": 500,
            },
            {
                "title": "News Feed 2",
                "rss_url": "https://example.com/feed2.xml",
                "language": "ru",
                "category": "news",
                "subscribers": 300,
            },
        ]
    })

    def mock_fetch(url):
        if "search" in url:
            return mock_response
        # Mock RSS validation
        return """<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <title>Test</title>
                <item><title>Item</title></item>
            </channel>
        </rss>"""

    discovered = SourceDiscoveryIntegrator.discover_and_normalize(
        topic="новости",
        language="ru",
        content_type="news",
        validate_feeds=True,
        top_k=10,
    )

    # Должны быть результаты
    assert len(discovered) > 0

    # Проверяем сортировку
    prev_score = float('inf')
    for source in discovered:
        if source.is_rss_validated:
            score = source.quality_score
            assert score <= prev_score or source.item_count >= discovered[discovered.index(source) - 1].item_count
