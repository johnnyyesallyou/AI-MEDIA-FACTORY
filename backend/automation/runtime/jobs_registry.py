"""Jobs Registry - Sprint 48.

Регистрирует все Job классы (через адаптеры для legacy jobs).
"""
import logging
from backend.automation.runtime.job_factory import JobFactory
from backend.automation.runtime.job_adapters import (
    ResearchJobAdapter, DecisionJobAdapter, WritingJobAdapter,
    EvaluatorJobAdapter, ImageJobAdapter, PublishJobAdapter
)
from backend.automation.jobs.news_research_job import NewsResearchJob
from backend.automation.jobs.news_publish_job import NewsPublishJob
from backend.automation.jobs.anime_research_job import AnimeResearchJob
from backend.automation.jobs.anime_publish_job import AnimePublishJob
from backend.automation.jobs.manga_research_job import MangaResearchJob
from backend.automation.jobs.manga_publish_job import MangaPublishJob
from backend.automation.jobs.manga_enrichment_job import MangaEnrichmentJob
from backend.automation.jobs.revision_job import RevisionJob
from backend.automation.jobs.re_evaluation_job import ReEvaluationJob
from backend.automation.jobs.smart_image_acquisition_job import SmartImageAcquisitionJob
from backend.automation.jobs.engagement_collection_job import EngagementCollectionJob

logger = logging.getLogger(__name__)


def register_all_jobs():
    """Регистрирует все Job классы в JobFactory."""
    # Базовые типы через АДАПТЕРЫ (legacy -> v2 contract)
    JobFactory.register("research", ResearchJobAdapter)
    JobFactory.register("decision", DecisionJobAdapter)
    JobFactory.register("writing", WritingJobAdapter, aliases=["brief"])
    JobFactory.register("evaluation", EvaluatorJobAdapter, aliases=["evaluator"])
    JobFactory.register("publish", PublishJobAdapter, aliases=["publisher"])
    JobFactory.register("image", ImageJobAdapter)
    
    # Специализированные типы (надеюсь они уже v2-compatible)
    JobFactory.register("news_research", NewsResearchJob)
    JobFactory.register("news_publish", NewsPublishJob)
    JobFactory.register("anime_research", AnimeResearchJob)
    JobFactory.register("anime_publish", AnimePublishJob)
    JobFactory.register("manga_research", MangaResearchJob)
    JobFactory.register("manga_publish", MangaPublishJob)
    JobFactory.register("manga_enrichment", MangaEnrichmentJob)
    
    # Вспомогательные
    JobFactory.register("revision", RevisionJob)
    JobFactory.register("re_evaluation", ReEvaluationJob)
    JobFactory.register("smart_image", SmartImageAcquisitionJob)
    JobFactory.register("engagement_collection", EngagementCollectionJob)
    
    logger.info(f"JobFactory registry loaded: {len(JobFactory._registry)} types (with adapters)")
    print(f"✅ JobFactory registered {len(JobFactory._registry)} job types (with adapters)")


register_all_jobs()