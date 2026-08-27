"""News Publish Job - Sprint 32.

Публикует новости через Knowledge Layer + Publishing Layer.

Pipeline:
  ContentORM (news_article_id)
       ↓
  NewsArticle (Knowledge Layer)
       ↓
  PublicationImageResolver (og:image → AI fallback если разрешено)
       ↓
  Telegraph page (опционально, если publishing_policy.telegraph_page)
       ↓
  Publication (text + image + buttons)
       ↓
  PlatformPublisher.publish()
"""
import logging
import json
import re
import html as html_lib
import requests
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from engines.research.models.news_article import NewsArticle
from engines.channel_profiles import resolve_channel_profile
from engines.ab_test_framework import ABTestFramework
from engines.telegraph.publisher import TelegraphPublisher
from engines.url_shortener import URLShortener
from engines.formatters import NewsFormatter, FormatContext
from engines.publishing import (
    Publication, PublicationButton,
    PublicationImageResolver, get_publisher_for_channel,
)

logger = logging.getLogger(__name__)

CAPTION_LIMIT = 1024


class NewsPublishJob:
    """Knowledge-aware publisher для новостей через Publishing Layer."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.ab_framework = ABTestFramework()

    def run(self, channel: ChannelORM = None, limit: int = 20) -> Dict[str, Any]:
        self.logger.info(f"NewsPublishJob started (limit={limit})")

        db = SessionLocal()
        try:
            news_channel = channel or db.query(ChannelORM).filter(
                (ChannelORM.name.like("%Новост%") | ChannelORM.name.like("%News%")),
                ChannelORM.is_connected == True,
            ).first()

            if not news_channel:
                return {"status": "failed", "error": "News channel not connected"}

            profile = resolve_channel_profile(news_channel)
            publishing_policy = profile.get("publishing_policy", {})
            formatting = profile.get("formatting_profile", {})

            self.logger.info(
                f"Profile: {profile.get('profile_key')} | "
                f"Telegraph: {publishing_policy.get('telegraph_page')} | "
                f"Image policy: {profile.get('image_policy', {}).get('preferred')}"
            )

            # A/B test (если есть running тест для этого канала)
            active_test = self.ab_framework.get_active_test(
                channel_id=news_channel.id,
                content_type=profile.get("content_type", "news"),
            )
            if active_test:
                self.logger.info(f"Active A/B test: {active_test.name}")

            publisher = get_publisher_for_channel(news_channel)
            telegraph = TelegraphPublisher() if publishing_policy.get("telegraph_page") else None
            shortener = URLShortener()
            image_resolver = PublicationImageResolver()

            # Берём research items с news_article_id
            items = db.query(ContentORM).filter(
                ContentORM.status == "research",
                ContentORM.news_article_id != None,
                ContentORM.channel_id == news_channel.id,
            ).limit(limit * 2).all()

            if not items:
                return {"status": "ok", "published": 0, "message": "No items"}

            self.logger.info(f"Found {len(items)} news items to publish")

            published, failed, skipped_en = 0, 0, 0

            for item in items:
                if published >= limit:
                    break

                news_article = db.query(NewsArticle).filter(
                    NewsArticle.id == item.news_article_id
                ).first()
                if not news_article:
                    continue

                # RU-only filter (если включён)
                title_name = news_article.title
                if publishing_policy.get("require_ru_title") and not re.search(r"[а-яА-ЯёЁ]", title_name):
                    self.logger.info(f"Skipping EN-only: {title_name[:50]}")
                    item.status = "skipped_en"
                    db.commit()
                    skipped_en += 1
                    continue

                # A/B: назначение варианта
                variant = None
                if active_test:
                    variant = self.ab_framework.assign_variant(active_test, item.id)
                    self.ab_framework.record_exposure(str(active_test.id), str(item.id), variant["id"])
                    self.logger.info(f"Post assigned to variant: {variant.get('name')}")

                try:
                    result = self._publish_one(
                        db=db,
                        publisher=publisher,
                        telegraph=telegraph,
                        shortener=shortener,
                        image_resolver=image_resolver,
                        news_article=news_article,
                        item=item,
                        channel=news_channel,
                        profile=profile,
                        variant=variant,
                    )

                    if result.get("status") == "success":
                        published += 1
                        item.status = "published"
                        item.published_at = datetime.utcnow()
                        db.commit()
                        self.logger.info(f"Published: {title_name[:60]}")
                    else:
                        failed += 1
                        self.logger.error(f"Failed: {title_name[:50]} - {result.get('error')}")
                except Exception as e:
                    failed += 1
                    db.rollback()
                    self.logger.exception(f"Error publishing {title_name[:50]}: {e}")

            stats = {
                "status": "ok",
                "total_processed": len(items),
                "published": published,
                "failed": failed,
                "skipped_en": skipped_en,
            }
            self.logger.info(f"NewsPublishJob finished: {stats}")
            return stats

        except Exception as e:
            db.rollback()
            self.logger.exception(f"NewsPublishJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()


    def _translate_to_russian(self, text: str, max_length: int = 500) -> str:
        """Sprint 52C: переводит EN текст на русский через LLM (gemma2:9b)."""
        if not text or not text.strip():
            return ""
        
        # Если уже содержит кириллицу — возвращаем как есть
        import re
        if re.search(r"[а-яА-ЯёЁ]", text):
            return text
        
        try:
            import requests
            prompt = f"""Переведи следующий текст на русский язык. Сохрани стиль и факты. Только перевод, без пояснений и комментариев.

