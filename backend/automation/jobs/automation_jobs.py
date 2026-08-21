from typing import Any
import logging
from datetime import datetime


from core.database import SessionLocal
from core.repositories.content_repository import ContentRepository
from core.repositories.channel_repository import ChannelRepository
from core.models.channel_schedule_orm import ChannelScheduleORM
from core.models.content_orm import ContentORM


from engines.writing.engine import WritingEngine
from engines.writing.models import ContentBrief
from engines.writing.output_guard import OutputGuard


from engines.evaluator.engine import LLMEvaluatorEngine
from engines.telegram.engine import TelegramEngine
from backend.automation.publishers import PublisherFactory
from engines.research.engine import ResearchEngine
import time
import uuid
from core.models.execution_log_orm import ExecutionLogORM


from backend.automation.config import TELEGRAM_AI_EXPERT


logger = logging.getLogger(__name__)




class PipelineLogger:
    def __init__(self, execution_id: str, channel_id: str = None):
        self.execution_id = execution_id or str(uuid.uuid4())
        self.channel_id = channel_id
        self.db = SessionLocal()
        self.start_time = None
        self.log_id = None

    def start(self, stage: str, headline: str = None):
        self.start_time = time.time()
        log = ExecutionLogORM(
            execution_id=self.execution_id,
            channel_id=self.channel_id,
            stage=stage,
            status='started',
            headline=headline
        )
        self.db.add(log)
        self.db.commit()
        self.log_id = log.id

    def finish(self, status: str, details: str = None, error_message: str = None):
        if not self.log_id: return
        duration_ms = int((time.time() - self.start_time) * 1000) if self.start_time else 0
        log = self.db.query(ExecutionLogORM).filter(ExecutionLogORM.id == self.log_id).first()
        if log:
            log.status = status
            log.completed_at = datetime.utcnow()
            log.duration_ms = duration_ms
            log.details = details
            log.error_message = error_message
            self.db.commit()
        self.db.close()

class ResearchJob:

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("research")

        logger.info(
            "ResearchJob started channel=%s",
            getattr(channel, "name", None)
        )

        db = SessionLocal()

        created = 0
        skipped = 0

        try:
            repo = ContentRepository(db)

            engine = ResearchEngine()

            research_result = engine.run(channel=channel)

            topics = research_result.get("topics", [])

            logger.info(
                "Research returned topics=%s",
                len(topics)
            )

            for topic in topics:

                title = topic.get(
                    "title",
                    "Untitled"
                )

                urls = topic.get(
                    "urls",
                    []
                )

                source_url = (
                    urls[0]
                    if urls
                    else "unknown"
                )

                if repo.exists(
                    channel_id=getattr(channel, "id", None),
                    source_url=source_url,
                    headline=title
                ):
                    skipped += 1
                    continue

                repo.create(
                    channel_id=(
                        channel.id
                        if channel
                        else None
                    ),
                    source_url=source_url,
                    headline=title,
                    source_text=topic.get(
                        "summary",
                        ""
                    ),
                    status="research"
                )

                created += 1

            p_logger.finish("success", details=f"Created {created}, skipped {skipped}")
            return {
                "status": "ok",
                "topics_received": len(topics),
                "created": created,
                "skipped": skipped
            }

        except Exception as e:

            error_msg = str(e)
            logger.exception(
                "ResearchJob failed: %s", error_msg
            )

            p_logger.finish("failed", error_message=error_msg)


            return {
                "status": "failed",
                "error": str(e)
            }

        finally:
            db.close()
        return {
        "status":"ok",
        "published":published,
        "failed":failed
        }


class DecisionJob:

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:

        logger.info("DecisionJob started")

        return {
            "status": "ok",
            "message": "decision engine placeholder"
        }



"""
WritingJob — генерирует контент из research items.

Использует WritingEngine v2 с полным Production Pipeline:
  Model Selector → Prompt Builder → LLM → Fact Guard → Validators → Output Guard
"""
import logging
from typing import Dict, Any

from sqlalchemy.orm import Session
from core.repositories.content_repository import ContentRepository
from engines.writing.engine import WritingEngine
from engines.writing.models import ContentBrief
from engines.writing.styles.profiles import TELEGRAM_AI_EXPERT


logger = logging.getLogger(__name__)


