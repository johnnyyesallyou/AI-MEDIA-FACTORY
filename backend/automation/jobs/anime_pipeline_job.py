"""Anime Pipeline Job - Sprint 51.

Pipeline:
  1. AnimeResearchJob - получает новые эпизоды
  2. AnimePublishJob - публикует в Telegram с key visual
"""
import logging
from typing import Dict, Any

from backend.automation.jobs.anime_research_job import AnimeResearchJob
from backend.automation.jobs.anime_publish_job import AnimePublishJob

logger = logging.getLogger(__name__)


class AnimePipelineJob:
    """Orchestrates anime pipeline: research → publish."""

    def run(self, channel=None) -> Dict[str, Any]:
        logger.info("AnimePipelineJob started")

        try:
            # Step 1: Research
            logger.info("[1/2] Running AnimeResearchJob...")
            research_job = AnimeResearchJob()
            research_result = research_job.run(channel=channel)
            logger.info(f"[1/2] Research completed: {research_result}")

            # Step 2: Publish
            logger.info("[2/2] Running AnimePublishJob...")
            publish_job = AnimePublishJob()
            publish_result = publish_job.run(channel=channel)
            logger.info(f"[2/2] Publish completed: {publish_result}")

            return {
                "status": "ok",
                "research": research_result,
                "publish": publish_result,
            }

        except Exception as e:
            logger.exception(f"AnimePipelineJob failed: {e}")
            return {"status": "failed", "error": str(e)}