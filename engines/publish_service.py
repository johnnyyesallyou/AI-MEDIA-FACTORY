"""Publish Service - Sprint 60.8 (multi-platform).

Публикует сгенерированные посты (ContentORM.status='generated').
Поддерживает Telegram и VK.

Flow:
  ContentORM (generated)
    ↓
  TelegramPublisher / VKPublisher (по platform)
    ↓
  ContentORM (published) + telegram_message_id / vk_post_id
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
from engines.post_history_recorder import record_post_history

logger = logging.getLogger(__name__)


class PublishService:
    """Публикация сгенерированных постов (multi-platform)."""

    def __init__(self, db_session: SessionLocal):
        self.db = db_session

    async def publish_generated_post(
        self,
        content_id: str
    ) -> Optional[ContentORM]:
        """
        Публикует сгенерированный пост.
        Поддерживает: telegram, vk
        
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

        if content.status not in ["draft", "approved", "generated"]:
            logger.error(f"Content {content_id} status is {content.status}, not 'draft/approved/generated'")
            return None

        # 2. Получить канал
        channel = self.db.query(ChannelORM).filter_by(id=content.channel_id).first()
        if not channel:
            logger.error(f"Channel {content.channel_id} not found")
            content.status = "failed"
            content.publish_error = "Channel not found"
            self.db.commit()
            return None

        platform = (channel.platform or "").lower()

        # 3. Dispatch по платформе
        try:
            if platform == "telegram":
                result = self._publish_telegram(channel, content)
            elif platform == "vk":
                result = self._publish_vk(channel, content)
            else:
                content.status = "failed"
                content.publish_error = f"Platform '{platform}' not supported"
                self.db.commit()
                logger.error(f"Platform '{platform}' not supported")
                return None

            # 4. Обработка результата
            if result.get("status") == "success":
                message_id = result.get("message_id") or result.get("post_id")
                content.status = "published"
                content.telegram_message_id = str(message_id) if message_id else None
                content.published_at = datetime.utcnow()
                content.publish_error = None
                
                # Записываем в PostHistory
                record_post_history(
                    db=self.db,
                    channel=channel,
                    item=content,
                    publication=None,
                    result=result
                )
                
                self.db.commit()
                self.db.refresh(content)
                
                logger.info(f"Post published to {platform}: id={content.id}, msg_id={message_id}")
                return content
            else:
                content.status = "failed"
                content.publish_error = result.get("error", "Unknown error")
                self.db.commit()
                logger.error(f"Publish failed to {platform}: {content.publish_error}")
                return None

        except Exception as e:
            content.status = "failed"
            content.publish_error = str(e)
            self.db.commit()
            logger.exception(f"Publish exception on {platform}: {e}")
            return None

    # ------------------------------------------------------------------
    # Telegram
    # ------------------------------------------------------------------
    def _publish_telegram(self, channel, content) -> dict:
        """Публикация в Telegram."""
        from engines.telegram.publisher import TelegramPublisher

        if not channel.bot_token or not channel.chat_id:
            return {"status": "error", "error": "Missing bot_token or chat_id"}

        publisher = TelegramPublisher(bot_token=channel.bot_token, chat_id=channel.chat_id)
        
        text = content.draft_text
        image_url = content.image_url
        video_url = getattr(content, 'video_url', None)

        # Нормализуем status VK-возврата (published) → Telegram-формат (success)
        if video_url:
            result = publisher.publish_video(text, video_url, inline_buttons=None)
        elif image_url:
            result = publisher.publish_photo(text, image_url, inline_buttons=None)
        else:
            result = publisher.publish(text, inline_buttons=None)
        
        # Telegram возвращает status="success" / "error"
        return result

    # ------------------------------------------------------------------
    # VK
    # ------------------------------------------------------------------
    def _publish_vk(self, channel, content) -> dict:
        """Публикация в VK."""
        from engines.vk.publisher import VKPublisher

        if not channel.vk_access_token or not channel.vk_group_id:
            return {"status": "error", "error": "Missing vk_access_token or vk_group_id"}

        publisher = VKPublisher(
            group_id=channel.vk_group_id,
            access_token=channel.vk_access_token
        )

        try:
            # VK пока поддерживает только текст (без attachments)
            result = publisher.publish(text=content.draft_text)
            
            # Нормализуем статус: VK возвращает "published" → приводим к "success"
            if result.get("status") == "published":
                return {
                    "status": "success",
                    "post_id": result.get("post_id"),
                    "platform": "vk",
                }
            else:
                return {
                    "status": "error",
                    "error": f"Unexpected VK status: {result.get('status')}",
                }
        except Exception as e:
            logger.exception(f"VK publish exception: {e}")
            return {"status": "error", "error": str(e)}