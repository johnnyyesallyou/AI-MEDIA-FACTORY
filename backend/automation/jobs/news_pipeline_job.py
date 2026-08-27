"""News Pipeline Job - Sprint 52B.

Orchestrates news pipeline: research → (optional writing) → publish.

Pipeline:
  1. NewsResearchJob - fetches RSS (habr/vc/3dnews/ixbt) → NewsArticle + ContentORM
  2. NewsPublishJob - publishes to Telegram with images + Telegraph

NewsResearchJob уже создаёт ContentORM записи со status=research.
NewsPublishJob публикует их с картинками через Publishing Layer.
"""
import logging
from typing import Dict, Any

from backend.automation.jobs.news_research_job import NewsResearchJob
from backend.automation.jobs.news_publish_job import NewsPublishJob

logger = logging.getLogger(__name__)


class NewsPipelineJob:
    """Orchestrates news pipeline: research → publish."""

    def run(self, channel=None) -> Dict[str, Any]:
        logger.info("NewsPipelineJob started")

        try:
            # Step 1: Research (fetch RSS → ContentORM)
            logger.info("[1/2] Running NewsResearchJob...")
            research_job = NewsResearchJob()
            research_result = research_job.run(channel=channel)
            logger.info(f"[1/2] Research completed: {research_result}")

            # Step 2: Publish
            logger.info("[2/2] Running NewsPublishJob...")
            publish_job = NewsPublishJob()
            publish_result = publish_job.run(channel=channel)
            logger.info(f"[2/2] Publish completed: {publish_result}")

            return {
                "status": "ok",
                "research": research_result,
                "publish": publish_result,
            }

        except Exception as e:
            logger.exception(f"NewsPipelineJob failed: {e}")
            return {"status": "failed", "error": str(e)}