class WritingJob:
    """Генерирует контент из research items."""
    
    async def run(self, channel: Any = None, execution_id: str = None) -> Dict[str, Any]:
        """
        Запускает генерацию контента.
        
        Returns:
            Dict с ключами: status, items_processed, failed
        """
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("writing")
        
        logger.info("WritingJob started (v2 with full pipeline)")
        
        db = SessionLocal()
        repo = ContentRepository(db)
        
        # Получаем research items
        items = repo.list_all(status="research", limit=50)
        logger.info(f"Writing queue size: {len(items)}")
        
        processed = 0
        failed = 0
        
        for item in items:
            try:
                logger.info(f"Processing item={item.id} headline={item.headline[:50]}")
                
                # Создаём brief
                brief = ContentBrief(
                    topic=item.headline,
                    audience=TELEGRAM_AI_EXPERT.get("audience", "IT аудитория Telegram"),
                    goal="Объяснить новость, дать контекст и показать практическое значение.",
                    tone=TELEGRAM_AI_EXPERT.get("tone", "экспертный"),
                    length_chars=1500,
                    call_to_action="Что думаете? Поделитесь мнением.",
                    key_facts=[item.source_text or item.headline],
                    platform="telegram"
                )
                
                # Генерируем через WritingEngine v2
                writer = WritingEngine()
                result = await writer.generate(brief, style_profile=TELEGRAM_AI_EXPERT)
                
                generated_text = result.get("generated_text", "")
                draft = result.get("draft")
                
                logger.info(f"Raw generated length={len(generated_text)}")
                
                # WritingEngine v1.5: не сохраняем пустые или слишком короткие драфты
                if not generated_text or len(generated_text.strip()) < 50:
                    item.status = "needs_revision"
                    item.last_revision_reason = f"Generated text too short ({len(generated_text.strip())} chars). OutputGuard вернул пустой текст."
                    db.commit()
                    logger.warning(f"Skip short draft item={item.id} len={len(generated_text.strip()) if generated_text else 0}")
                    failed += 1
                    continue
                
                # Сохраняем результат
                item.draft_text = generated_text
                item.status = "draft"
                
                # WritingEngine v2: сохраняем validation_issues, fact_check_passed, model_used
                if draft:
                    # Конвертируем ValidationIssue в dict для JSON
                    item.validation_issues = [
                        {
                            "category": issue.category,
                            "severity": issue.severity,
                            "message": issue.message,
                            "suggestion": issue.suggestion
                        }
                        for issue in draft.validation_issues
                    ]
                    item.fact_check_passed = draft.fact_check_passed
                    item.model_used = draft.model_used
                    
                    logger.info(
                        f"Item {item.id}: model={draft.model_used}, "
                        f"fact_check={draft.fact_check_passed}, "
                        f"issues={len(draft.validation_issues)}"
                    )
                
                db.commit()
                processed += 1
                logger.info(f"Written item={item.id} len={len(generated_text)}")
                
            except Exception as item_e:
                failed += 1
                db.rollback()
                logger.exception(f"Writing failed item={item.id} error={item_e}")
        
        logger_status = "success" if failed == 0 else "partial" if processed > 0 else "failed"
        p_logger.finish(logger_status, details=f"Processed {processed}, failed {failed}")
        status = "ok" if failed == 0 else "partial" if processed > 0 else "failed"
        return {"status": status, "items_processed": processed, "failed": failed}


class EvaluatorJob:

    async def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("evaluation")
        logger.info("EvaluatorJob started")
        db = SessionLocal()
        processed = 0
        approved = 0
        rejected = 0

        try:
            repo = ContentRepository(db)
            items = repo.list_all(status="draft", limit=50)
            logger.info("Evaluation queue size=%s", len(items))
            evaluator = LLMEvaluatorEngine()

            for item in items:
                try:
                    if not item.draft_text:
                        logger.warning("Skip empty draft item=%s", item.id)
                        continue

                    result = await evaluator.evaluate(
                        source_facts=(item.source_text or item.headline),
                        generated_post=item.draft_text,
                        target_style="Telegram expert IT channel"
                    )
                    logger.info("Evaluated item=%s score=%s approved=%s", item.id, result.overall, result.is_approved)
                    item.quality_score = result.overall

                    if result.is_approved:
                        item.status = "approved"
                        item.last_revision_reason = None
                        approved += 1
                    else:
                        item.status = "needs_revision"
                        # Р·РЅР°Р»Рё, Р§РўРћ РёРјРµРЅРЅРѕ РЅСѓР¶РЅРѕ СѓР»СѓС‡С€РёС‚СЊ РІ С‚РµРєСЃС‚Рµ
                        item.last_revision_reason = getattr(result, 'feedback_for_regeneration', None) or "РљР°С‡РµСЃС‚РІРѕ РЅРёР¶Рµ РїРѕСЂРѕРіР° 80"
                        rejected += 1
                        logger.info("Item %s needs revision: %s", item.id, (item.last_revision_reason or "")[:100])

                    processed += 1
                    db.commit()
                except Exception as e:
                    db.rollback()
                    logger.exception("Evaluation failed item=%s error=%s", item.id, e)

            p_logger.finish("success", details=f"Processed {processed}, approved {approved}, rejected {rejected}")
            return {
                "status": "ok",
                "processed": processed,
                "approved": approved,
                "rejected": rejected
            }

        except Exception as e:
            error_msg = str(e)
            logger.exception("EvaluatorJob failed with error: %s", error_msg)
            p_logger.finish("failed", error_message=error_msg)
            return {"status": "failed", "error": error_msg}
        finally:
            db.close()




