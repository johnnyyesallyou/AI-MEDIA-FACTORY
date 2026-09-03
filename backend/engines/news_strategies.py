"""Sprint 67.3 + 69.3: News Strategies — использует реальные RSS из channel.content_profile."""
import logging
from typing import List, Dict, Any, Optional

from backend.engines.rss_fetcher import fetch_rss_topics
from backend.engines.llm_post_generator import generate_news_post_llm
from backend.engines.telegram_publisher import TelegramPublisher
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM

logger = logging.getLogger(__name__)


class NewsResearchStrategy:
    """Research стратегия для новостных каналов."""
    
    def __init__(self, profile: Any):
        self.profile = profile
        # Sprint 69.3: читаем из content_profile (проброшен из channel)
        cp = getattr(profile, 'content_profile', None) or {}
        self.real_sources = cp.get('sources', [])
        self.freshness_hours = cp.get('freshness_hours', 24)
        if not self.freshness_hours:
            research_cfg = getattr(profile, 'research', None) or {}
            self.freshness_hours = research_cfg.get('freshness_hours', 24)
    
    async def collect_sources(self) -> List[Dict[str, Any]]:
        if self.real_sources and isinstance(self.real_sources, list):
            logger.info(f"Collecting {len(self.real_sources)} real RSS sources")
            return self.real_sources
        logger.warning("No real RSS sources in content_profile")
        return []
    
    async def extract_topics(self, sources: List[Dict]) -> List[Dict[str, Any]]:
        if not sources:
            logger.warning("No sources provided")
            return []
        topics = await fetch_rss_topics(sources, max_age_hours=self.freshness_hours, max_topics=10)
        logger.info(f"Extracted {len(topics)} topics from RSS")
        return topics