Текст: {text[:800]}

Перевод на русском:"""
            
            response = requests.post(
                "http://host.docker.internal:11434/api/generate",
                json={
                    "model": "gemma2:9b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 600}
                },
                timeout=120,
            )
            
            if response.status_code == 200:
                translated = response.json().get("response", "").strip()
                if translated:
                    self.logger.info(f"Translated: {text[:50]}... -> {translated[:50]}...")
                    return translated[:max_length]
        except Exception as e:
            self.logger.warning(f"Translation failed: {e}")
        
        return ""  # Не возвращаем EN текст

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

    def _build_publication(
        self,
        news_article: NewsArticle,
        item: ContentORM,
        telegraph_url: Optional[str],
        short_url: str,
        image_url: Optional[str],
        formatting: dict,
        publishing_policy: dict,
    ) -> Publication:
        """Sprint 54: делегируем форматирование в NewsFormatter."""
        formatter = NewsFormatter()
        ctx = FormatContext(
            item=item,
            meta=self._meta(item),
            related_items=[],
            telegraph_url=telegraph_url,
            short_url=short_url,
            image_url=image_url,
            formatting=formatting,
            publishing_policy=publishing_policy,
        )
        return formatter.format(news_article, ctx)

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

    def _publish_one(
        self,
        db,
        publisher,
        telegraph,
        shortener,
        image_resolver,
        news_article: NewsArticle,
        item: ContentORM,
        channel: ChannelORM,
        profile: dict,
        variant: dict = None,
    ) -> Dict[str, Any]:
        publishing_policy = profile.get("publishing_policy", {})
        formatting = dict(profile.get("formatting_profile", {}))
        
        # A/B: применяем overrides из варианта
        if variant and variant.get("config"):
            cfg = variant["config"]
            for key in ("emoji_header", "include_description", "max_hashtags", "unescape_html"):
                if key in cfg:
                    formatting[key] = cfg[key]
        
        title_name = news_article.title

        # Telegraph (если разрешено)
        telegraph_url = None
        if telegraph and publishing_policy.get("telegraph_page"):
            try:
                result = telegraph.publish_manga_page(
                    title=title_name,
                    description=news_article.summary or "",
                    cover_url=news_article.og_image_url,
                    source_url=news_article.canonical_url,
                    chapter_url=news_article.canonical_url,
                    preview_pages=None,
                )
                telegraph_url = result["url"]
                self.logger.info(f"Telegraph: {telegraph_url}")
            except Exception as e:
                self.logger.warning(f"Telegraph failed: {e}")

        # Short URL
        short_url = ""
        try:
            short_url = shortener.shorten(news_article.canonical_url)
        except Exception:
            short_url = news_article.canonical_url

        # Image через Publishing Layer (с ВАЛИДАЦИЕЙ)
        image_url = image_resolver.resolve(item, channel)
        if not image_url:
            # Fallback: og_image из NewsArticle
            image_url = news_article.og_image_url
        
        # ВАЛИДАЦИЯ: проверяем что URL отдаёт реальное изображение
        if image_url and not image_resolver.is_valid_image_url(image_url):
            self.logger.warning(f"Invalid image URL (wrong content-type): {image_url[:80]}")
            image_url = None  # Сбрасываем, будем публиковать как text
        
        # A/B: вариант может отключать картинку
        if variant and variant.get("config", {}).get("include_image") is False:
            image_url = None
            image_bytes = None

        # Для news можно публиковать без картинки (как text post)
        if not image_url:
            self.logger.info(f"Publishing as text post (no valid image)")

        publication = self._build_publication(
            news_article=news_article,
            item=item,
            telegraph_url=telegraph_url,
            short_url=short_url,
            image_url=image_url,
            formatting=formatting,
            publishing_policy=publishing_policy,
        )
        
        # Скачиваем картинку (Habr URLs без расширения ломают sendPhoto)
        image_bytes = None
        if image_url:
            try:
                headers = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}
                r = requests.get(image_url, headers=headers, timeout=15)
                if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
                    image_bytes = r.content
                    self.logger.debug(f"Downloaded image: {len(image_bytes)} bytes from {image_url[:60]}")
                else:
                    self.logger.warning(f"Image download failed: status={r.status_code}, ct={r.headers.get('content-type')}")
            except Exception as e:
                self.logger.warning(f"Image download error: {e}")

        # Сохраняем bytes в metadata для передачи в publisher
        if image_bytes:
            publication.metadata["_image_bytes"] = image_bytes

        result = publisher.publish(publication)

        if result.get("status") == "success":
            item.telegram_message_id = str(result.get("message_id", ""))
            db.commit()

        return result