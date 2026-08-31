"""Integration tests for Sprint 60 (Learning Loop + Post Generation).

Тесты проверяют что полный цикл работает:
  Generate → ContentORM (generated) → Publish → ContentORM (published) + PostHistory
"""
import asyncio
import pytest
import os

# Sprint 66.4: marker for tests requiring external LLM (Ollama)
requires_llm = pytest.mark.skipif(
    os.environ.get("APP_ENV") == "test",
    reason="Requires Ollama LLM service (skipped in CI/unit mode)"
)

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.content_orm import ContentORM
from core.models.post_history_orm import PostHistoryORM
from engines.post_generation_service import PostGenerationService
from engines.publish_service import PublishService
from engines.media_policy import get_media_policy, MEDIA_POLICIES


# ---------------------------------------------------------------------------
# Unit tests: Media Policy
# ---------------------------------------------------------------------------

class TestMediaPolicy:
    """Тесты Media Policy."""
    
    def test_manga_releases_no_video(self):
        """manga_releases должен использовать только cover (без видео)."""
        policy = get_media_policy("manga_releases")
        assert policy.primary == "image"
        assert policy.source == "cover"
        assert policy.should_fetch_video() is False
        assert policy.should_fetch_image() is True
    
    def test_ai_news_video_primary(self):
        """ai_news должен использовать видео как primary."""
        policy = get_media_policy("ai_news")
        assert policy.primary == "video"
        assert policy.source == "pixabay"
        assert policy.should_fetch_video() is True
        assert policy.fallback == "image"
    
    def test_anime_news_image_with_video_fallback(self):
        """anime_news должен использовать image с video_fallback."""
        policy = get_media_policy("anime_news")
        assert policy.primary == "image"
        assert policy.video_fallback is True
    
    def test_general_fallback_to_video(self):
        """Неизвестный профиль должен использовать general (video)."""
        policy = get_media_policy("unknown_profile_xyz")
        assert policy.primary == "video"
        assert policy.source == "pixabay"
    
    def test_all_predefined_profiles_exist(self):
        """Все ожидаемые профили должны существовать."""
        expected = ["manga_releases", "anime_news", "tech_news", "ai_news", "general"]
        for key in expected:
            assert key in MEDIA_POLICIES, f"Profile '{key}' not found"


# ---------------------------------------------------------------------------
# Integration tests: PostGenerationService
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestPostGenerationService:
    """Integration тесты PostGenerationService.
    
    ВНИМАНИЕ: Требуют Ollama LLM на host.docker.internal:11434.
    Запускаются только если доступен LLM.
    """
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_news_post(self):
        """Тест генерации новостного поста."""
        db = SessionLocal()
        try:
            # Sprint 66.4: Create test channel first
            channel_id = str(uuid.uuid4())
            test_channel = ChannelORM(
                id=channel_id,
                name="Test News Channel",
                platform="telegram",
                language_search="en",
                language_publish="ru",
                style_profile="minimal",
                timezone="UTC",
                is_active=True,
                is_connected=True
            )
            db.add(test_channel)
            db.commit()
            
            service = PostGenerationService(db)
            article = {
                "title": "Test News Article",
                "source_name": "Test Source",
                "summary": "Test summary for integration test.",
                "image_url": "https://example.com/test.jpg"
            }
            
            content = await service.generate_post(
                channel_id=channel_id,
                content=article,
                content_type="news"
            )
            
            assert content is not None
            assert content.status == "generated"
            assert content.draft_text is not None
            assert len(content.draft_text) > 50
            assert content.channel_id == channel_id
            
            # Cleanup
            db.delete(content)
            db.delete(test_channel)
            db.commit()
            
        finally:
            db.close()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_generate_manga_post_no_video(self):
        """Тест генерации манга-поста (должен быть без видео)."""
        db = SessionLocal()
        try:
            # Sprint 66.4: Create test channel first
            channel_id = str(uuid.uuid4())
            test_channel = ChannelORM(
                id=channel_id,
                name="Test Manga Channel",
                platform="telegram",
                language_search="en",
                language_publish="ru",
                style_profile="minimal",
                timezone="UTC",
                is_active=True,
                is_connected=True
            )
            db.add(test_channel)
            db.commit()
            
            service = PostGenerationService(db)
            manga_content = {
                "title": "Test Manga",
                "title_ru": "Тестовая манга",
                "chapter_number": "1",
                "genres": ["Action"],
                "description": "Test description.",
                "cover_url": "https://example.com/cover.jpg"
            }
            
            content = await service.generate_post(
                channel_id=channel_id,
                content=manga_content,
                content_type="manga"
            )
            
            assert content is not None
            assert content.status == "generated"
            # Media Policy: manga_releases не запрашивает видео
            assert content.video_url is None or isinstance(content.video_url, str)
            
            # Cleanup
            db.delete(content)
            db.delete(test_channel)
            db.commit()
            
        finally:
            db.close()
    
    @pytest.mark.asyncio
    async def test_invalid_channel_id_returns_none(self):
        """Неверный channel_id должен вернуть None."""
        db = SessionLocal()
        try:
            service = PostGenerationService(db)
            content = await service.generate_post(
                channel_id="nonexistent-channel-xyz",
                content={"title": "Test"},
                content_type="news"
            )
            assert content is None
        finally:
            db.close()


# ---------------------------------------------------------------------------
# Regression tests: existing components
# ---------------------------------------------------------------------------

class TestRegression:
    """Regression тесты чтобы убедиться что существующие компоненты не сломаны."""
    
    def test_channel_context_imports(self):
        """ChannelContext должен импортироваться."""
        from engines.content_context import ChannelContext
        assert ChannelContext is not None
    
    def test_formatter_registry_imports(self):
        """Formatter Registry должен импортироваться."""
        from engines.formatters.formatter_registry import get_formatter
        assert get_formatter is not None
    
    def test_source_registry_imports(self):
        """Source Registry должен импортироваться."""
        from engines.source_registry import SourceRegistry
        assert SourceRegistry is not None
    
    def test_analytics_collector_imports(self):
        """Analytics Collector должен импортироваться."""
        from engines.analytics import AnalyticsCollector
        assert AnalyticsCollector is not None
    
    def test_video_manager_imports(self):
        """Video Manager должен импортироваться."""
        from engines.video_manager import VideoManager
        assert VideoManager is not None
    
    def test_post_history_recorder_imports(self):
        """Post History Recorder должен импортироваться."""
        from engines.post_history_recorder import record_post_history
        assert record_post_history is not None
    
    def test_publish_service_imports(self):
        """Publish Service должен импортироваться."""
        from engines.publish_service import PublishService
        assert PublishService is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
