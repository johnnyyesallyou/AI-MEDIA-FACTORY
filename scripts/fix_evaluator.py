import re

# 1. Fix EvaluatorJob in automation_jobs.py (добавляем p_logger.finish и внешний except)
file_path1 = './backend/automation/jobs/automation_jobs.py'
with open(file_path1, 'r', encoding='utf-8') as f:
    content1 = f.read()

correct_evaluator = '''class EvaluatorJob:

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
            items = repo.list_all(status="draft", limit=10)
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
                        approved += 1
                    else:
                        item.status = "needs_revision"
                        rejected += 1

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

'''

content1 = re.sub(r'class EvaluatorJob:.*?(?=\nclass PublishJob:)', correct_evaluator, content1, flags=re.DOTALL)

with open(file_path1, 'w', encoding='utf-8') as f:
    f.write(content1)

print("✅ EvaluatorJob в automation_jobs.py исправлен (добавлен p_logger.finish и except)!")


# 2. Fix ReEvaluationJob (полностью переписываем файл с правильными аргументами и await)
file_path2 = './backend/automation/jobs/re_evaluation_job.py'

correct_reeval = '''from typing import Any
import logging

from core.database import SessionLocal
from core.repositories.content_repository import ContentRepository
from engines.evaluator.engine import LLMEvaluatorEngine
from .automation_jobs import PipelineLogger

logger = logging.getLogger(__name__)

class ReEvaluationJob:

    async def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("re_evaluation")
        logger.info("ReEvaluationJob started")
        db = SessionLocal()
        processed = 0
        approved = 0
        rejected = 0

        try:
            repo = ContentRepository(db)
            items = repo.list_all(status="draft", limit=10)
            evaluator = LLMEvaluatorEngine()

            for item in items:
                try:
                    if not getattr(item, 'revision_count', 0):
                        continue
                    if not item.draft_text:
                        continue

                    result = await evaluator.evaluate(
                        source_facts=(item.source_text or item.headline),
                        generated_post=item.draft_text,
                        target_style="Telegram expert IT channel"
                    )
                    
                    score = getattr(result, 'overall', 0)
                    is_approved = getattr(result, 'is_approved', False)

                    item.quality_score = score
                    processed += 1

                    if is_approved or score >= 70:
                        item.status = "approved"
                        approved += 1
                    else:
                        item.status = "needs_revision"
                        rejected += 1
                        
                    db.commit()
                except Exception as item_e:
                    db.rollback()
                    logger.exception("ReEvaluation failed item=%s error=%s", item.id, item_e)

            p_logger.finish("success", details=f"Processed {processed}, approved {approved}, rejected {rejected}")
            return {
                "status": "ok",
                "processed": processed,
                "approved": approved,
                "rejected": rejected
            }

        except Exception as e:
            db.rollback()
            error_msg = str(e)
            logger.exception("ReEvaluation failed error=%s", error_msg)
            p_logger.finish("failed", error_message=error_msg)
            return {
                "status": "failed",
                "error": error_msg
            }

        finally:
            db.close()
'''

with open(file_path2, 'w', encoding='utf-8') as f:
    f.write(correct_reeval)

print("✅ ReEvaluationJob полностью переписан (async, await, правильные аргументы)!")
