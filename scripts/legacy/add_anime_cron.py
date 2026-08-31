import pathlib

p = pathlib.Path("/app/backend/automation/scheduler.py")
c = p.read_text(encoding="utf-8")

# Добавляем импорт AnimePipelineJob
if "from .jobs.anime_pipeline_job import AnimePipelineJob" not in c:
    c = c.replace(
        "from .jobs.manga_pipeline_job import MangaPipelineJob",
        "from .jobs.manga_pipeline_job import MangaPipelineJob\nfrom .jobs.anime_pipeline_job import AnimePipelineJob",
    )
    print("[OK] Added AnimePipelineJob import")

# Добавляем cron job для anime (каждые 30 минут, через 15 минут после manga)
if "anime_pipeline_job" not in c:
    anime_cron = '''
        # Sprint 51: Anime pipeline (every 30 minutes, offset by 15 min from manga)
        self.scheduler.add_job(
            func=lambda: asyncio.to_thread(AnimePipelineJob().run),
            trigger="interval",
            minutes=30,
            id="anime_pipeline_job",
            name="Anime Pipeline (Research + Publish)",
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )
        logger.info("Added anime pipeline job (every 30 minutes)")
'''
    
    # Вставляем после manga_pipeline_job (строка 73)
    c = c.replace(
        '        logger.info("Added manga pipeline job (every 30 minutes)")\n',
        '        logger.info("Added manga pipeline job (every 30 minutes)")\n' + anime_cron,
    )
    print("[OK] Added anime_pipeline_job cron")

p.write_text(c, encoding="utf-8")