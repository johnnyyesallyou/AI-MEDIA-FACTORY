import logging
from datetime import datetime
from .publisher import VKPublisher
from .models import VKPublishResult
from .exceptions import VKPublishError

logger = logging.getLogger(__name__)

class VKEngine:
    def publish(self, text: str, group_id: str, access_token: str) -> VKPublishResult:
        try:
            publisher = VKPublisher(group_id=group_id, access_token=access_token)
            result = publisher.publish(text)
            return VKPublishResult(
                status=result["status"],
                post_id=result["post_id"],
                published_at=datetime.utcnow(),
                text_length=result["text_length"],
            )
        except Exception as e:
            logger.exception("VK publish failed")
            raise VKPublishError(str(e))