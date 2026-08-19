import pathlib

code = '''from typing import Any
import logging

from core.database import SessionLocal
from core.repositories.content_repository import ContentRepository
from .automation_jobs import PipelineLogger

logger = logging.getLogger(__name__)


class RevisionJob:

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        # Локальная константа - защита от бесконечного цикла
        MAX_REVISION_COUNT = 3

        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("revision")

        logger.info("=== REVISION JOB STARTED ===")
        db = SessionLocal()
        processed = 0
        rejected_too_many = 0

        try:
            repo = ContentRepository(db)
            items = repo.list_all(status="needs_revision", limit=50)

            logger.info(f"=== REVISION QUEUE SIZE: {len(items)} ===")

            for item in items:
                current_count = (getattr(item, 'revision_count', 0) or 0) + 1
                item.revision_count = current_count

                if current_count >= MAX_REVISION_COUNT:
                    # Защита от бесконечного цикла - помечаем как rejected
                    item.status = "rejected"
                    item.last_revision_reason = f"Превышен лимит итераций ({MAX_REVISION_COUNT}). Текст не улучшился."
                    rejected_too_many += 1
                    logger.info("Item %s rejected: too many revisions (%d)", item.id, current_count)
                else:
                    # Возвращаем на черновик для повторной оценки
                    item.status = "draft"
                    processed += 1

            if rejected_too_many > 0:
                logger.info("Rejected %d items due to max revision count", rejected_too_many)

            if processed > 0 or rejected_too_many > 0:
                db.commit()

            p_logger.finish("success", details=f"Revised {processed}, rejected {rejected_too_many} (max revisions)")

            return {
                "status": "ok",
                "processed": processed,
                "rejected": rejected_too_many
            }

        except Exception as e:
            db.rollback()
            error_msg = str(e)
            logger.exception("Revision failed error=%s", error_msg)
            p_logger.finish("failed", error_message=error_msg)

            return {
                "status": "failed",
                "error": error_msg
            }

        finally:
            db.close()
'''

p = pathlib.Path('./backend/automation/jobs/revision_job.py')
p.write_text(code, encoding='utf-8')
print('OK: revision_job.py rewritten')