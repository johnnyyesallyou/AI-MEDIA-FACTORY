"""Sprint 71.2: VkPublishingStrategy — стратегия публикации для VK."""
import logging
from typing import Dict, Any, Optional

from backend.engines.vk_publisher import publish_to_vk

logger = logging.getLogger(__name__)


class VkPublishingStrategy:
    """Publishing стратегия для VK."""

    def __init__(self, profile: Any):
        self.profile = profile
        self.vk_group_id = getattr(profile, 'vk_group_id', None)
        self.vk_access_token = getattr(profile, 'vk_access_token', None)

    async def publish(self, post: Dict[str, Any]) -> Optional[str]:
        """
        Публикует пост в VK.

        Args:
            post: {"title": "...", "content": "...", "url": "..."}

        Returns:
            post_id или None
        """
        if not self.vk_group_id or not self.vk_access_token:
            logger.error("VK credentials not configured")
            return None

        logger.info(f"Publishing to VK group {self.vk_group_id}: {post.get('title', 'N/A')[:50]}")
        
        post_id = await publish_to_vk(
            post=post,
            vk_group_id=self.vk_group_id,
            vk_access_token=self.vk_access_token,
        )
        
        if post_id:
            logger.info(f"Published to VK: post_id={post_id}")
        else:
            logger.error("Failed to publish to VK")
        
        return post_id