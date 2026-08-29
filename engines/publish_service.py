"""Publish Service - Sprint 60.4.

Публикует сгенерированные посты (ContentORM.status='generated').

Flow:
  ContentORM (generated)
    ↓
  TelegramPublisher (sendMessage/sendPhoto/sendVideo)
    ↓
  ContentORM (published) + telegram_message_id
    ↓
  PostHistoryORM (для analytics)
"""
import logging
from typing import Optional
from datetime import datetime

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from core.models.post_history_orm import PostHistoryORM
from engines.telegram.publisher import TelegramPublisher
from engines.post_history_recorder import record_post_history

logger = logging.getLogger(__name__)


class PublishService:
    """Публикация сгенерированных постов."""

    def __init__(self, db_session: SessionLocal):
        self.db = db_session

    async def publish_generated_post(
        self,
        content_id: str
    ) -> Optional[ContentORM]:
        """
        Публикует сгенерированный пост.
        
        Args:
            content_id: ID ContentORM со status='generated'
            
        Returns:
            ContentORM со status='published' или None
        """
        # 1. Получить ContentORM
        content = self.db.query(ContentORM).filter_by(id=content_id).first()
        if not content:
            logger.error(f"Content {content_id} not found")
            return None

        if content.status != "generated":
            logger.error(f"Content {content_id} status is {content.status}, not 'generated'")
            return None

        # 2. Получить канал
        channel = self.db.query(ChannelORM).filter_by(id=content.channel_id).first()
        if not channel:
            logger.error(f"Channel {content.channel_id} not found")
            content.status = "failed"
            content.publish_error = "Channel not found"
            self.db.commit()
            return None

        # 3. Создать publisher
        if channel.platform != "telegram":
            logger.error(f"Platform {channel.platform} not supported yet")
            content.status = "failed"
            content.publish_error = f"Platform {channel.platform} not supported"
            self.db.commit()
            return None

        if not channel.bot_token or not channel.chat_id:
            logger.error(f"Channel {channel.id} missing bot_token or chat_id")
            content.status = "failed"
            content.publish_error = "Missing bot_token or chat_id"
            self.db.commit()
            return None

        publisher = TelegramPublisher(bot_token=channel.bot_token, chat_id=channel.chat_id)

        # 4. Публикуем
        text = content.draft_text
        image_url = content.image_url
        video_url = getattr(content, 'video_url', None)

        try:
            if video_url:
                # Видео приоритет
                result = publisher.publish_video(text, video_url, inline_buttons=None)
            elif image_url:
                # Картинка
                result = publisher.publish_photo(text, image_url, inline_buttons=None)
            else:
                # Только текст
                result = publisher.publish(text, inline_buttons=None)

            if result.get("status") == "success":
                # Успех
                content.status = "published"
                content.telegram_message_id = str(result.get("message_id"))
                content.published_at = datetime.utcnow()
                content.publish_error = None
                
                # Записываем в PostHistory для analytics
                record_post_history(
                    db=self.db,
                    channel=channel,
                    item=content,
                    publication=None,  # Publication object не нужен для ContentORM
                    result=result
                )
                
                self.db.commit()
                self.db.refresh(content)
                
                logger.info(f"Post published: id={content.id}, message_id={content.telegram_message_id}")
                return content
            else:
                # Ошибка
                content.status = "failed"
                content.publish_error = result.get("error", "Unknown error")
                self.db.commit()
                logger.error(f"Publish failed: {content.publish_error}")
                return None

        except Exception as e:
            content.status = "failed"
            content.publish_error = str(e)
            self.db.commit()
            logger.exception(f"Publish exception: {e}")
            return None