class ImageJob:
    """
    Sprint 11: Генерирует картинки для approved постов через Pollinations AI.
    Запускается перед PublishJob для добавления визуального контента.
    """

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        logger.info("ImageJob started")

        db = SessionLocal()
        processed = 0
        generated = 0
        failed = 0

        try:
            from core.repositories.content_repository import ContentRepository
            from engines.image.engine import ImageEngine

            repo = ContentRepository(db)

            # Берём approved посты БЕЗ image_url
            items = repo.list_all(status="approved", limit=10)
            items = [i for i in items if not getattr(i, 'image_url', None)]

            logger.info(f"Items without images: {len(items)}")

            if not items:
                logger.info("No items need images")
                return {"status": "ok", "processed": 0, "generated": 0, "failed": 0}

            image_engine = ImageEngine()

            for item in items:
                try:
                    processed += 1

                    # Извлекаем название аниме из headline (в кавычках)
                    import re
                    anime_match = re.search(r'[""«»]([^""«»]+)[""«»]', item.headline)
                    anime_title = anime_match.group(1) if anime_match else item.headline[:50]

                    logger.info(f"Generating image for: {anime_title}...")

                    # Генерируем картинку
                    result = image_engine.generate_anime_poster(
                        anime_title=anime_title,
                        context=item.headline
                    )

                    if result and result.get("image_url") and 'error' not in result:
                        item.image_url = result["image_url"]
                        item.image_prompt = result.get("prompt", "")
                        db.commit()
                        generated += 1
                        logger.info(f"✅ Image generated for {item.id}")
                    else:
                        logger.warning(f"Failed to generate image for {item.id}: {result}")
                        failed += 1

                except Exception as e:
                    logger.exception(f"Image generation failed for {item.id}: {e}")
                    failed += 1
                    db.rollback()

            logger.info(f"ImageJob finished: processed={processed}, generated={generated}, failed={failed}")
            return {
                "status": "ok",
                "processed": processed,
                "generated": generated,
                "failed": failed
            }

        except Exception as e:
            logger.exception(f"ImageJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()


class PublishJob:
    """
    Sprint 11 (refactored): Публикует уже готовые approved посты.
    
    ВАЖНО: НЕ генерирует текст заново — использует существующий draft_text.
    Текст уже прошёл WritingJob + EvaluatorJob + получил approval.
    """

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("publish")

        logger.info("PublishJob started (refactored: using existing draft_text)")

        db = SessionLocal()

        # === RATE LIMITS & AUTO_PUBLISH ===
        schedule = None
        if channel:
            schedule = db.query(ChannelScheduleORM).filter(
                ChannelScheduleORM.channel_id == channel.id
            ).first()

        auto_publish = schedule.auto_publish if schedule else True
        max_posts_per_day = schedule.max_posts_per_day if schedule else 3

        if not auto_publish:
            logger.info("Auto-publish disabled for channel %s", channel.id if channel else None)
            p_logger.finish("success", details="Auto-publish disabled for this channel")
            db.close()
            return {"status": "skipped", "reason": "auto_publish_disabled", "published": 0, "failed": 0}

        # Лимит публикаций за сутки
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        published_today = 0
        if channel:
            published_today = db.query(ContentORM).filter(
                ContentORM.channel_id == channel.id,
                ContentORM.status == "published",
                ContentORM.published_at >= today_start
            ).count()

        remaining = max(0, max_posts_per_day - published_today)
        logger.info(
            "Rate limit check: channel=%s published_today=%s max=%s remaining=%s",
            channel.id if channel else None, published_today, max_posts_per_day, remaining
        )

        if remaining <= 0:
            logger.info("Rate limit reached for channel %s", channel.id if channel else None)
            p_logger.finish(
                "success",
                details=f"Rate limit reached ({published_today}/{max_posts_per_day} posts today)"
            )
            db.close()
            return {
                "status": "skipped",
                "reason": "rate_limit",
                "published_today": published_today,
                "max_posts_per_day": max_posts_per_day,
                "published": 0,
                "failed": 0,
            }

        published = 0
        failed = 0

        try:
            from core.repositories.channel_repository import ChannelRepository
            from backend.automation.publishers import PublisherFactory

            content_repo = ContentRepository(db)
            channel_repo = ChannelRepository(db)

            # Получаем одобренные посты для публикации
            items = content_repo.list_all(
                status="approved",
                limit=min(10, remaining)
            )
            logger.info("Publish queue size=%s", len(items))

            # Sprint 11: получаем publisher для платформы канала
            platform = getattr(channel, "platform", "telegram") or "telegram"
            publisher = PublisherFactory.get(platform)
            logger.info("Using publisher for platform=%s", platform)

            for item in items:
                try:
                    # Проверяем что канал подключен
                    if not channel or not getattr(channel, "is_connected", False):
                        logger.warning("Skip publish item=%s channel not connected", item.id)
                        continue

                    # Проверяем что есть готовый draft_text (не генерируем заново!)
                    if not item.draft_text or len(item.draft_text.strip()) < 50:
                        logger.warning("Skip publish item=%s no draft_text or too short", item.id)
                        item.status = "needs_revision"
                        item.last_revision_reason = "No valid draft_text for publishing"
                        db.commit()
                        failed += 1
                        continue

                    # Собираем credentials в зависимости от платформы
                    if platform == "vk":
                        credentials = {
                            "group_id": getattr(channel, "vk_group_id", None),
                            "access_token": getattr(channel, "vk_access_token", None),
                        }
                    elif platform == "youtube":
                        credentials = {
                            "channel_id": getattr(channel, "youtube_channel_id", None),
                            "api_key": getattr(channel, "youtube_api_key", None),
                        }
                    elif platform == "dzen":
                        credentials = {
                            "channel_id": getattr(channel, "dzen_channel_id", None),
                            "api_key": getattr(channel, "dzen_api_key", None),
                        }
                    else:  # telegram (default)
                        credentials = {
                            "bot_token": getattr(channel, "bot_token", None),
                            "chat_id": getattr(channel, "chat_id", None),
                        }

                    if not publisher.validate_credentials(credentials):
                        logger.warning("Skip publish item=%s invalid credentials for platform=%s", item.id, platform)
                        continue

                    # Публикуем через PublisherFactory (используем существующий draft_text!)
                    full_text = f"{item.headline}\n\n{item.draft_text}"
                    
                    # Sprint 11: добавляем картинку если есть
                    image_url = getattr(item, 'image_url', None)
                    
                    result = publisher.publish(
                        text=full_text,
                        credentials=credentials,
                        channel=channel,
                        image_url=image_url
                    )

                    if not result.success:
                        logger.warning("Skip publish item=%s platform=%s error=%s", item.id, platform, result.error)
                        failed += 1
                        item.publish_error = result.error
                        db.commit()
                        continue

                    # Успешная публикация
                    item.status = "published"
                    item.telegram_message_id = str(result.message_id) if result.message_id else None
                    item.published_at = result.published_at
                    item.publish_error = None

                    # Sprint 11: сохраняем platform-specific данные если поле есть
                    if hasattr(item, "publish_platform_data") and result.platform_data:
                        item.publish_platform_data = result.platform_data

                    db.commit()
                    published += 1
                    logger.info("✅ Published item=%s platform=%s message_id=%s", item.id, platform, result.message_id)
                    
                    # Sprint 50: создаём PostMetric для аналитики
                    try:
                        from core.models.analytics import PostMetric
                        post_metric = PostMetric()
                        post_metric.content_id = item.id
                        post_metric.channel_id = channel.id if channel else None
                        post_metric.platform = platform
                        post_metric.published_at = result.published_at
                        post_metric.external_id = str(result.message_id) if result.message_id else None
                        db.add(post_metric)
                        db.commit()
                        logger.info("✅ PostMetric created for item=%s", item.id)
                    except Exception as metric_e:
                        logger.warning("Failed to create PostMetric for item=%s: %s", item.id, metric_e)

                except Exception as e:
                    db.rollback()
                    logger.exception("Publish failed for item=%s error=%s", item.id, e)
                    failed += 1

            p_logger.finish("success", details=f"Published {published}, failed {failed}")
            return {"status": "ok", "published": published, "failed": failed}

        except Exception as e:
            error_msg = str(e)
            logger.exception("PublishJob failed with error: %s", error_msg)
            p_logger.finish("failed", error_message=error_msg)
            return {"status": "failed", "error": error_msg}
        finally:
            db.close()