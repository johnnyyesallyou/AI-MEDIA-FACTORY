"""Manga Publish Job v5 - Sprint 25.2 (Multi-Channel Publishing).

Pipeline:
  ContentORM (manga_chapter_id)
       ↓
  MangaChapter + MangaTitle (Knowledge Layer)
       ↓
  PublicationImageResolver (policy-driven: cover)
       ↓
  Telegraph page (если publishing_policy.telegraph_page)
       ↓
  Publication (text + image + buttons)
       ↓
  TelegramPlatformPublisher.publish()
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
from core.models.manga_knowledge import MangaTitle, MangaChapter
from engines.channel_profiles import resolve_channel_profile
from engines.telegraph.publisher import TelegraphPublisher
from engines.url_shortener import URLShortener
from engines.formatters import MangaFormatter, FormatContext
from engines.publishing import (
    Publication, PublicationButton,
    PublicationImageResolver, get_publisher_for_channel,
)

logger = logging.getLogger(__name__)

CAPTION_LIMIT = 1024


class MangaPublishJob:
    """Knowledge-aware publisher через Publishing Layer."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self, channel: ChannelORM = None, limit: int = 20) -> Dict[str, Any]:
        self.logger.info(f"MangaPublishJob v5 started (limit={limit})")

        db = SessionLocal()
        try:
            manga_channel = channel or db.query(ChannelORM).filter(
                ChannelORM.name.like("%Манга%"),
                ChannelORM.is_connected == True,
            ).first()

            if not manga_channel:
                return {"status": "failed", "error": "Manga channel not connected"}

                try:
                    mode = (manga_channel.content_profile or {}).get("publishing_mode", "auto")
                except Exception:
                    mode = "auto"
                if mode != "auto":
                    try:
                        moved = db.query(ContentORM).filter(ContentORM.channel_id == manga_channel.id, ContentORM.status == "research").update({"status": "draft"})
                        db.commit()
                    except Exception:
                        moved = 0
                    self.logger.info(f"publishing_mode={mode}: {moved} items -> review queue, auto-publish skipped")
                    return {"status": "ok", "published": 0, "moved_to_review": moved, "publishing_mode": mode}

            profile = resolve_channel_profile(manga_channel)
            publishing_policy = profile.get("publishing_policy", {})
            formatting = profile.get("formatting_profile", {})

            self.logger.info(
                f"Profile: {profile.get('profile_key')} | "
                f"RU required: {publishing_policy.get('require_ru_title')} | "
                f"Telegraph: {publishing_policy.get('telegraph_page')}"
            )

            publisher = get_publisher_for_channel(manga_channel)
            telegraph = TelegraphPublisher() if publishing_policy.get("telegraph_page") else None
            shortener = URLShortener()
            image_resolver = PublicationImageResolver()

            items = db.query(ContentORM).filter(
                ContentORM.status == "research",
                ContentORM.manga_chapter_id != None,
                ContentORM.channel_id == manga_channel.id,
            ).limit(limit * 2).all()

            if not items:
                return {"status": "ok", "published": 0, "message": "No items"}

            grouped = self._group_by_title(db, items)
            self.logger.info(f"Grouped {len(items)} items into {len(grouped)} titles")

            published, failed, skipped_en = 0, 0, 0

            for manga_title_id, title_items in grouped.items():
                if published >= limit:
                    break

                manga_title = db.query(MangaTitle).filter(
                    MangaTitle.id == manga_title_id
                ).first()
                if not manga_title:
                    continue

                # RU-only filter
                title_name = self._get_title_name(manga_title, title_items[0])
                if publishing_policy.get("require_ru_title") and not re.search(r"[а-яА-ЯёЁ]", title_name):
                    self.logger.info(f"Skipping EN-only: {title_name[:50]}")
                    for item in title_items:
                        item.status = "skipped_en"
                    db.commit()
                    skipped_en += 1
                    continue

                max_item = self._get_max_chapter_item(title_items)

                try:
                    result = self._publish_one(
                        db=db,
                        publisher=publisher,
                        telegraph=telegraph,
                        shortener=shortener,
                        image_resolver=image_resolver,
                        manga_title=manga_title,
                        item=max_item,
                        related_items=title_items,
                        channel=manga_channel,
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
            self.logger.info(f"MangaPublishJob v5 finished: {stats}")
            return stats

        except Exception as e:
            db.rollback()
            self.logger.exception(f"MangaPublishJob v5 failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()

    # ---------------- grouping / helpers ----------------

    def _group_by_title(self, db, items: List[ContentORM]) -> Dict[str, List[ContentORM]]:
        grouped: Dict[str, List[ContentORM]] = defaultdict(list)
        for item in items:
            if item.manga_chapter_id:
                chapter = db.query(MangaChapter).filter(
                    MangaChapter.id == item.manga_chapter_id
                ).first()
                if chapter:
                    grouped[chapter.manga_title_id].append(item)
        return dict(grouped)

    def _get_title_name(self, manga_title: MangaTitle, item: ContentORM) -> str:
        meta = self._meta(item)
        lang = meta.get("manga_chapter_language", "ru")
        if manga_title.aliases and lang in manga_title.aliases:
            return manga_title.aliases[lang]
        return manga_title.canonical_title

    def _get_max_chapter_item(self, items: List[ContentORM]) -> ContentORM:
        def num(item):
            m = self._meta(item)
            try:
                return float(m.get("manga_chapter_number", "0"))
            except (ValueError, TypeError):
                return 0
        return max(items, key=num)

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
        manga_title: MangaTitle,
        item: ContentORM,
        related_items: List[ContentORM],
        telegraph_url: Optional[str],
        short_url: str,
        image_url: Optional[str],
        formatting: dict,
        publishing_policy: dict,
    ) -> Publication:
        """Sprint 54: делегируем форматирование в MangaFormatter."""
        formatter = MangaFormatter()
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
        return formatter.format(manga_title, ctx)

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
        manga_title: MangaTitle,
        item: ContentORM,
        related_items: List[ContentORM],
        channel: ChannelORM,
        profile: dict,
    ) -> Dict[str, Any]:
        meta = self._meta(item)
        publishing_policy = profile.get("publishing_policy", {})
        formatting = profile.get("formatting_profile", {})
        title_name = self._get_title_name(manga_title, item)
        chapter_number = meta.get("manga_chapter_number", "?")

        # Telegraph (если разрешено)
        telegraph_url = None
        if telegraph and publishing_policy.get("telegraph_page"):
            try:
                cover_url = manga_title.cover_url
                chapter_url = meta.get("manga_chapter_url", item.source_url)
                preview_pages = None

                # preview pages для ReManga
                if item.source_url and "remanga.org" in item.source_url and manga_title.title_slug:
                    try:
                        from engines.preview_resolver import resolve_preview_pages
                        # Sprint 51: берём slug из URL главы (title_slug может быть MangaDex UUID)
                        chapter_url_for_slug = meta.get("manga_chapter_url") or item.source_url or ""
                        url_slug = None
                        if "remanga.org" in chapter_url_for_slug:
                            m = re.search(r"remanga\.org/manga/([^/]+)", chapter_url_for_slug)
                            if m:
                                url_slug = m.group(1)
                        
                        slug_to_use = url_slug or manga_title.title_slug
                        self.logger.info(f"Preview: using slug={slug_to_use} (url_slug={url_slug}, title_slug={manga_title.title_slug})")
                        preview_pages = resolve_preview_pages(slug_to_use, limit=5)
                        self.logger.info(f"Preview pages fetched: {len(preview_pages) if preview_pages else 0}")
                    except Exception as e:
                        self.logger.warning(f"Preview fetch failed: {e}")
                        preview_pages = None

                result = telegraph.publish_manga_page(
                    title=f"{title_name} — глава {chapter_number}",
                    description=html_lib.unescape(manga_title.description or ""),
                    cover_url=cover_url,
                    source_url=item.source_url,
                    chapter_url=chapter_url,
                    preview_pages=preview_pages,
                )
                telegraph_url = result["url"]
                item.telegraph_url = telegraph_url  # Sprint 51: сохраняем в БД
                self.logger.info(f"Telegraph: {telegraph_url}")
                db.commit()  # Sprint 51: commit чтобы сохранить telegraph_url
            except Exception as e:
                self.logger.warning(f"Telegraph failed: {e}")
                telegraph_url = None

        # Short URL fallback
        chapter_url = meta.get("manga_chapter_url") or item.source_url
        short_url = shortener.shorten(chapter_url)

        # Image через Publishing Layer (policy-driven)
        image_url = image_resolver.resolve(item, channel)
        if not image_url:
            return {"status": "failed", "error": "No image resolved"}

        # Строим Publication
        publication = self._build_publication(
            manga_title=manga_title,
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