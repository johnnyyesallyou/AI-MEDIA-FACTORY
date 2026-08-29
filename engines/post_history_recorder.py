"""Post History Recorder - Sprint 58.

Единый helper для записи факта публикации в post_history после успешного publish.

Используется publish job-ами:
- manga_publish_job.py
- news_publish_job.py
- anime_publish_job.py

Цель:
Publish → PostHistory(message_id) → AnalyticsCollector → PostMetric → Learnings
"""
import logging
from datetime import datetime
from typing import Any, Optional

from core.models.post_history_orm import PostHistoryORM

logger = logging.getLogger(__name__)


def _get_attr(obj: Any, *names: str, default=None):
    """Безопасно достать первый существующий attr/key."""
    if obj is None:
        return default

    for name in names:
        if isinstance(obj, dict) and name in obj:
            return obj.get(name)

        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value

    return default


def _get_publication_text(publication: Any, item: Any = None) -> Optional[str]:
    return (
        _get_attr(publication, "text", "caption", "content")
        or _get_attr(item, "text", "draft_text", "description", "title", "name", "headline")
    )


def _get_image_url(publication: Any, item: Any = None) -> Optional[str]:
    return (
        _get_attr(publication, "image_url", "cover_url", "thumbnail_url", "cover")
        or _get_attr(item, "image_url", "cover_url", "thumbnail_url", "cover")
    )


def _get_video_url(publication: Any, item: Any = None) -> Optional[str]:
    return (
        _get_attr(publication, "video_url", "media_url")
        or _get_attr(item, "video_url", "media_url")
    )


def _infer_media_type(publication: Any, item: Any = None) -> str:
    video_url = _get_video_url(publication, item)
    image_url = _get_image_url(publication, item)

    if video_url:
        return "video"
    if image_url:
        return "image"

    metadata = _get_attr(publication, "metadata", default={}) or {}
    if isinstance(metadata, dict):
        if metadata.get("_video_bytes") or metadata.get("video_bytes"):
            return "video"
        if metadata.get("_image_bytes") or metadata.get("image_bytes"):
            return "image"

    return "none"


def record_post_history(
    db,
    channel,
    item,
    publication,
    result: dict,
) -> Optional[PostHistoryORM]:
    """
    Записать публикацию в post_history.

    Args:
        db: SQLAlchemy Session
        channel: ChannelORM
        item: ContentORM/Knowledge item
        publication: Publication объект из Formatter Layer
        result: результат publisher.publish(), должен содержать message_id

    Returns:
        PostHistoryORM или None
    """
    if not channel:
        logger.warning("record_post_history skipped: channel is None")
        return None

    if not result or result.get("status") != "success":
        return None

    message_id = result.get("message_id")
    if message_id is None:
        logger.warning("record_post_history skipped: no message_id in publish result")
        return None

    channel_id = str(_get_attr(channel, "id"))
    content_id = _get_attr(item, "id")

    # Не создаём дубликаты: сначала ищем по channel_id + message_id.
    existing = (
        db.query(PostHistoryORM)
        .filter(
            PostHistoryORM.channel_id == channel_id,
            PostHistoryORM.message_id == str(message_id),
        )
        .first()
    )

    if existing:
        existing.text = existing.text or _get_publication_text(publication, item)
        existing.image_url = existing.image_url or _get_image_url(publication, item)
        existing.video_url = existing.video_url or _get_video_url(publication, item)
        existing.media_type = existing.media_type or _infer_media_type(publication, item)
        existing.posted_at = existing.posted_at or datetime.utcnow()
        logger.debug("PostHistory already exists for channel=%s message_id=%s", channel_id, message_id)
        return existing

    post = PostHistoryORM(
        channel_id=channel_id,
        content_id=str(content_id) if content_id else None,
        platform=_get_attr(channel, "platform", default="telegram"),
        text=_get_publication_text(publication, item),
        image_url=_get_image_url(publication, item),
        video_url=_get_video_url(publication, item),
        media_type=_infer_media_type(publication, item),
        message_id=str(message_id),
        posted_at=_get_attr(item, "published_at") or datetime.utcnow(),
        created_at=datetime.utcnow(),
    )

    db.add(post)
    logger.info(
        "PostHistory recorded: channel=%s content=%s message_id=%s media=%s",
        channel_id,
        content_id,
        message_id,
        post.media_type,
    )
    return post