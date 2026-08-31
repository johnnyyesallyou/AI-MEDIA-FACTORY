"""VK Publisher - реальная интеграция с VK API."""
import requests
from datetime import datetime
from typing import Any
import logging

from .base import PublisherInterface, PublishResult


logger = logging.getLogger(__name__)


class VkPublisher(PublisherInterface):
    """
    Sprint 11: Publisher для VK (ВКонтакте).
    
    Использует VK API метод wall.post для публикации постов в группе.
    
    API документация: https://dev.vk.com/ru/method/wall.post
    
    Требуемые credentials:
        - group_id: ID группы VK (например: -123456789 или 123456789)
        - access_token: Access token с правами wall, groups
    """
    
    VK_API_URL = "https://api.vk.com/method/wall.post"
    VK_API_VERSION = "5.199"
    
    @property
    def platform_name(self) -> str:
        return "vk"
    
    def validate_credentials(self, credentials: dict) -> bool:
        """Проверяет наличие group_id и access_token."""
        return bool(
            credentials.get("group_id") and
            credentials.get("access_token")
        )
    
    def publish(
        self,
        text: str,
        credentials: dict,
        channel: Any = None,
        **kwargs
    ) -> PublishResult:
        """
        Публикует пост в VK группу через wall.post.
        
        Args:
            text: Текст поста
            credentials: {
                "group_id": str,      # ID группы (с минусом для групп)
                "access_token": str   # VK access token
            }
            channel: Channel объект (опционально)
            **kwargs: Дополнительные параметры (attachments, и т.д.)
        
        Returns:
            PublishResult с post_id и published_at
        """
        if not self.validate_credentials(credentials):
            logger.error("VK: Missing group_id or access_token")
            return PublishResult(
                success=False,
                error="Missing group_id or access_token"
            )
        
        group_id = credentials["group_id"]
        access_token = credentials["access_token"]
        
        # Если group_id без минуса — добавляем (для групп нужен отрицательный owner_id)
        owner_id = str(group_id)
        if not owner_id.startswith("-") and not owner_id.startswith("club"):
            owner_id = f"-{owner_id}"
        
        try:
            logger.info(f"VK: Publishing to group {owner_id}")
            
            # VK API wall.post
            payload = {
                "owner_id": owner_id,
                "from_group": 1,  # Публикация от имени группы
                "message": text,
                "access_token": access_token,
                "v": self.VK_API_VERSION,
            }
            
            # Добавляем дополнительные параметры (attachments, и т.д.)
            for key in ["attachments", "services", "signed", "publish_date", 
                       "lat", "long", "place_id", "post_id", "guid", 
                       "mark_as_ads", "close_comments", "donut_paid_duration",
                       "mute_notifications", "copyright"]:
                if key in kwargs:
                    payload[key] = kwargs[key]
            
            response = requests.post(
                self.VK_API_URL,
                data=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Проверяем ошибки VK API
            if "error" in data:
                error = data["error"]
                error_msg = f"VK API error {error.get('error_code')}: {error.get('error_msg')}"
                logger.error(error_msg)
                return PublishResult(
                    success=False,
                    error=error_msg
                )
            
            # Успех — получаем post_id
            post_id = data.get("response", {}).get("post_id")
            if post_id:
                full_post_id = f"{owner_id}_{post_id}"
                logger.info(f"VK: Published successfully. Post ID: {full_post_id}")
                return PublishResult(
                    success=True,
                    message_id=full_post_id,
                    published_at=datetime.utcnow(),
                    platform_data={
                        "vk_post_id": full_post_id,
                        "vk_owner_id": owner_id,
                        "vk_post_number": post_id
                    }
                )
            else:
                logger.error("VK: No post_id in response")
                return PublishResult(
                    success=False,
                    error="No post_id in VK API response"
                )
        
        except requests.exceptions.Timeout:
            logger.error("VK: Request timeout")
            return PublishResult(success=False, error="VK API timeout")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"VK: Connection error: {e}")
            return PublishResult(success=False, error=f"Connection error: {str(e)}")
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"VK: HTTP error: {e}")
            return PublishResult(success=False, error=f"HTTP error: {str(e)}")
        
        except Exception as e:
            logger.exception(f"VK: Unexpected error: {e}")
            return PublishResult(success=False, error=str(e))
    
    def get_post_url(self, owner_id: str, post_id: str) -> str:
        """Возвращает URL поста в VK."""
        # Убираем минус из owner_id для URL
        clean_owner_id = owner_id.lstrip("-")
        return f"https://vk.com/wall{owner_id}_{post_id}"