"""Anime Publish Job - Sprint 31.5.

Публикует anime через Knowledge Layer + Publishing Layer.

Pipeline:
  ContentORM (anime_episode_id)
       ↓
  AnimeEpisode + AnimeTitle (Knowledge Layer)
       ↓
  PublicationImageResolver (policy-driven: cover)
       ↓
  Telegraph page (если publishing_policy.telegraph_page)
       ↓
  Publication (text + image + buttons)
       ↓
  PlatformPublisher.publish()
"""
import logging
import json
import re
import html as html_lib
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from core.models.anime_knowledge import AnimeTitle, AnimeEpisode
from engines.channel_profiles import resolve_channel_profile
from engines.telegraph.publisher import TelegraphPublisher
from engines.url_shortener import URLShortener
from engines.formatters import AnimeFormatter, FormatContext
from engines.publishing import (
    Publication, PublicationButton,
    PublicationImageResolver, get_publisher_for_channel,
)

logger = logging.getLogger(__name__)

CAPTION_LIMIT = 1024


class AnimePublishJob:
    def _translate_to_russian(self, text: str, max_length: int = 500) -> str:
        """Sprint 51: переводит EN описание на русский через LLM (gemma2:9b)."""
        if not text or not text.strip():
            return ""
        
        # Если уже содержит кириллицу — возвращаем как есть
        import re
        if re.search(r"[а-яА-ЯёЁ]", text):
            return text
        
        try:
            import requests
            prompt = f"""Переведи описание аниме на русский язык. Сохрани стиль и эмоции. Только перевод, без пояснений.

Описание: {text[:800]}

Перевод на русском:"""
            
            response = requests.post(
                "http://host.docker.internal:11434/api/generate",
                json={
                    "model": "gemma2:9b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3}
                },
                timeout=60,
            )
            
            if response.status_code == 200:
                translated = response.json().get("response", "").strip()
                if translated:
                    return translated[:max_length]
        except Exception as e:
            self.logger.warning(f"Translation failed: {e}")
        
        return ""  # Не возвращаем EN текст, пусть будет пустой
    

    """Knowledge-aware publisher для anime через Publishing Layer."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self, channel: ChannelORM = None, limit: int = 20) -> Dict[str, Any]:
        self.logger.info(f"AnimePublishJob started (limit={limit})")

        db = SessionLocal()
        try:
            anime_channel = channel or db.query(ChannelORM).filter(
                ChannelORM.name.like("%Аниме%") | ChannelORM.name.like("%Anime%"),
                ChannelORM.is_connected == True,
            ).first()

            if not anime_channel:
                return {"status": "failed", "error": "Anime channel not connected"}

            profile = resolve_channel_profile(anime_channel)
            publishing_policy = profile.get("publishing_policy", {})
            formatting = profile.get("formatting_profile", {})

            self.logger.info(
                f"Profile: {profile.get('profile_key')} | "
                f"RU required: {publishing_policy.get('require_ru_title')} | "
                f"Telegraph: {publishing_policy.get('telegraph_page')}"
            )

            publisher = get_publisher_for_channel(anime_channel)
            telegraph = TelegraphPublisher() if publishing_policy.get("telegraph_page") else None
            shortener = URLShortener()
            image_resolver = PublicationImageResolver()

            items = db.query(ContentORM).filter(
                ContentORM.status == "research",
                ContentORM.anime_episode_id != None,
                ContentORM.channel_id == anime_channel.id,
            ).limit(limit * 2).all()

            if not items:
                return {"status": "ok", "published": 0, "message": "No items"}

            grouped = self._group_by_title(db, items)
            self.logger.info(f"Grouped {len(items)} items into {len(grouped)} titles")

            published, failed, skipped_en = 0, 0, 0

            for anime_title_id, title_items in grouped.items():
                if published >= limit:
                    break

                anime_title = db.query(AnimeTitle).filter(
                    AnimeTitle.id == anime_title_id
                ).first()
                if not anime_title:
                    continue

                # RU-only filter (если включён)
                title_name = self._get_title_name(anime_title, title_items[0])
                if publishing_policy.get("require_ru_title") and not re.search(r"[а-яА-ЯёЁ]", title_name):
                    self.logger.info(f"Skipping EN-only: {title_name[:50]}")
                    for item in title_items:
                        item.status = "skipped_en"
                    db.commit()
                    skipped_en += 1
                    continue

                max_item = title_items[0]  # Для anime пока берём первый (все episode=1)

                try:
                    result = self._publish_one(
                        db=db,
                        publisher=publisher,
                        telegraph=telegraph,
                        shortener=shortener,
                        image_resolver=image_resolver,
                        anime_title=anime_title,
                        item=max_item,
                        related_items=title_items,
                        channel=anime_channel,
                        profile=profile,
                    )

                    if result.get("status") == "success":
                        published += 1
                        for related in title_items:
                            related.status = "published"
                            related.published_at = datetime.utcnow()
                        db.commit()
                        self.logger.info(f"Published: {title_name}")
                    else:
                        failed += 1
                        self.logger.error(f"Failed: {title_name} - {result.get('error')}")
                except Exception as e:
                    failed += 1
                    db.rollback()
                    self.logger.exception(f"Error publishing {title_name}: {e}")

            stats = {
                "status": "ok",
                "total_processed": len(items),
                "unique_titles": len(grouped),
                "published": published,
                "failed": failed,
                "skipped_en": skipped_en,
            }
            self.logger.info(f"AnimePublishJob finished: {stats}")
            return stats

        except Exception as e:
            db.rollback()
            self.logger.exception(f"AnimePublishJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()

    # ---------------- grouping / helpers ----------------

    def _group_by_title(self, db, items: List[ContentORM]) -> Dict[str, List[ContentORM]]:
        grouped: Dict[str, List[ContentORM]] = defaultdict(list)
        for item in items:
            if item.anime_episode_id:
                episode = db.query(AnimeEpisode).filter(
                    AnimeEpisode.id == item.anime_episode_id
                ).first()
                if episode:
                    grouped[episode.anime_title_id].append(item)
        return dict(grouped)

    def _get_title_name(self, anime_title: AnimeTitle, item: ContentORM) -> str:
        meta = self._meta(item)
        # Приоритет: romaji > english > native > canonical
        if anime_title.aliases:
            if "romaji" in anime_title.aliases:
                return anime_title.aliases["romaji"]
            if "en" in anime_title.aliases:
                return anime_title.aliases["en"]
            if "ja" in anime_title.aliases:
                return anime_title.aliases["ja"]
        return anime_title.canonical_title

    def _meta(self, item: ContentORM) -> dict:
        try:
            return json.loads(item.source_text or "{}")
        except Exception:
            return {}

    def _format_hashtag(self, tag: str) -> str:
        tag = html_lib.unescape(tag.strip())
        tag = re.sub(r'[^\wа-яА-ЯёЁ\s]', '', tag)
        tag = tag.replace(' ', '_')
        tag = re.sub(r'^[\d_]+', '', tag)
        return f"#{tag}" if tag else ""

    # ---------------- publication assembly ----------------

    def _build_publication(
        self,
        anime_title: AnimeTitle,
        item: ContentORM,
        related_items: List[ContentORM],
        telegraph_url: Optional[str],
        short_url: str,
        image_url: Optional[str],
        formatting: dict,
        publishing_policy: dict,
    ) -> Publication:
        """Sprint 54: делегируем форматирование в AnimeFormatter."""
        formatter = AnimeFormatter()
        ctx = FormatContext(
            item=item,
            meta=self._meta(item),
            related_items=related_items,
            telegraph_url=telegraph_url,
            short_url=short_url,
            image_url=image_url,
            formatting=formatting,
            publishing_policy=publishing_policy,
        )
        return formatter.format(anime_title, ctx)

    def _smart_truncate(self, text: str, max_length: int) -> str:
        if len(text) <= max_length:
            return text
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length // 2:
            truncated = truncated[:last_space]
        last_punct = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
        if last_punct > max_length // 2:
            truncated = truncated[:last_punct + 1]
        return truncated

    # ---------------- per-item publish ----------------

    def _publish_one(
        self,
        db: SessionLocal,
        publisher,
        telegraph,
        shortener,
        image_resolver,
        anime_title: AnimeTitle,
        item: ContentORM,
        related_items: List[ContentORM],
        channel: ChannelORM,
        profile: dict,
    ) -> Dict[str, Any]:
        meta = self._meta(item)
        publishing_policy = profile.get("publishing_policy", {})
        formatting = profile.get("formatting_profile", {})
        title_name = self._get_title_name(anime_title, item)

        # Telegraph (если разрешено)
        telegraph_url = None
        if telegraph and publishing_policy.get("telegraph_page"):
            try:
                cover_url = anime_title.cover_url
                description = anime_title.description or ""

                result = telegraph.publish_manga_page(
                    title=f"{title_name}",
                    description=description,
                    cover_url=cover_url,
                    source_url=f"https://anilist.co/anime/{anime_title.external_ids.get('anilist', '')}",
                    chapter_url="",
                    preview_pages=None,
                )
                telegraph_url = result["url"]
                self.logger.info(f"Telegraph: {telegraph_url}")
            except Exception as e:
                self.logger.warning(f"Telegraph failed: {e}")

        # Short URL (AniList link)
        anilist_url = f"https://anilist.co/anime/{anime_title.external_ids.get('anilist', '')}"
        short_url = shortener.shorten(anilist_url) if anilist_url else ""

        # Image через Publishing Layer (policy-driven)
        image_url = image_resolver.resolve(item, channel)
        if not image_url:
            # Fallback: cover из AnimeTitle
            image_url = anime_title.cover_url

        if not image_url:
            return {"status": "failed", "error": "No image resolved"}

        # Строим Publication
        publication = self._build_publication(
            anime_title=anime_title,
            item=item,
            related_items=related_items,
            telegraph_url=telegraph_url,
            short_url=short_url,
            image_url=image_url,
            formatting=formatting,
            publishing_policy=publishing_policy,
        )

        # Отправляем через Publishing Layer
        result = publisher.publish(publication)

        if result.get("status") == "success":
            item.telegram_message_id = str(result.get("message_id", ""))

            # Sprint 58: record publication in post_history for Learning Loop
            try:
                from engines.post_history_recorder import record_post_history
                _channel = locals().get("channel") or locals().get("manga_channel") or locals().get("anime_channel") or locals().get("news_channel")
                record_post_history(
                    db=db,
                    channel=_channel,
                    item=item,
                    publication=publication,
                    result=result,
                )
            except Exception as history_e:
                self.logger.warning(f"Failed to record post_history: {history_e}")
            db.commit()

        return result