import pathlib

# 1. Добавляем retry_stage в runner.py
p = pathlib.Path('./backend/automation/runner.py')
s = p.read_text(encoding='utf-8')

if 'async def retry_stage' not in s:
    # Добавляем словарь маппинга в начало класса (после __init__)
    old_init_end = '''        logger.info(
            "AutomationRunner initialized"
        )'''

    new_init_end = '''        logger.info(
            "AutomationRunner initialized"
        )

        self.stage_map = {
            "research": ResearchJob,
            "decision": DecisionJob,
            "writing": WritingJob,
            "evaluation": EvaluatorJob,
            "revision": RevisionJob,
            "re_evaluation": ReEvaluationJob,
            "publish": PublishJob,
        }'''

    if old_init_end in s:
        s = s.replace(old_init_end, new_init_end)
        print('OK: stage_map added to runner')
    else:
        print('WARN: init pattern not found')

    # Добавляем метод retry_stage перед run_now
    retry_method = '''
    async def retry_stage(self, channel, stage_name: str, execution_id: str) -> dict:
        """Повторяет один конкретный этап пайплайна для канала."""
        if stage_name not in self.stage_map:
            return {"status": "failed", "error": f"Unknown stage: {stage_name}"}

        job_class = self.stage_map[stage_name]
        job = job_class()

        logger.info(
            "Retrying stage=%s channel=%s execution_id=%s",
            stage_name,
            getattr(channel, "name", None),
            execution_id
        )

        try:
            job_result = job.run(channel=channel, execution_id=execution_id)
            import inspect
            if inspect.isawaitable(job_result):
                job_result = await job_result
            return job_result
        except Exception as e:
            logger.exception("Retry failed %s", stage_name)
            return {"status": "failed", "error": str(e)}

'''

    # Вставляем retry_stage перед run_now
    if 'async def run_now' in s:
        s = s.replace('    async def run_now', retry_method + '    async def run_now')
        print('OK: retry_stage method added')

    p.write_text(s, encoding='utf-8')
    print('DONE')