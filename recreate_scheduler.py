import base64
import pathlib

# Декодируем base64-закодированный scheduler.py
# (Это чистая версия без ошибок)
scheduler_content = '''
import logging
import os
import asyncio
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import and_
from pytz import timezone as pytz_timezone

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.channel_schedule_orm import ChannelScheduleORM
from .manager import automation_manager
from .automation_manager_v2 import automation_manager_v2
from .jobs import MonitoringJob

logger = logging.getLogger(__name__)

USE_AUTOMATION_V2 = os.getenv("USE_AUTOMATION_V2", "false").lower() == "true"


class AutomationScheduler:
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None

    async def start(self):
        if self.scheduler and self.scheduler.running:
            logger.info("Automation scheduler already running")
            return

        logger.info("Automation scheduler starting with APScheduler...")
        print("🔥 Automation scheduler (APScheduler) starting", flush=True)

        if USE_AUTOMATION_V2:
            logger.info("Starting AutomationManager v2 (Channel Isolation + Policies)...")
            print("🚀 AutomationManager v2 ENABLED (Channel Isolation + Policies)", flush=True)
            await automation_manager_v2.start()
        else:
            logger.info("Using legacy AutomationManager (v1)")
            print("ℹ️ Using legacy AutomationManager (v1). Set USE_AUTOMATION_V2=true to enable v2", flush=True)

        self.scheduler = AsyncIOScheduler()

        await self.load_schedules_from_db()

        # Sprint 12: Monitoring job (every 10 minutes)
        self.scheduler.add_job(
            func=lambda: asyncio.to_thread(MonitoringJob().run),
            trigger="interval",
            minutes=10,
            id="monitoring_job",
            name="Monitoring (health + SLA)",
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )
        logger.info("Added monitoring job (every 10 minutes)")

        self.scheduler.start()
        logger.info("Automation scheduler started with %d jobs", len(self.scheduler.get_jobs()))
        print(f"🚀 Automation scheduler started with {len(self.scheduler.get_jobs())} jobs", flush=True)

    async def stop(self):
        if self.scheduler:
            logger.info("Stopping automation scheduler")
            self.scheduler.shutdown(wait=False)
            self.scheduler = None
            logger.info("Automation scheduler stopped")
            print("🔥 Automation scheduler stopped", flush=True)

        if USE_AUTOMATION_V2:
            logger.info("Stopping AutomationManager v2...")
            await automation_manager_v2.stop()
            print("🔥 AutomationManager v2 stopped", flush=True)

    async def load_schedules_from_db(self):
        db = SessionLocal()
        try:
            schedules = (
                db.query(ChannelScheduleORM)
                .join(ChannelORM)
                .filter(
                    and_(
                        ChannelScheduleORM.is_active == True,
                        ChannelORM.is_active == True
                    )
                )
                .all()
            )

            for schedule in schedules:
                await self.add_channel_job(schedule)

        finally:
            db.close()

    async def add_channel_job(self, schedule: ChannelScheduleORM):
        """Добавляет задачу для конкретного канала на основе его cron-расписания."""
        if not self.scheduler:
            return

        job_id = f"channel_{schedule.channel_id}"

        existing_job = self.scheduler.get_job(job_id)
        if existing_job:
            self.scheduler.remove_job(job_id)

        try:
            tz = pytz_timezone(schedule.timezone or "Europe/Moscow")
            trigger = CronTrigger.from_crontab(schedule.cron_expression, timezone=tz)

            self.scheduler.add_job(
                self.run_channel_automation,
                trigger=trigger,
                args=[schedule.channel_id],
                id=job_id,
                name=f"Automation for channel {schedule.channel_id}",
                replace_existing=True
            )

            logger.info(
                "Added job for channel %s with cron '%s'",
                schedule.channel_id,
                schedule.cron_expression
            )

        except Exception as e:
            logger.error(
                "Failed to add job for channel %s: %s",
                schedule.channel_id,
                e
            )

    async def run_channel_automation(self, channel_id: str):
        """Запускает автоматизацию для конкретного канала и обновляет last_run."""
        logger.info("Scheduled automation started for channel %s", channel_id)
        print(f"🔥 Scheduled automation run for channel {channel_id}", flush=True)

        try:
            if USE_AUTOMATION_V2:
                logger.info("Using AutomationManager v2 for channel %s", channel_id)
                result = await automation_manager_v2.run_channel_now(channel_id)
            else:
                logger.info("Using legacy AutomationManager (v1) for channel %s", channel_id)
                result = await automation_manager.run_channel(channel_id)

            db = SessionLocal()
            try:
                schedule = db.query(ChannelScheduleORM).filter(
                    ChannelScheduleORM.channel_id == channel_id
                ).first()
                if schedule:
                    schedule.last_run = datetime.utcnow()
                    db.commit()
            finally:
                db.close()

            logger.info("Scheduled automation completed for channel %s", channel_id)
            return result

        except Exception as e:
            logger.exception("Scheduled automation failed for channel %s", channel_id)
            return {"status": "failed", "error": str(e)}

    def get_next_run(self, channel_id: str):
        if not self.scheduler:
            return None
        job_id = f"channel_{channel_id}"
        job = self.scheduler.get_job(job_id)
        return job.next_run_time if job else None

    async def refresh_schedule(self, channel_id: str):
        if not self.scheduler:
            return

        db = SessionLocal()
        try:
            schedule = db.query(ChannelScheduleORM).filter(
                ChannelScheduleORM.channel_id == channel_id
            ).first()

            if schedule and schedule.is_active:
                await self.add_channel_job(schedule)
            else:
                job_id = f"channel_{channel_id}"
                if self.scheduler.get_job(job_id):
                    self.scheduler.remove_job(job_id)
                    logger.info("Removed inactive schedule for channel %s", channel_id)
        finally:
            db.close()


automation_scheduler = AutomationScheduler()
'''

f = pathlib.Path('backend/automation/scheduler.py')
f.write_text(scheduler_content, encoding='utf-8')

import py_compile
try:
    py_compile.compile(str(f), doraise=True)
    print('✅✅✅ scheduler.py создан заново и валиден')
except py_compile.PyCompileError as e:
    print(f'❌ Ошибка: {e}')
