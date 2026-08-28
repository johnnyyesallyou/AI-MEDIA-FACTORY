"""Post Generation Service - Sprint 60.

Единый orchestration layer для генерации постов.
Собирает: Channel + Profile + Context + Content → Publication

Архитектура:
  Channel
     ↓
  ChannelContext (learnings + history)
     ↓
  PostGenerationService
     ├── PromptBuilder (промпт с контекстом)
     ├── LLMGenerator (текст)
     ├── VideoManager (видео/картинка)
     └── Formatter (формат)
     ↓
  Publication → Publisher → PostHistory
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.post_history_orm import PostHistoryORM
from engines.content_context import ChannelContext
from engines.prompt_builder import PromptBuilder
from engines.llm_generator import LLMGenerator
from engines.video_manager.engine import VideoManager

logger = logging.getLogger(__name__)


class PostGenerationService:
    """Генерация постов с учётом контекста канала."""

    def __init__(self, db_session: SessionLocal):
        self.db = db_session
        self.llm = LLMGenerator()
        self.video_manager = VideoManager()

    async def generate_post(
        self,
        channel_id: str,
        content: Dict[str, Any],
        content_type: str = "news"
    ) -> Optional[PostHistoryORM]:
        """
        Генерирует пост для канала.

        Args:
            channel_id: ID канала
            content: Данные контента (например, article для news)
            content_type: Тип контента (news/manga/anime)

        Returns:
            PostHistoryORM или None
        """
        # 1. Получить канал
        channel = self.db.query(ChannelORM).filter_by(id=channel_id).first()
        if not channel:
            logger.error(f"Channel {channel_id} not found")
            return None

        # 2. Создать контекст
        context = ChannelContext(channel, self.db)
        builder = PromptBuilder(context)

        # 3. Построить промпт
        if content_type == "news":
            prompt = builder.build_news_prompt(content)
        elif content_type == "manga":
            prompt = builder.build_manga_prompt(
                content, 
                content.get("chapter_number", "?")
            )
        else:
            prompt = builder.build_generic_prompt(content, content_type)

        logger.info(f"Built prompt ({len(prompt)} chars) for channel={channel.name}")

        # 4. Сгенерировать текст
        text = self.llm.generate(prompt, max_tokens=500)
        if not text:
            logger.error("LLM generation failed")
            return None

        logger.info(f"Generated text ({len(text)} chars)")

        # 5. Получить медиа (видео или картинка)
        media = self.video_manager.get_video(
            content.get("title", content.get("topic", "general")),
            timeout=20
        )

        video_url = None
        image_url = None
        media_type = "none"

        if media and media.get("type") == "video":
            video_url = media.get("url")
            media_type = "video"
            logger.info(f"Video found: {media.get('source')}")
        else:
            # Fallback на image_url из content
            image_url = content.get("image_url") or content.get("cover_url")
            if image_url:
                media_type = "image"

        # 6. Сохранить в PostHistory
        post = PostHistoryORM(
            channel_id=channel_id,
            content_id=content.get("content_id"),
            platform=channel.platform,
            text=text,
            image_url=image_url,
            video_url=video_url,
            media_type=media_type,
            message_id=None,  # Будет заполнен после publish
            posted_at=datetime.utcnow(),
        )

        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)

        logger.info(
            f"Post generated: id={post.id}, media={media_type}, "
            f"channel={channel.name}, text_len={len(text)}"
        )

        return post

    def get_post_preview(self, post: PostHistoryORM) -> Dict[str, Any]:
        """Получить превью поста для UI."""
        return {
            "id": post.id,
            "text": post.text,
            "media_type": post.media_type,
            "image_url": post.image_url,
            "video_url": post.video_url,
            "ready_to_publish": bool(post.text and (post.image_url or post.video_url)),
        }