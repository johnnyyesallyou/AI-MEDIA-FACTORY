"""Manga Publish Job v3 - публикует с Telegraph страницами."""
import logging
import json
import re
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from engines.telegram.publisher import TelegramPublisher
from engines.telegraph.publisher import TelegraphPublisher
from engines.url_shortener import URLShortener
from engines.source_adapters.remanga_adapter import ReMangaAdapter

logger = logging.getLogger(__name__)

TELEGRAM_CAPTION_LIMIT = 1024


class MangaPublishJob:
    """
    Публикует манга-главы в Telegram с Telegraph страницами.
    
    Sprint 18: Telegraph integration
    """
    
    def run(self, channel: ChannelORM = None, limit: int = 20) -> Dict[str, Any]:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"MangaPublishJob v3 started (limit={limit})")
        
        db = SessionLocal()
        
        try:
            manga_channel = db.query(ChannelORM).filter(
                ChannelORM.name == "Манга — новые главы",
                ChannelORM.is_connected == True
            ).first()
            
            if not manga_channel:
                return {"status": "failed", "error": "Manga channel not connected"}
            
            publisher = TelegramPublisher(manga_channel.bot_token, manga_channel.chat_id)
            telegraph = TelegraphPublisher()
            shortener = URLShortener()
            
            items = db.query(ContentORM).filter(
                ContentORM.status == "research",
                ContentORM.asset_id != None,
                (ContentORM.source_url.like("%remanga.org%") | ContentORM.source_url.like("%mangadex.org%"))
            ).limit(limit * 2).all()
            
            if not items:
                return {"status": "ok", "published": 0, "message": "No items"}
            
            grouped = self._group_by_title(items)
            self.logger.info(f"Grouped {len(items)} items into {len(grouped)} titles")
            
            published = 0
            failed = 0
            published_titles = []
            
            for (source, title_id), title_items in grouped.items():
                if published >= limit:
                    break
                
                max_item = self._get_max_chapter(title_items)
                
                # Sprint 19: RU-only фильтр - пропускаем англоязычные тайтлы
                meta_check = self._parse_metadata(max_item.source_text)
                title_check = meta_check.get("manga_title_name", "") or ""
                if not re.search(r"[а-яА-ЯёЁ]", title_check):
                    self.logger.info(f"Skipping EN-only title: {title_check[:50]}")
                    for rel in title_items:
                        rel.status = "skipped_en"
                    db.commit()
                    continue
                
                try:
                    result = self._publish_manga_post(
                        db=db,
                        publisher=publisher,
                        telegraph=telegraph,
                        shortener=shortener,
                        item=max_item,
                        related_items=title_items
                    )
                    
                    if result.get("status") == "success":
                        published += 1
                        published_titles.append(max_item.headline)
                        
                        for related in title_items:
                            related.status = "published"
                            related.published_at = datetime.utcnow()
                        db.commit()
                        
                        self.logger.info(f"Published: {max_item.headline}")
                    else:
                        failed += 1
                        self.logger.error(f"Failed: {max_item.headline} - {result}")
                
                except Exception as e:
                    failed += 1
                    db.rollback()
                    self.logger.error(f"Error publishing {max_item.headline}: {e}")
            
            stats = {
                "status": "ok",
                "total_processed": len(items),
                "unique_titles": len(grouped),
                "published": published,
                "failed": failed,
                "published_titles": published_titles,
            }
            
            self.logger.info(f"MangaPublishJob v3 finished: {stats}")
            return stats
        
        except Exception as e:
            db.rollback()
            self.logger.exception(f"MangaPublishJob v3 failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()
    
    def _group_by_title(self, items: List[ContentORM]) -> Dict[Tuple[str, str], List[ContentORM]]:
        grouped = {}
        for item in items:
            metadata = self._parse_metadata(item.source_text)
            if not metadata:
                continue
            source = metadata.get("manga_source", "unknown")
            title_id = metadata.get("manga_title_id", "unknown")
            key = (source, title_id)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item)
        return grouped
    
    def _get_max_chapter(self, items: List[ContentORM]) -> ContentORM:
        def get_chapter_num(item):
            metadata = self._parse_metadata(item.source_text)
            if not metadata:
                return 0
            chapter = metadata.get("manga_chapter_number", "0")
            try:
                return float(chapter)
            except (ValueError, TypeError):
                return 0
        return max(items, key=get_chapter_num)
    
    def _parse_metadata(self, source_text: str) -> Dict[str, Any]:
        if not source_text:
            return {}
        try:
            return json.loads(source_text)
        except json.JSONDecodeError:
            return {}
    
    def _format_hashtag(self, tag: str) -> str:
        tag = tag.strip()
        tag = re.sub(r'[^\wа-яА-ЯёЁ\s]', '', tag)
        tag = tag.replace(' ', '_')
        tag = re.sub(r'^[\d_]+', '', tag)
        return f"#{tag}" if tag else ""
    
    def _build_post_text(
        self,
        item: ContentORM,
        related_items: List[ContentORM],
        telegraph_url: Optional[str],
        short_url: str
    ) -> str:
        metadata = self._parse_metadata(item.source_text)
        
        title_name = metadata.get("manga_title_name", item.headline)
        title_name_en = metadata.get("manga_title_name_en", "")
        chapter_number = metadata.get("manga_chapter_number", "?")
        description = metadata.get("manga_description", "")
        # Sprint 19: только русские описания
        if description and not re.search(r"[а-яА-ЯёЁ]", description):
            description = 
        genres = metadata.get("manga_genres", [])
        manga_type = metadata.get("manga_type", "")
        
        chapters = []
        for rel in related_items:
            m = self._parse_metadata(rel.source_text)
            if m.get("manga_chapter_number"):
                chapters.append(m["manga_chapter_number"])
        chapters = sorted(set(chapters), key=lambda x: float(x) if x.replace('.','').isdigit() else 0)
        
        # Hashtags
        hashtags = []
        if manga_type:
            hashtags.append(self._format_hashtag(manga_type))
        for genre in genres[:15]:
            ht = self._format_hashtag(genre)
            if ht:
                hashtags.append(ht)
        
        # Header
        header = f"📚 {title_name}\n"
        if title_name_en and title_name_en != title_name:
            header += f"🌐 {title_name_en}\n"
        header += "\n"
        
        # Chapter line
        if len(chapters) > 1:
            chapter_line = f"📖 Новые главы: {', '.join(chapters)}\n"
        else:
            chapter_line = f"📖 Глава {chapter_number}\n"
        
        # Link (Telegraph URL если есть, иначе short URL)
        link_url = telegraph_url or short_url
        link_line = f"🔗 Читать: {link_url}\n\n"
        
        # Hashtags
        hashtags_text = " ".join(hashtags) if hashtags else "#манга"
        
        # Description (smart truncate)
        description_text = ""
        if description:
            reserved = len(header) + len(chapter_line) + len(link_line) + len(hashtags_text) + 10
            available = TELEGRAM_CAPTION_LIMIT - reserved
            if available > 100:
                description_text = self._smart_truncate(description, available)
                description_text = description_text + "\n\n"
        
        text = header + description_text + chapter_line + link_line + hashtags_text
        
        if len(text) > TELEGRAM_CAPTION_LIMIT:
            excess = len(text) - TELEGRAM_CAPTION_LIMIT + 5
            if description_text:
                description_text = description_text[:max(0, len(description_text) - excess)]
                text = header + description_text + "...\n\n" + chapter_line + link_line + hashtags_text
        
        return text
    
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
    
    def _publish_manga_post(
        self,
        db: SessionLocal,
        publisher: TelegramPublisher,
        telegraph: TelegraphPublisher,
        shortener: URLShortener,
        item: ContentORM,
        related_items: List[ContentORM]
    ) -> Dict[str, Any]:
        metadata = self._parse_metadata(item.source_text)
        
        # Создаём Telegraph страницу
        telegraph_url = None
        try:
            title_name = metadata.get("manga_title_name", item.headline)
            chapter_number = metadata.get("manga_chapter_number", "?")
            page_title = f"{title_name} — глава {chapter_number}"
            
            description = metadata.get("manga_description", "")
            cover_url = metadata.get("manga_cover_url")
            source_url = item.source_url
            chapter_url = metadata.get("manga_chapter_url", item.source_url)
            
            # Sprint 18: ?????? ?????? ????? ??? ReManga
            preview_pages = None
            if source_url and "remanga.org" in source_url:
                try:
                    slug = metadata.get("manga_title_slug")
                    if not slug:
                        # Fallback: ????????? slug ?? URL
                        import re
                        m = re.search(r"remanga\.org/manga/([^/]+)/", source_url)
                        if m:
                            slug = m.group(1)
                    
                    if slug:
                        adapter = ReMangaAdapter()
                        from engines.preview_resolver import resolve_preview_pages
                        preview_pages = resolve_preview_pages(slug, limit=5)
                        if preview_pages:
                            self.logger.info(f"Got {len(preview_pages)} preview pages for {slug}")
                except Exception as e:
                    self.logger.warning(f"Preview fetch failed: {e}")
            
            telegraph_result = telegraph.publish_manga_page(
                title=page_title,
                description=description,
                cover_url=cover_url,
                source_url=source_url,
                chapter_url=chapter_url,
                preview_pages=preview_pages
            )
            
            telegraph_url = telegraph_result["url"]
            self.logger.info(f"Telegraph page created: {telegraph_url}")
        
        except Exception as e:
            self.logger.warning(f"Telegraph failed, using short URL: {e}")
        
        # Short URL (fallback если Telegraph не сработал)
        chapter_url = metadata.get("manga_chapter_url") or item.source_url
        short_url = shortener.shorten(chapter_url)
        
        # Строим текст поста
        text = self._build_post_text(item, related_items, telegraph_url, short_url)
        
        # Image URL
        image_url = item.image_url
        if not image_url:
            image_url = metadata.get("manga_cover_url")
            image_url = re.sub(r'<[^>]+>', '', image_url) if image_url else None
        
        if not image_url:
            return {"status": "failed", "error": "No image URL"}
        
        # Sprint 19: Inline-кнопки (Читать на источнике + Telegraph)
        inline_buttons = []
        if telegraph_url:
            inline_buttons.append({"text": "📖 Читать на Telegraph", "url": telegraph_url})
        if short_url and short_url != telegraph_url:
            inline_buttons.append({"text": "🔗 Источник", "url": short_url})
        
        result = publisher.publish_photo(
            text=text,
            image_url=image_url,
            inline_buttons=inline_buttons
        )
        
        if result.get("status") == "success":
            item.telegram_message_id = str(result.get("message_id", ""))
            db.commit()
        
        return result