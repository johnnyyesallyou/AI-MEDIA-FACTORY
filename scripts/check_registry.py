import sys, traceback
sys.path.insert(0, '/app')

print("=" * 70)
print("TESTING ALL IMPORTS FROM jobs_registry.py")
print("=" * 70)

imports = [
    ("JobFactory", "from backend.automation.runtime.job_factory import JobFactory"),
    ("automation_jobs (ResearchJob)", "from backend.automation.jobs.automation_jobs import ResearchJob, DecisionJob, WritingJob, EvaluatorJob, ImageJob, PublishJob"),
    ("NewsResearchJob", "from backend.automation.jobs.news_research_job import NewsResearchJob"),
    ("NewsPublishJob", "from backend.automation.jobs.news_publish_job import NewsPublishJob"),
    ("AnimeResearchJob", "from backend.automation.jobs.anime_research_job import AnimeResearchJob"),
    ("AnimePublishJob", "from backend.automation.jobs.anime_publish_job import AnimePublishJob"),
    ("MangaResearchJob", "from backend.automation.jobs.manga_research_job import MangaResearchJob"),
    ("MangaPublishJob", "from backend.automation.jobs.manga_publish_job import MangaPublishJob"),
    ("MangaEnrichmentJob", "from backend.automation.jobs.manga_enrichment_job import MangaEnrichmentJob"),
    ("RevisionJob", "from backend.automation.jobs.revision_job import RevisionJob"),
    ("ReEvaluationJob", "from backend.automation.jobs.re_evaluation_job import ReEvaluationJob"),
    ("SmartImageAcquisitionJob", "from backend.automation.jobs.smart_image_acquisition_job import SmartImageAcquisitionJob"),
    ("EngagementCollectionJob", "from backend.automation.jobs.engagement_collection_job import EngagementCollectionJob"),
]

for name, stmt in imports:
    try:
        exec(stmt)
        print(f"  OK  {name}")
    except Exception as e:
        print(f"  FAIL {name}: {e}")

print("\n" + "=" * 70)
print("ATTEMPTING FULL import of jobs_registry")
print("=" * 70)
try:
    import backend.automation.runtime.jobs_registry
    from backend.automation.runtime.job_factory import JobFactory
    print(f"After import: {len(JobFactory._registry)} types registered")
    print("Keys:", sorted(JobFactory._registry.keys()))
except Exception as e:
    print(f"FAIL: {e}")
    traceback.print_exc()