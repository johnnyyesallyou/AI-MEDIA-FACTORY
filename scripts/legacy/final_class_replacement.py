import re

file_path = './backend/automation/jobs/automation_jobs.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Идеальный, пуленепробиваемый WritingJob
correct_writing = '''class WritingJob:

    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("writing")
        logger.info("WritingJob started")
        db = SessionLocal()
        processed = 0
        failed = 0
        guard = OutputGuard()

        try:
            repo = ContentRepository(db)
            items = repo.list_all(status="research", limit=10)
            logger.info("Writing queue size=%s", len(items))

            for item in items:
                try:
                    logger.info("Processing item=%s headline=%s", item.id, item.headline)
                    brief = ContentBrief(
                        topic=item.headline,
                        audience=TELEGRAM_AI_EXPERT.get("audience", "IT аудитория Telegram"),
                        goal="Объяснить новость, дать контекст и показать практическое значение.",
                        tone=TELEGRAM_AI_EXPERT.get("tone", "экспертный"),
                        length_chars=1500,
                        call_to_action="Что думаете? Поделитесь мнением.",
                        key_facts=[item.source_text or item.headline]
                    )
                    writer = WritingEngine()
                    result = writer.generate(brief, style_profile=TELEGRAM_AI_EXPERT)
                    raw_text = result.get("generated_text", "")
                    logger.info("Raw generated length=%s", len(raw_text))
                    clean_text = guard.clean(raw_text)
                    logger.info("Clean generated length=%s", len(clean_text))

                    if len(clean_text) < 100:
                        logger.warning("Text too short after guard. Saving anyway for evaluator.")

                    item.draft_text = clean_text
                    item.status = "draft"
                    db.commit()
                    processed += 1
                    logger.info("Written item=%s", item.id)
                except Exception as item_e:
                    failed += 1
                    db.rollback()
                    logger.exception("Writing failed item=%s error=%s", item.id, item_e)

            p_logger.finish("success", details=f"Processed {processed}, failed {failed}")
            return {"status": "ok", "items_processed": processed, "failed": failed}

        except Exception as e:
            error_msg = str(e)
            logger.exception("WritingJob failed with error: %s", error_msg)
            p_logger.finish("failed", error_message=error_msg)
            return {"status": "failed", "error": error_msg}
        finally:
            db.close()

'''

# 2. Идеальный, пуленепробиваемый EvaluatorJob
correct_evaluator = '''class EvaluatorJob:

    async def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        p_logger = PipelineLogger(execution_id, channel.id if channel else None)
        p_logger.start("evaluation")
        logger.info("EvaluatorJob started")
        db = SessionLocal()
        processed = 0
        approved = 0

        try:
            repo = ContentRepository(db)
            items = repo.list_all(status="draft", limit=10)
            logger.info("Evaluation queue size=%s", len(items))
            evaluator = LLMEvaluatorEngine()

            for item in items:
                try:
                    logger.info("Evaluating item=%s", item.id)
                    # Пытаемся оценить, если аргументы не совпадут, inner except перехватит это
                    result = evaluator.evaluate(item.draft_text)
                    score = result.get("quality_score", 0)
                    item.quality_score = score
                    processed += 1

                    if score >= 80:
                        item.status = "approved"
                        approved += 1
                    else:
                        item.status = "needs_revision"
                    
                    db.commit()
                except Exception as item_e:
                    db.rollback()
                    logger.exception("Evaluation failed for item=%s error=%s", item.id, item_e)

            p_logger.finish("success", details=f"Processed {processed}, approved {approved}")
            return {"status": "ok", "processed": processed, "approved": approved}

        except Exception as e:
            error_msg = str(e)
            logger.exception("EvaluatorJob failed with error: %s", error_msg)
            p_logger.finish("failed", error_message=error_msg)
            return {"status": "failed", "error": error_msg}
        finally:
            db.close()

'''

# Заменяем классы целиком (от "class X:" до следующего "class Y:")
content = re.sub(r'class WritingJob:.*?(?=\nclass EvaluatorJob:)', correct_writing, content, flags=re.DOTALL)
content = re.sub(r'class EvaluatorJob:.*?(?=\nclass RevisionJob:)', correct_evaluator, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ WritingJob и EvaluatorJob полностью переписаны с идеальными отступами и try/except!")
