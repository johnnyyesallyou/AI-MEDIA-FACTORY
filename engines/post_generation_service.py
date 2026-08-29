"""Post Generation Service - Sprint 60.5 (с Media Policy).

Архитектура:
  Channel Profile
    ↓
  Media Policy (определяет video/image/none)
    ↓
  Generate (LLM + VideoManager)
    ↓
  ContentORM (status='generated')
    ↓
  Publish
    ↓
  ContentORM (status='published') + PostHistoryORM
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
from engines.media_policy import get_media_policy

logger = logging.getLogger(__name__)


class PostGenerationService:
    """Генерация постов с учётом контекста канала и media policy."""

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
        Генерирует пост для канала с учётом Media Policy.
        
        Returns:
            ContentORM со status='generated' или None
        """
        # 1. Получить канал
        channel = self.db.query(ChannelORM).filter_by(id=channel_id).first()
        if not channel:
            logger.error(f"Channel {channel_id} not found")
            return None

        # 2. Получить Media Policy из профиля
        content_profile = channel.content_profile or {}
        profile_key = content_profile.get("profile_key", "general")
        media_policy = get_media_policy(profile_key)
        
        logger.info(f"Media policy for {channel.name}: primary={media_policy.primary}, source={media_policy.source}")

        # 3. Создать контекст
        context = ChannelContext(channel, self.db)
        builder = PromptBuilder(context)

        # 4. Построить промпт
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

        # 5. Сгенерировать текст
        text = self.llm.generate(prompt, max_tokens=500)
        if not text:
            logger.error("LLM generation failed")
            return None

        logger.info(f"Generated text ({len(text)} chars)")

        # 6. Получить медиа согласно Media Policy
        video_url = None
        image_url = None

        if media_policy.should_fetch_video():
            # Пробуем получить видео
            topic = content.get("title", content.get("topic", "general"))
            media = self.video_manager.get_video(topic, timeout=20)
            
            if media and media.get("type") == "video":
                video_url = media.get("url")
                logger.info(f"Video found via {media.get('source')}")
            elif media_policy.fallback == "image":
                # Fallback на картинку
                image_url = content.get("image_url") or content.get("cover_url")
                logger.info(f"Video not found, using image fallback")
        
        elif media_policy.should_fetch_image():
            # Только картинка
            image_url = content.get("image_url") or content.get("cover_url")
            logger.info(f"Using image from source: {media_policy.source}")

        # 7. Создать ContentORM со status='generated'
        generated_content = ContentORM(
            id=str(uuid.uuid4()),
            channel_id=channel_id,
            source_url=content.get("source_url", f"generated://{channel_id}/{uuid.uuid4()}"),
            headline=content.get("title", "Generated post"),
            source_text=content.get("summary", ""),
            status="generated",
            draft_text=text,
            image_url=image_url,
            video_url=video_url,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

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
            "video_url": content.video_url,
            "ready_to_publish": bool(content.draft_text and (content.image_url or content.video_url)),
        }