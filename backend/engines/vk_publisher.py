"""Sprint 71.1: VK Publisher — публикация постов в VK группу."""
import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)

VK_API_VERSION = "5.199"
VK_API_BASE = "https://api.vk.com/method"


async def publish_to_vk(
    post: Dict[str, Any],
    vk_group_id: str,
    vk_access_token: str,
) -> Optional[str]:
    """
    Публикует пост в VK группу через wall.post.

    Args:
        post: {"title": "...", "content": "...", "url": "..."}
        vk_group_id: ID группы (например "240792540" или "-240792540")
        vk_access_token: VK access token с правами wall

    Returns:
        post_id строка (например "123") или None при ошибке
    """
    # Нормализуем group_id: убираем "club" и делаем отрицательным для групп
    group_id = str(vk_group_id).replace("club", "").replace("public", "").replace("event", "")
    if not group_id.startswith("-"):
        group_id = f"-{group_id}"

    title = post.get("title", "")
    content = post.get("content", "")
    source_url = post.get("url", "")

    # Формируем текст поста
    message = f"{title}\n\n{content}"
    if source_url:
        message += f"\n\n🔗 Источник: {source_url}"

    # Ограничение VK: 16384 символа
    if len(message) > 16000:
        message = message[:16000] + "..."
        logger.warning(f"VK message truncated to 16000 chars")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{VK_API_BASE}/wall.post",
                data={
                    "owner_id": group_id,
                    "from_group": 1,
                    "message": message,
                    "access_token": vk_access_token,
                    "v": VK_API_VERSION,
                },
            )
            
            data = response.json()
            
            if "error" in data:
                error = data["error"]
                logger.error(f"VK API error: {error.get('error_code')} - {error.get('error_msg')}")
                return None
            
            if "response" in data and "post_id" in data["response"]:
                post_id = str(data["response"]["post_id"])
                logger.info(f"VK post published: group={group_id}, post_id={post_id}")
                return post_id
            
            logger.error(f"VK API unexpected response: {data}")
            return None

    except httpx.TimeoutException:
        logger.error("VK API timeout")
        return None
    except Exception as e:
        logger.error(f"VK publish failed: {e}")
        return None