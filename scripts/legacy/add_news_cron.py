import pathlib

p = pathlib.Path("/app/backend/automation/scheduler.py")
c = p.read_text(encoding="utf-8")

# Добавляем импорт NewsPipelineJob
if "from .jobs.news_pipeline_job import NewsPipelineJob" not in c:
    c = c.replace(
        "from .jobs.anime_pipeline_job import AnimePipelineJob",
        "from .jobs.anime_pipeline_job import AnimePipelineJob\nfrom .jobs.news_pipeline_job import NewsPipelineJob",
    )
    print("[OK] Added NewsPipelineJob import")

# Добавляем cron job (каждые 30 минут, через 10 минут после anime)
if "news_pipeline_job" not in c:
    news_cron = '''
        # Sprint 52B: News pipeline (every 30 minutes)
        self.scheduler.add_job(
            func=lambda: asyncio.to_thread(NewsPipelineJob().run),
            trigger="interval",
            minutes=30,
            id="news_pipeline_job",
            name="News Pipeline (Research + Publish)",
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )
        logger.info("Added news pipeline job (every 30 minutes)")
'''
    
    c = c.replace(
        '        logger.info("Added anime pipeline job (every 30 minutes)")\n',
        '        logger.info("Added anime pipeline job (every 30 minutes)")\n' + news_cron,
    )
    print("[OK] Added news_pipeline_job cron")

p.write_text(c, encoding="utf-8")