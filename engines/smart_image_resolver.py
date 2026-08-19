"""Smart Image Resolver - Sprint 21.

Интеллектуальный резолвер изображений с учётом типа контента.
Приоритеты зависят от channel_profile (news/manga/anime).

Pipeline:
  SourceImageResolver → найдена? → YES → AssetManager
                           ↓ NO
                    AI Generation → ImageValidator → AssetManager
"""
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

from engines.source_image_resolver import SourceImageResolver
from engines.asset.manager import AssetManager
from engines.channel_profiles import resolve_channel_profile

logger = logging.getLogger(__name__)


@dataclass
class SmartImageResult:
    """Результат резолвера с метаданными."""
    asset_id: str
    url: str
    source: str  # og_image, manga_cover, ai_generated
    confidence: float  # 0.0-1.0
    type: str  # source, ai


class SmartImageResolver:
    """
    Умный резолвер изображений с приоритетами по типу контента.
    
    Sprint 21: Smart Image Acquisition
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.source_resolver = SourceImageResolver()
        self.asset_manager = AssetManager()

    def resolve(
        self,
        content_id: str,
        source_url: str,
        channel,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[SmartImageResult]:
        """
        Находит или генерирует изображение для контента.
        
        Args:
            content_id: ID контента в БД
            source_url: URL источника
            channel: ChannelORM объект (для чтения профиля)
            metadata: Дополнительные метаданные (manga_cover_url, etc.)
        
        Returns:
            SmartImageResult если найдено/сгенерировано, иначе None
        """
        metadata = metadata or {}
        profile = resolve_channel_profile(channel)
        
        image_policy = profile.get("image_policy", {})
        preferred = image_policy.get("preferred", "og_image")
        fallback = image_policy.get("fallback", "ai_generated")
        content_type = profile.get("content_type", "news")
        
        self.logger.info(f"Resolving image for {content_type}: preferred={preferred}, fallback={fallback}")
        
        # --- Шаг 1: Приоритетные источники по типу контента ---
        
        # Manga: cover из API
        if content_type == "chapter_release":
            manga_cover = metadata.get("manga_cover_url")
            if manga_cover:
                self.logger.info(f"Trying manga_cover: {manga_cover[:60]}")
                asset_id = self._save_asset(content_id, manga_cover, "manga_cover")
                if asset_id:
                    return SmartImageResult(
                        asset_id=asset_id,
                        url=manga_cover,
                        source="manga_cover",
                        confidence=0.95,
                        type="source"
                    )
            
            # Chapter preview (первая страница)
            preview_pages = metadata.get("preview_pages", [])
            if preview_pages:
                first_page = preview_pages[0]
                self.logger.info(f"Trying chapter_preview: {first_page[:60]}")
                asset_id = self._save_asset(content_id, first_page, "chapter_preview")
                if asset_id:
                    return SmartImageResult(
                        asset_id=asset_id,
                        url=first_page,
                        source="chapter_preview",
                        confidence=0.90,
                        type="source"
                    )
        
        # Anime: key visual из API (если есть)
        if content_type == "anime_news":
            anime_visual = metadata.get("anime_visual_url")
            if anime_visual:
                self.logger.info(f"Trying anime_visual: {anime_visual[:60]}")
                asset_id = self._save_asset(content_id, anime_visual, "anime_visual")
                if asset_id:
                    return SmartImageResult(
                        asset_id=asset_id,
                        url=anime_visual,
                        source="anime_visual",
                        confidence=0.95,
                        type="source"
                    )
        
        # --- Шаг 2: SourceImageResolver (og:image, twitter:image, etc.) ---
        if preferred == "og_image":
            self.logger.info("Trying SourceImageResolver (og:image, etc.)")
            asset_id = self.source_resolver.resolve_and_save(content_id, source_url)
            if asset_id:
                return SmartImageResult(
                    asset_id=asset_id,
                    url=source_url,
                    source="og_image",
                    confidence=0.85,
                    type="source"
                )
        
        # --- Шаг 3: Fallback на AI generation ---
        if fallback == "ai_generated":
            style = image_policy.get("style", "news")
            self.logger.info(f"Fallback: AI generation (style={style})")
            
            # TODO: Интеграция с ImageEngine/ImagePromptEngine
            # Для MVP возвращаем None
            self.logger.warning("AI generation not implemented yet")
        
        # Fallback: none (не генерируем)
        self.logger.warning(f"No image found, fallback={fallback}")
        return None

    def _save_asset(self, content_id: str, url: str, source: str) -> Optional[str]:
        """Сохраняет изображение через AssetManager."""
        try:
            asset = self.asset_manager.save_from_url(
                image_url=url,
                content_id=content_id,
                prompt="",
                model=f"smart_{source}"
            )
            if asset:
                self.logger.info(f"Saved {source}: {url[:60]} -> {asset.public_url}")
                return asset.id
        except Exception as e:
            self.logger.warning(f"Failed to save {source}: {e}")
        return None