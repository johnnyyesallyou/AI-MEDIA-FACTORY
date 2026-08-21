import requests
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class VKPublisher:
    def __init__(self, group_id: str, access_token: str):
        self.group_id = group_id.replace("club", "").replace("-", "")
        self.access_token = access_token
        self.api_url = "https://api.vk.com/method/wall.post"
    
    def publish(self, text: str) -> Dict:
        """Публикует пост в VK группу."""
        try:
            params = {
                "owner_id": f"-{self.group_id}",
                "from_group": 1,
                "message": text,
                "access_token": self.access_token,
                "v": "5.131",
            }
            
            resp = requests.post(self.api_url, data=params, timeout=30)
            data = resp.json()
            
            if "response" in data:
                post_id = data["response"]["post_id"]
                return {
                    "status": "published",
                    "post_id": str(post_id),
                    "text_length": len(text),
                }
            elif "error" in data:
                error_msg = data["error"].get("error_msg", "Unknown error")
                logger.error(f"VK API error: {error_msg}")
                raise Exception(f"VK API error: {error_msg}")
            else:
                raise Exception(f"Unexpected VK response: {data}")
                
        except Exception as e:
            logger.exception("VK publish failed")
            raise