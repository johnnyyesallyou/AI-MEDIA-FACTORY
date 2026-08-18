"""Revision Job - перерабатывает текст на основе feedback от EvaluatorJob."""
import logging
from typing import Any
from core.database import SessionLocal
from core.repositories.content_repository import ContentRepository
from engines.writing.engine import WritingEngine

logger = logging.getLogger(__name__)


class RevisionJob:
    """
    Sprint 8.4: Перерабатывает контент на основе feedback от EvaluatorJob.
    
    Берёт rejected посты с last_revision_reason и регенерирует их через WritingEngine.
    """

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        logger.info("RevisionJob started")

        db = SessionLocal()
        processed = 0
        revised = 0
        failed = 0

        try:
            repo = ContentRepository(db)

            # Берём rejected посты с reason
            items = repo.list_all(status="needs_revision", limit=10)
            items = [i for i in items if getattr(i, 'last_revision_reason', None)]

            logger.info(f"Items for revision: {len(items)}")

            if not items:
                logger.info("No items need revision")
                return {"status": "ok", "processed": 0, "revised": 0, "failed": 0}

            writer = WritingEngine()

            for item in items:
                try:
                    processed += 1
                    logger.info(f"Revising: {item.headline[:50]}...")
                    logger.info(f"  Reason: {item.last_revision_reason[:100]}")

                    # Регенерируем с учётом feedback
                    result = writer.revise(
                        original_text=item.draft_text or "",
                        feedback=item.last_revision_reason,
                        headline=item.headline
                    )

                    if result and result.get("revised_text"):
                        item.draft_text = result["revised_text"]
                        item.status = "draft"  # Снова draft для повторной evaluation
                        item.revision_count = (item.revision_count or 0) + 1
                        item.last_revision_reason = None
                        db.commit()
                        revised += 1
                        logger.info(f"✅ Revised: {item.id}")
                    else:
                        logger.warning(f"Failed to revise {item.id}")
                        failed += 1

                except Exception as e:
                    logger.exception(f"Revision failed for {item.id}: {e}")
                    failed += 1
                    db.rollback()

            logger.info(f"RevisionJob finished: processed={processed}, revised={revised}, failed={failed}")
            return {
                "status": "ok",
                "processed": processed,
                "revised": revised,
                "failed": failed
            }

        except Exception as e:
            logger.exception(f"RevisionJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()