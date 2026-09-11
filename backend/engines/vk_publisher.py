"""Sprint 71.1: VK Publisher — публикация постов в VK группу.
Sprint 74.1: retry с exponential backoff (VK error codes 1/6/9/10/29 → transient)."""
import logging
from typing import Optional, Dict, Any
import httpx

from backend.core.reliability import with_retry, get_policy, VKError

logger = logging.getLogger(__name__)

VK_API_VERSION = "5.199"
VK_API_BASE = "https://api.vk.com/method"


async def _wall_post(group_id: str, message: str, vk_access_token: str) -> Dict[str, Any]:
    """Один вызов VK wall.post. Raise VKError/httpx ошибки (для retry)."""
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
        raise VKError(int(error.get("error_code", 0)), error.get("error_msg", "unknown"))

    if "response" in data and "post_id" in data["response"]:
        return data["response"]

    # Неизвестный формат ответа — не ретраим


def _enqueue_dlq_vk(
    group_id: str,
    post: Dict[str, Any],
    message: str,
    error_message: str,
    vk_access_token: str = "",
):
    """Sprint 74.4: автозапись в DLQ при исчерпании retry для VK."""
    try:
        from backend.core.dead_letter import get_dlq

        content: Dict[str, Any] = {
            "platform": "vk",
            "vk_group_id": group_id,
            "vk_access_token": vk_access_token,
            "title": post.get("title", ""),
            "text": post.get("content", ""),
            "url": post.get("url", ""),
            "message": message,
        }

        dlq = get_dlq()
        try:
            failure = dlq.enqueue(
                channel_id=group_id,
                pipeline="publishing",
                job="publish_vk",
                error_message=error_message,
                content_payload=content,
                error_type="publish_error",
                retry_delay_seconds=900.0,
            )
            logger.warning(
                f"DLQ auto-enqueue (vk): {failure.id} "
                f"group={group_id} retry_at={failure.retry_at}"
            )
        finally:
            dlq.close()
    except Exception as e:  # pragma: no cover — защита основного потока
        logger.error(f"DLQ auto-enqueue failed (vk): {e}")


async def publish_to_vk(
    post: Dict[str, Any],
    vk_group_id: str,
    vk_access_token: str,
) -> Optional[str]:
    """
    Публикует пост в VK группу через wall.post.

    Sprint 74.1: transient VK ошибки (flood/rate limit) ретраятся
    с exponential backoff (4 attempts); auth (5/7/17) и params (15/100/200) — fail fast.

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
        logger.warning("VK message truncated to 16000 chars")

    try:
        response = await with_retry(
            _wall_post, group_id, message, vk_access_token,
            policy=get_policy("vk"),
            context="vk.wall_post",
            channel_id=group_id,
            platform="vk",
        )
        post_id = str(response["post_id"])
        logger.info(f"VK post published: group={group_id}, post_id={post_id}")
        return post_id

    except (VKError, httpx.TimeoutException) as e:
        logger.error(f"VK API error after retries: {e}")
        _enqueue_dlq_vk(group_id, post, message, str(e), vk_access_token)
        return None
    except Exception as e:
        logger.error(f"VK publish failed: {e}")
        _enqueue_dlq_vk(group_id, post, message, str(e), vk_access_token)
        return None
