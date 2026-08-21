"""VK Publisher - Sprint 49."""
import logging
from typing import Dict
from engines.vk.engine import VKEngine

logger = logging.getLogger(__name__)


class VKPublisher:
    """Publisher для VK platform."""
    
    def __init__(self):
        self.engine = VKEngine()
    
    def publish(self, item, channel) -> Dict:
        """Публикует пост в VK."""
        try:
            group_id = getattr(channel, "vk_group_id", None)
            access_token = getattr(channel, "vk_access_token", None)
            
            if not group_id or not access_token:
                raise ValueError("VK channel not configured (missing group_id or access_token)")
            
            text = item.draft_text
            result = self.engine.publish(
                text=text,
                group_id=group_id,
                access_token=access_token,
            )
            
            return {
                "status": result.status,
                "post_id": result.post_id,
                "text_length": result.text_length,
                "published_at": result.published_at.isoformat(),
            }
            
        except Exception as e:
            logger.exception("VK publish failed")
            raise