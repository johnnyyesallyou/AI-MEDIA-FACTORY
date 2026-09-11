import logging

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

from .runner import AutomationRunner

# Sprint 74.3: skip каналов на паузе (429) даже в legacy run-path (run-now/run-channel)
from backend.core.reliability import channel_paused_for


logger = logging.getLogger(__name__)


class AutomationManager:

    def __init__(self):
        self.runner = AutomationRunner()



    async def run_channel(self, channel_id: str):
        """Запускает автоматизацию для одного конкретного канала."""
        db = SessionLocal()
        try:
            channel = db.query(ChannelORM).filter(ChannelORM.id == channel_id).first()
            if not channel:
                logger.warning("Channel %s not found", channel_id)
                return {"status": "failed", "error": "Channel not found"}
            
            if not channel.is_active:
                logger.info("Channel %s is not active, skipping", channel.name)
                return {"status": "skipped", "reason": "Channel not active"}

            # Sprint 74.3: канал на паузе (429) — не запускаем дорогой pipeline
            paused_for = channel_paused_for(channel)
            if paused_for > 0:
                logger.warning(
                    "Channel %s paused for another %.1fs (429) — run skipped",
                    channel.name, paused_for,
                )
                return {"status": "skipped", "reason": "channel_paused",
                        "remaining_seconds": round(paused_for, 1)}
            
            logger.info("Starting automation for single channel %s", channel.name)
            result = await self.runner.run_now(channel=channel)
            
            return {
                "status": "completed",
                "channel_id": channel.id,
                "channel_name": channel.name,
                "result": result
            }
        finally:
            db.close()

    async def run_all_channels(self):

        db = SessionLocal()

        try:

            channels = (
                db.query(ChannelORM)
                .filter(
                    ChannelORM.is_active == True
                )
                .all()
            )


            logger.info(
                "Automation Manager found %s active channels",
                len(channels)
            )


            results = []


            for channel in channels:

                logger.info(
                    "Starting automation for channel %s",
                    channel.name
                )

                # Sprint 74.3: канал на паузе (429) — не запускаем pipeline
                paused_for = channel_paused_for(channel)
                if paused_for > 0:
                    logger.warning(
                        "Channel %s paused for another %.1fs (429) — skipped",
                        channel.name, paused_for,
                    )
                    results.append(
                        {
                            "channel_id": channel.id,
                            "channel_name": channel.name,
                            "result": {"status": "skipped", "reason": "channel_paused",
                                       "remaining_seconds": round(paused_for, 1)},
                        }
                    )
                    continue

                result = await self.runner.run_now(
                    channel=channel
                )


                results.append(
                    {
                        "channel_id": channel.id,
                        "channel_name": channel.name,
                        "result": result
                    }
                )


            return {
                "status": "completed",
                "channels_processed": len(channels),
                "results": results
            }


        finally:

            db.close()



automation_manager = AutomationManager()