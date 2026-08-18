"""Manga Pipeline Job - объединяет Research + Image + Publish."""
import logging
from typing import Dict, Any

from backend.automation.jobs.manga_research_job import MangaResearchJob
from engines.manga_image_resolver import MangaImageResolver
from backend.automation.jobs.manga_publish_job import MangaPublishJob

logger = logging.getLogger(__name__)


class MangaPipelineJob:
    """
    Sprint 15: Запускает полный цикл манга-постов.
    
    Pipeline:
    1. MangaResearchJob - получает новые главы с ReManga
    2. MangaImageResolver - скачивает обложки
    3. MangaPublishJob - публикует в Telegram
    
    Sprint 15: Manga Chapter Release
    """
    
    def run(self) -> Dict[str, Any]:
        logger.info("=" * 70)
        logger.info("MANGA PIPELINE START")
        logger.info("=" * 70)
        
        results = {
            "research": None,
            "image": None,
            "publish": None,
        }
        
        # Step 1: Research
        try:
            logger.info("[1/3] Running MangaResearchJob...")
            research_job = MangaResearchJob()
            results["research"] = research_job.run(limit_per_source=20)
            logger.info(f"  Result: {results['research']}")
        except Exception as e:
            logger.error(f"  Research failed: {e}")
            results["research"] = {"status": "failed", "error": str(e)}
        
        # Step 2: Image resolver
        try:
            logger.info("[2/3] Running MangaImageResolver...")
            resolver = MangaImageResolver()
            results["image"] = resolver.resolve_all_research(limit=50)
            logger.info(f"  Result: {results['image']}")
        except Exception as e:
            logger.error(f"  Image resolver failed: {e}")
            results["image"] = {"status": "failed", "error": str(e)}
        
        # Step 3: Publish
        try:
            logger.info("[3/3] Running MangaPublishJob...")
            publish_job = MangaPublishJob()
            results["publish"] = publish_job.run(limit=5)
            logger.info(f"  Result: {results['publish']}")
        except Exception as e:
            logger.error(f"  Publish failed: {e}")
            results["publish"] = {"status": "failed", "error": str(e)}
        
        logger.info("=" * 70)
        logger.info("MANGA PIPELINE FINISH")
        logger.info(f"  Research: {results['research'].get('status')}")
        logger.info(f"  Image: {results['image'].get('status')}")
        logger.info(f"  Publish: {results['publish'].get('status')}")
        logger.info("=" * 70)
        
        return results