class NewsGenerationStrategy:
    def __init__(self, profile: Any):
        self.profile = profile
        content = getattr(profile, 'content', None) or {}
        self.max_length = content.get('max_length', 1200)
        self.formats = content.get('formats', ['breaking_news'])
        self.tone = getattr(profile, 'tone', 'informative') or 'informative'
    
    async def generate_post(self, topic: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        logger.info(f"Generating news post: {topic.get('title', 'unknown')[:60]}")
        
        # Sprint 69.4: пробуем LLM generation
        llm_content = await generate_news_post_llm(
            topic=topic,
            tone=self.tone,
            max_length=self.max_length
        )
        
        # Fallback на summary если LLM недоступен
        content = llm_content if llm_content else topic.get("summary", "")
        
        return {
            "title": topic.get("title", ""),
            "content": content,
            "url": topic.get("url", ""),
            "source": topic.get("source", ""),
            "format": self.formats[0] if self.formats else "breaking_news",
        }


class NewsMediaStrategy:
    def __init__(self, profile: Any):
        self.profile = profile
        media = getattr(profile, 'media', None) or {}
        self.preferred = media.get('preferred', ['image'])
    
    async def select_media(self, post: Dict[str, Any]) -> Optional[str]:
        logger.info(f"Selecting media for: {post.get('title', 'unknown')[:50]}")
        return None


class NewsPublishingStrategy:
    def __init__(self, profile: Any):
        self.profile = profile
        publishing = getattr(profile, 'publishing', None) or {}
        mode = publishing.get('mode')
        if not mode:
            cp = getattr(profile, 'content_profile', None) or {}
            if isinstance(cp, dict):
                mode = cp.get('publishing_mode')
        self.mode = mode or 'approval_required'

        # Sprint 69.18: platform + credentials из канала (если не проброшены)
        self.platform = getattr(profile, 'platform', None)
        if getattr(profile, 'channel_id', None):
            try:
                db = SessionLocal()
                try:
                    ch = db.query(ChannelORM).filter(ChannelORM.id == profile.channel_id).first()
                    if ch:
                        self.platform = self.platform or ch.platform
                        if not getattr(profile, 'vk_group_id', None):
                            profile.vk_group_id = ch.vk_group_id
                        if not getattr(profile, 'vk_access_token', None):
                            profile.vk_access_token = ch.vk_access_token
                        if not getattr(profile, 'bot_token', None):
                            profile.bot_token = ch.bot_token
                        if not getattr(profile, 'chat_id', None):
                            profile.chat_id = ch.chat_id
                finally:
                    db.close()
            except Exception as e:
                logger.warning(f"Channel lookup failed: {e}")
        self.platform = self.platform or 'telegram'
        logger.info(f"NewsPublishingStrategy: mode={self.mode}, platform={self.platform}")
    
    def _publish_vk(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Sprint 69.18: публикация в VK через wall.post."""
        import requests as _requests
        group_id = getattr(self.profile, "vk_group_id", None)
        token = getattr(self.profile, "vk_access_token", None)
        if not group_id or not token:
            return {"success": False, "error": "VK credentials missing"}
        gid = "".join(ch for ch in str(group_id) if ch.isdigit())
        title = post.get("title", "")
        body = post.get("content", "")
        message = (title + "\n\n" + body)[:4000]
        try:
            resp = _requests.post(
                "https://api.vk.com/method/wall.post",
                data={
                    "owner_id": "-" + gid,
                    "message": message,
                    "access_token": token,
                    "v": "5.131",
                },
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
        
        # Sprint 69.5 fix: правильные имена полей (headline/draft_text) + channel_id
        db = SessionLocal()
        try:
            channel_id = getattr(self.profile, 'channel_id', None)
            status = "draft" if self.mode == "approval_required" else "published"
            
            content = ContentORM(
                headline=post.get("title", ""),
                draft_text=post.get("content", ""),
                source_url=post.get("url", ""),
                source_text=post.get("summary", ""),
                channel_id=channel_id,
                status=status,
                model_used="llama3.1:8b",
            )
            db.add(content)
            db.commit()
            db.refresh(content)
            logger.info(f"Content saved: id={content.id}, status={status}, headline={content.headline[:50]}")
        except Exception as e:
            logger.exception(f"Failed to save content: {e}")
            try:
                db.rollback()
            except:
                pass
            try:
                db.close()
            except:
                pass
            return {"success": False, "error": f"DB save failed: {e}"}
        db.close()
        
        # Auto mode: отправляем в Telegram
        if self.mode == "auto":
            # Sprint 69.18: VK платформа — публикуем в VK и возвращаемся
            if self.platform == "vk":
                vk_result = self._publish_vk(post)
                if vk_result.get("success"):
                    try:
                        from datetime import datetime as _dt
                        db2 = SessionLocal()
                        try:
                            row = db2.query(ContentORM).filter(ContentORM.id == content.id).first()
                            if row:
                                row.telegram_message_id = str(vk_result.get("message_id"))
                                row.published_at = _dt.utcnow()
                                db2.commit()
                                logger.info(f"Saved VK post id to content {content.id}")
                        finally:
                            db2.close()
                    except Exception as e:
                        logger.error(f"Failed to save VK post id: {e}")
                return vk_result
            # Получаем bot_token и chat_id из profile (проброшены из channel)
            bot_token = getattr(self.profile, 'bot_token', None)
            chat_id = getattr(self.profile, 'chat_id', None)
            
            if not bot_token or not chat_id:
                logger.error("bot_token or chat_id not set")
                return {"success": False, "error": "Missing bot_token/chat_id"}
            
            publisher = TelegramPublisher(bot_token, chat_id)
            
            # Формируем текст сообщения
            text = f"{post.get('content', '')}"
            if post.get('source'):
                text += f"\n\nИсточник: {post['source']}"
            
            # Отправляем
            if media_url:
                result = await publisher.send_photo(media_url, caption=text)
            else:
                result = await publisher.send_message(text)
            
            if result.get("success"):
                message_id = result.get("message_id")
                logger.info(f"Published to Telegram: message_id={message_id}")
                
                # Sprint 69.15 fix: сохраняем telegram_message_id и published_at
                # Получаем content.id из созданной записи
                content_id = content.id if hasattr(content, 'id') else None
                if content_id and message_id:
                    try:
                        db2 = SessionLocal()
                        try:
                            # Sprint 69.16: ORM update (обходит затенение text локальной строкой)
                            from datetime import datetime as _dt
                            row = db2.query(ContentORM).filter(ContentORM.id == content_id).first()
                            if row:
                                row.telegram_message_id = str(message_id)
                                row.published_at = _dt.utcnow()
                                db2.commit()
                                logger.info(f"Saved telegram_message_id={message_id} to content {content_id}")
                            else:
                                logger.error(f"Content row not found: {content_id}")
                        except Exception as e:
                            logger.error(f"Failed to save telegram_message_id: {e}")
                            db2.rollback()
                        finally:
                            db2.close()
                    except Exception as e:
                        logger.error(f"DB session error: {e}")
                
                return {"success": True, "mode": "auto", "message_id": message_id}
            else:
                logger.error(f"Telegram publish failed: {result.get('error')}")
                return {"success": False, "error": result.get("error")}
        
        # Approval required: сохраняем как draft
        if self.mode == "approval_required":
            logger.info(f"Saved as draft (approval_required)")
            return {"success": True, "mode": "approval_required", "status": "draft", "content_id": content.id}
        
        # Manual mode
        return {"success": False, "mode": "manual", "reason": "Manual mode"}
