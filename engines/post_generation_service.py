"""Post Generation Service - Sprint 60.4 (refactored).

Единый orchestration layer для генерации постов.

Архитектура:
  Generate → ContentORM (status='generated', draft_text)
  Publish  → ContentORM (status='published', telegram_message_id) + PostHistoryORM
  Failed   → ContentORM (status='failed', publish_error)
"""
import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.content_orm import ContentORM
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
    ) -> Optional[ContentORM]:
        """
        Генерирует пост для канала.
        
        Returns:
            ContentORM со status='generated' или None
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

        if media and media.get("type") == "video":
            video_url = media.get("url")
            logger.info(f"Video found: {media.get('source')}")
        else:
            # Fallback на image_url из content
            image_url = content.get("image_url") or content.get("cover_url")

        # 6. Создать ContentORM со status='generated'
        generated_content = ContentORM(
            id=str(uuid.uuid4()),
            channel_id=channel_id,
            source_url=content.get("source_url", f"generated://{channel_id}/{uuid.uuid4()}"),
            headline=content.get("title", "Generated post"),
            source_text=content.get("summary", ""),
            status="generated",  # ← КЛЮЧЕВОЕ: generated, не published
            draft_text=text,
            image_url=image_url,
            video_url=video_url if hasattr(ContentORM, 'video_url') else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Добавляем video_url если колонка существует
        if hasattr(generated_content, 'video_url'):
            generated_content.video_url = video_url

        self.db.add(generated_content)
        self.db.commit()
        self.db.refresh(generated_content)

        logger.info(
            f"Post generated: id={generated_content.id}, status=generated, "
            f"video={'YES' if video_url else 'NO'}, image={'YES' if image_url else 'NO'}"
        )

        return generated_content

    def get_post_preview(self, content: ContentORM) -> Dict[str, Any]:
        """Получить превью поста для UI."""
        return {
            "id": content.id,
            "status": content.status,
            "text": content.draft_text,
            "image_url": content.image_url,
            "video_url": getattr(content, 'video_url', None),
            "ready_to_publish": bool(content.draft_text and (content.image_url or getattr(content, 'video_url', None))),
        }