"""Re-Evaluation Job - переоценивает переработанный контент."""
import logging
from typing import Any
from core.database import SessionLocal
from core.repositories.content_repository import ContentRepository
from engines.evaluator.engine import LLMEvaluatorEngine

logger = logging.getLogger(__name__)


class ReEvaluationJob:
    """
    Sprint 8.4: Переоценивает контент после RevisionJob.
    
    Берёт revised посты (status=draft с revision_count>0) и переоценивает.
    """

    async def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        logger.info("ReEvaluationJob started")

        db = SessionLocal()
        processed = 0
        approved = 0
        rejected = 0
        failed = 0

        try:
            repo = ContentRepository(db)

            # Берём revised посты (draft с revision_count > 0)
            items = repo.list_all(status="draft", limit=10)
            items = [i for i in items if (i.revision_count or 0) > 0]

            logger.info(f"Items for re-evaluation: {len(items)}")

            if not items:
                logger.info("No items need re-evaluation")
                return {"status": "ok", "processed": 0, "approved": 0, "rejected": 0, "failed": 0}

            evaluator = LLMEvaluatorEngine()

            for item in items:
                try:
                    processed += 1
                    logger.info(f"Re-evaluating: {item.headline[:50]}...")

                    result = await evaluator.evaluate(
                        source_facts=(item.source_text or item.headline),
                        generated_post=item.draft_text,
                        target_style="Telegram expert IT channel"
                    )

                    item.quality_score = result.overall

                    if result.is_approved:
                        item.status = "approved"
                        approved += 1
                        logger.info(f"✅ Approved after revision: {item.id}")
                    else:
                        item.status = "needs_revision"
                        item.last_revision_reason = getattr(result, 'feedback_for_regeneration', None) or "Still needs revision"
                        rejected += 1

                    db.commit()

                except Exception as e:
                    logger.exception(f"Re-evaluation failed for {item.id}: {e}")
                    failed += 1
                    db.rollback()

            logger.info(f"ReEvaluationJob finished: processed={processed}, approved={approved}, rejected={rejected}, failed={failed}")
            return {
                "status": "ok",
                "processed": processed,
                "approved": approved,
                "rejected": rejected,
                "failed": failed
            }

        except Exception as e:
            logger.exception(f"ReEvaluationJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()