"""Sprint 67.4: Generic Strategies — универсальные стратегии для всех архетипов.

Читают настройки из ChannelProfile + ArchetypeDefaults.
Один код обслуживает releases/educational/viral/reviews/community/aggregator.
"""
import logging
from typing import List, Dict, Any, Optional

from core.models.archetypes import Archetype, get_archetype_defaults
from core.models.publication_builder import PublicationBuilder
from core.models.renderers import TelegramRenderer, VKRenderer

logger = logging.getLogger(__name__)


def _arch(profile: Any) -> Archetype:
    try:
        return Archetype(getattr(profile, "archetype", "news"))
    except (ValueError, KeyError):
        return Archetype.NEWS


class GenericResearchStrategy:
    """Sprint 70.1: реальная реализация вместо заглушки.
    Читает RSS-источники из content_profile (как NewsResearchStrategy),
    freshness выводится из archetype.frequency_per_day, если явно не задан."""

    def __init__(self, profile: Any):
        self.profile = profile
        self.archetype_defaults = get_archetype_defaults(_arch(profile))
        self.archetype = self.archetype_defaults.archetype

        cp = getattr(profile, "content_profile", None) or {}
        self.real_sources = list(cp.get("sources", []))
        for s in self.real_sources:
            if isinstance(s, dict) and "source_type" not in s and "type" in s:
                s["source_type"] = s["type"]

        explicit_freshness = cp.get("freshness_hours")
        if explicit_freshness:
            self.freshness_hours = explicit_freshness
        else:
            freq = self.archetype_defaults.frequency_per_day or 5
            self.freshness_hours = max(6, min(72, 168 // freq))

    async def collect_sources(self) -> List[Dict[str, Any]]:
        logger.info(f"[{self.archetype.value}] Collecting {len(self.real_sources)} real sources")
        if self.real_sources and isinstance(self.real_sources, list):
            return self.real_sources
        logger.warning(f"[{self.archetype.value}] No real sources in content_profile")
        return []

    async def extract_topics(self, sources: List[Dict]) -> List[Dict[str, Any]]:
        if not sources:
            logger.warning(f"[{self.archetype.value}] No sources provided")
            return []

        from backend.engines.rss_fetcher import fetch_rss_topics
        from backend.engines.deduplicator import filter_new_topics

        topics = await fetch_rss_topics(sources, max_age_hours=self.freshness_hours, max_topics=10)
        logger.info(f"[{self.archetype.value}] Extracted {len(topics)} raw topics (freshness={self.freshness_hours}h)")

        channel_id = getattr(self.profile, "channel_id", None)
        if channel_id and topics:
            topics = filter_new_topics(channel_id, topics)

        return topics


class GenericGenerationStrategy:
    def __init__(self, profile: Any):
        self.profile = profile
        self.archetype = _arch(profile)  # Sprint 69.21: сохраняем для LLM prompt
        defaults = get_archetype_defaults(self.archetype)
        cfg = profile.content or {}
        self.max_length = cfg.get("max_length", defaults.max_post_length)
        self.formats = cfg.get("formats", defaults.allowed_formats)
        self.tone = profile.tone or defaults.tone

    async def generate_post(self, topic: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        logger.info(f"[{self.tone}] Generating post with LLM (archetype={self.archetype}, max={self.max_length})")
        
        # Sprint 69.21: реальная LLM-генерация вместо копирования RSS
        from backend.engines.llm_post_generator import generate_generic_post_llm
        
        llm_content = await generate_generic_post_llm(
            topic=topic,
            archetype=self.archetype,
            tone=self.tone,
            max_length=self.max_length,
            language="Russian"
        )
        
        # Fallback на RSS summary если LLM недоступен
        content = llm_content if llm_content else topic.get("summary", "")
        
        return {
            "title": topic.get("title", ""),
            "content": content,
            "url": topic.get("url", ""),
            "source": topic.get("source", ""),
            "format": self.formats[0] if self.formats else "post",
            "tone": self.tone,
            "max_length": self.max_length,
        }


class GenericMediaStrategy:
    def __init__(self, profile: Any):
        self.profile = profile
        defaults = get_archetype_defaults(_arch(profile))
        cfg = profile.media or {}
        self.preferred = cfg.get("preferred", [defaults.media_policy])
        self.fallback = cfg.get("fallback", [])

    async def select_media(self, post: Dict[str, Any]) -> Optional[str]:
        logger.info(f"Selecting media (preferred={self.preferred})")
        return None


class GenericPublishingStrategy:
    """Sprint 70.2: реальная реализация вместо заглушки.
    Sprint 70.3: честный status - published выставляется только после
    подтверждённой успешной отправки, иначе status='failed'.
    Логика скопирована из NewsPublishingStrategy (проверена в бою) —
    сохраняет ContentORM, публикует в Telegram/VK, пишет telegram_message_id."""

    def __init__(self, profile: Any):
        self.profile = profile
        defaults = get_archetype_defaults(_arch(profile))
        cfg = profile.publishing or {}
        self.mode = cfg.get("mode", defaults.publishing_mode)
        self.frequency = cfg.get("frequency_per_day", defaults.frequency_per_day)

        self.platform = getattr(profile, "platform", None)
        if getattr(profile, "channel_id", None):
            try:
                from core.database import SessionLocal
                from core.models.channel_orm import ChannelORM
                db = SessionLocal()
                try:
                    ch = db.query(ChannelORM).filter(ChannelORM.id == profile.channel_id).first()
                    if ch:
                        self.platform = self.platform or ch.platform
                        if not getattr(profile, "vk_group_id", None):
                            profile.vk_group_id = ch.vk_group_id
                        if not getattr(profile, "vk_access_token", None):
                            profile.vk_access_token = ch.vk_access_token
                        if not getattr(profile, "bot_token", None):
                            profile.bot_token = ch.bot_token
                        if not getattr(profile, "chat_id", None):
                            profile.chat_id = ch.chat_id
                finally:
                    db.close()
            except Exception as e:
                logger.warning(f"Channel lookup failed: {e}")
        self.platform = self.platform or "telegram"
        logger.info(f"GenericPublishingStrategy: mode={self.mode}, platform={self.platform}, freq={self.frequency}/day")

    def _publish_vk(self, post: Dict[str, Any]) -> Dict[str, Any]:
        import requests as _requests
        group_id = getattr(self.profile, "vk_group_id", None)
        token = getattr(self.profile, "vk_access_token", None)
        if not group_id or not token:
            return {"success": False, "error": "VK credentials missing"}
        gid = "".join(ch for ch in str(group_id) if ch.isdigit())
        title = post.get("title", "")
        body = post.get("content", "")
        # Sprint 72.5: Use VKRenderer instead of manual formatting
        try:
            builder = PublicationBuilder()
            from core.models.channel_orm import ChannelORM
            db_temp = SessionLocal()
            channel = db_temp.query(ChannelORM).filter(ChannelORM.id == getattr(self.profile, 'channel_id', None)).first()
            db_temp.close()
            
            publication = builder.build(post=post, profile=self.profile, channel=channel)
            renderer = VKRenderer()
            render_result = renderer.render(publication)
            message = render_result.message
            logger.info(f"Sprint 72.5: VK Publication built")
        except Exception as e:
            logger.error(f"Sprint 72.5: VK Builder/Renderer failed: {e}")
            # Fallback to manual formatting
            message = (title + "\n\n" + body)[:4000]
        try:
            resp = _requests.post(
                "https://api.vk.com/method/wall.post",
                data={"owner_id": "-" + gid, "message": message, "access_token": token, "v": "5.131"},
                timeout=30,
            )
            data = resp.json()
        except Exception as e:
            return {"success": False, "error": f"VK API error: {e}"}
        if "response" in data and data["response"].get("post_id"):
            post_id = data["response"]["post_id"]
            logger.info(f"Published to VK: post_id={post_id}")
            return {"success": True, "message_id": f"vk_{post_id}"}
        return {"success": False, "error": str(data.get("error"))}

    async def publish(self, post: Dict[str, Any], media_url: Optional[str]) -> Dict[str, Any]:
        logger.info(f"Publishing (mode={self.mode}): {post.get('title', '')[:50]}")

        from core.database import SessionLocal
        from core.models.content_orm import ContentORM

        db = SessionLocal()
        try:
            channel_id = getattr(self.profile, "channel_id", None)
            # Sprint 70.3: изначально НЕ published — реальный статус выставляется
            # ниже, по факту успеха/неудачи отправки.
            initial_status = "draft" if self.mode == "approval_required" else "pending"

            content = ContentORM(
                headline=post.get("title", ""),
                draft_text=post.get("content", ""),
                source_url=post.get("url", ""),
                source_text=post.get("summary", ""),
                channel_id=channel_id,
                status=initial_status,
                model_used="llama3.1:8b",
            )
            db.add(content)
            db.commit()
            db.refresh(content)
            content_id = content.id  # Sprint 72.5: save before db.close()
            rendered_text = None  # Sprint 72.5: will be set by Renderer
            logger.info(f"Content saved: id={content.id}, status={initial_status}, headline={content.headline[:50]}")
        except Exception as e:
            logger.exception(f"Failed to save content: {e}")
            try:
                db.rollback()
            except Exception:
                pass
            try:
                db.close()
            except Exception:
                pass
            return {"success": False, "error": f"DB save failed: {e}"}
        db.close()

        def _mark_status(content_id, status, message_id=None):
            """Sprint 70.3: единая точка обновления финального статуса."""
            from datetime import datetime as _dt
            try:
                db2 = SessionLocal()
                try:
                    row = db2.query(ContentORM).filter(ContentORM.id == content_id).first()
                    if row:
                        row.status = status
                        if message_id:
                            row.telegram_message_id = str(message_id)
                            row.published_at = _dt.utcnow()
                        db2.commit()
                        logger.info(f"Content {content_id} status -> {status}" + (f" (msg_id={message_id})" if message_id else ""))
                except Exception as e:
                    logger.error(f"Failed to update status for {content_id}: {e}")
                    db2.rollback()
                finally:
                    db2.close()
            except Exception as e:
                logger.error(f"DB session error while marking status: {e}")

        if self.mode == "auto":
            if self.platform == "vk":
                vk_result = self._publish_vk(post)
                if vk_result.get("success"):
                    _mark_status(content_id, "published", vk_result.get("message_id"))
                else:
                    _mark_status(content_id, "failed")
                    logger.error(f"VK publish failed: {vk_result.get('error')}")
                return vk_result

            bot_token = getattr(self.profile, "bot_token", None)
            chat_id = getattr(self.profile, "chat_id", None)
            if not bot_token or not chat_id:
                logger.error("bot_token or chat_id not set")
                _mark_status(content_id, "failed")
                return {"success": False, "error": "Missing bot_token/chat_id"}

            from backend.engines.telegram_publisher import TelegramPublisher
            publisher = TelegramPublisher(bot_token, chat_id)

            # Sprint 72.5: Use PublicationBuilder + Renderer instead of manual formatting
            try:
                builder = PublicationBuilder()
                from core.models.channel_orm import ChannelORM
                db_temp = SessionLocal()
                channel = db_temp.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
                db_temp.close()
                
                publication = builder.build(post=post, profile=self.profile, channel=channel)
                
                if self.platform == 'vk':
                    renderer = VKRenderer()
                    render_result = renderer.render(publication)
                    rendered_text = render_result.message
                    text = rendered_text
                else:  # telegram
                    renderer = TelegramRenderer(source_emoji="🔗")
                    render_result = renderer.render(publication)
                    rendered_text = render_result.text
                    text = rendered_text
                
                logger.info(f"Sprint 72.5: Publication built and rendered for {self.platform}")
            except Exception as e:
                logger.error(f"Sprint 72.5: Builder/Renderer failed: {e}")
                # Fallback to manual formatting
                text = f"{post.get('content', '')}"
                if post.get("source"):
                    text += f"\n\nИсточник: {post['source']}"

            if media_url:
                result = await publisher.send_photo(media_url, caption=text)
            else:
                # Sprint 72.5: Extract render metadata if available
                parse_mode = None
                reply_markup = None
                disable_web_page_preview = False
                
                if 'render_result' in locals() and hasattr(render_result, 'parse_mode'):
                    parse_mode = render_result.parse_mode
                    reply_markup = render_result.reply_markup
                    disable_web_page_preview = render_result.disable_web_page_preview
                    logger.info(f"Sprint 72.5: Passing render metadata to publisher")
                
                result = await publisher.send_message(text)

            if result.get("success"):
                message_id = result.get("message_id")
                logger.info(f"Published to Telegram: message_id={message_id}")
                _mark_status(content_id, "published", message_id)
                return {"success": True, "mode": "auto", "message_id": message_id}
            else:
                logger.error(f"Telegram publish failed: {result.get('error')}")
                _mark_status(content_id, "failed")
                result = await publisher.send_message(text, parse_mode=parse_mode, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)

        if self.mode == "approval_required":
            logger.info("Saved as draft (approval_required)")
            return {"success": True, "mode": "approval_required", "status": "draft", "content_id": content.id}

        _mark_status(content_id, "failed")
        return {"success": False, "mode": "manual", "reason": "Manual mode"}
