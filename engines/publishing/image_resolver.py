"""Publication Image Resolver v3 - Sprint 27.

Валидация с Referer (MangaDex требует).
"""
import json
import logging
import requests
from typing import List, Optional

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.manga_knowledge import MangaTitle, MangaChapter
from engines.channel_profiles import resolve_channel_profile
from engines.source_image_resolver import SourceImageResolver
from .image_acquisition import ImageAcquisitionPolicy

logger = logging.getLogger(__name__)

UA = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}


class PublicationImageResolver:
    """Policy-driven выбор изображения с валидацией."""

    VALIDATE_TIMEOUT = 8

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.source_resolver = SourceImageResolver()
        self.acquisition = ImageAcquisitionPolicy()

    def resolve(self, content: ContentORM, channel) -> Optional[str]:
        profile = resolve_channel_profile(channel)
        content_type = profile.get("content_type", "news")
        image_policy = profile.get("image_policy", {})

        if content_type == "chapter_release":
            candidates = self._manga_candidates(content)
        elif content_type == "anime_release":
            candidates = self._anime_candidates(content)
        elif content_type == "news":
            candidates = self._news_candidates(content, image_policy)
        else:
            candidates = self._news_candidates(content, image_policy)

        real_url = None
        for url in candidates:
            if self.is_valid_image_url(url):
                real_url = url
                break
            elif url:
                self.logger.debug(f"Invalid image candidate: {url[:60]}")

        # Policy-driven acquisition (AI fallback только для news если разрешено)
        result = self.acquisition.acquire(
            content=content,
            real_url=real_url,
            profile=profile,
        )
        return result.url

    def _manga_candidates(self, content: ContentORM) -> List[Optional[str]]:
        candidates: List[Optional[str]] = []

        db = SessionLocal()
        try:
            if content.manga_chapter_id:
                chapter = db.query(MangaChapter).filter(
                    MangaChapter.id == content.manga_chapter_id
                ).first()
                if chapter:
                    title = db.query(MangaTitle).filter(
                        MangaTitle.id == chapter.manga_title_id
                    ).first()
                    if title and title.cover_url:
                        candidates.append(title.cover_url)
        finally:
            db.close()

        meta = self._meta(content)
        candidates.append(meta.get("manga_cover_url"))
        candidates.append(content.image_url)
        return candidates

    def _anime_candidates(self, content: ContentORM) -> List[Optional[str]]:
        """AnimeEpisode -> AnimeTitle -> cover (Knowledge Layer)."""
        from core.models.anime_knowledge import AnimeTitle, AnimeEpisode
        
        candidates: List[Optional[str]] = []

        db = SessionLocal()
        try:
            if content.anime_episode_id:
                episode = db.query(AnimeEpisode).filter(
                    AnimeEpisode.id == content.anime_episode_id
                ).first()
                if episode:
                    title = db.query(AnimeTitle).filter(
                        AnimeTitle.id == episode.anime_title_id
                    ).first()
                    if title and title.cover_url:
                        candidates.append(title.cover_url)
        finally:
            db.close()

        meta = self._meta(content)
        candidates.append(meta.get("anime_cover_url"))
        candidates.append(content.image_url)
        return candidates

    def _news_candidates(self, content: ContentORM, image_policy: dict) -> List[Optional[str]]:
        candidates: List[Optional[str]] = [content.image_url]

        if not content.image_url:
            try:
                asset_id = self.source_resolver.resolve_and_save(content.id, content.source_url)
                if asset_id:
                    db = SessionLocal()
                    try:
                        fresh = db.query(ContentORM).filter(ContentORM.id == content.id).first()
                        if fresh:
                            candidates.append(fresh.image_url)
                    finally:
                        db.close()
            except Exception as e:
                self.logger.warning(f"SourceImageResolver failed: {e}")

        return candidates

    def is_valid_image_url(self, url: Optional[str]) -> bool:
        """
        Проверяет URL. Пробует:
        1. Без Referer (быстрый путь)
        2. С Referer (fallback для MangaDex и других strict CDN)
        """
        if not url or url.startswith("data:"):
            return False
        try:
            # Попытка 1: без Referer
            r = requests.get(url, headers=UA, timeout=self.VALIDATE_TIMEOUT, stream=True)
            if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
                r.close()
                return True
            r.close()
        except Exception:
            pass

        # Попытка 2: с Referer (MangaDex и некоторые CDN требуют)
        try:
            headers_with_referer = {**UA, "Referer": "https://mangadex.org/"}
            r = requests.get(url, headers=headers_with_referer, timeout=self.VALIDATE_TIMEOUT, stream=True)
            if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
                r.close()
                return True
            r.close()
        except Exception:
            pass

        return False

    def _meta(self, content: ContentORM) -> dict:
        try:
            return json.loads(content.source_text or "{}")
        except Exception:
            return {}