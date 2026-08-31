import sys, asyncio, uuid, inspect
sys.path.insert(0, '/app')
import backend.automation.runtime.jobs_registry  # noqa

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from backend.automation.runtime.job_factory import JobFactory

async def main():
    db = SessionLocal()
    try:
        ch = db.query(ChannelORM).filter(ChannelORM.name.like('%Манга%')).first()
        if not ch:
            print('[!] Manga channel not found'); return
        print(f'Channel: {ch.name} | style={ch.style_profile}')

        for node_type in ['manga_research', 'manga_enrichment', 'manga_publish', 'anime_research', 'anime_publish']:
            job = JobFactory.create(node_type)
            has_exec = hasattr(job, 'execute')
            has_run = hasattr(job, 'run')
            is_async_run = has_run and inspect.iscoroutinefunction(job.run)
            print(f'  {node_type:18} -> {type(job).__name__:22} execute={has_exec} run={has_run} async_run={is_async_run}')
    finally:
        db.close()

asyncio.run(main())