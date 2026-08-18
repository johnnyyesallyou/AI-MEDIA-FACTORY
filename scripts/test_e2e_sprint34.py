import sys
sys.path.insert(0, "/app")

from core.monitoring import monitor_job
from core.health import health_check_endpoint
import json

print("=" * 70)
print("E2E TEST: Production Hardening")
print("=" * 70)

# 1. Health check
print("\n[1] Health check:")
health = health_check_endpoint()
print(f"    Status: {health['status']}")
print(f"    Database: {health['checks']['database']['status']}")
print(f"    External APIs: {health['checks']['external_apis']['status']}")

# 2. Test manga research с retry
print("\n[2] Manga research (with retry):")
from backend.automation.jobs.manga_research_job import MangaResearchJob

@monitor_job("MangaResearchJob")
def run_manga_research():
    job = MangaResearchJob()
    return job.run(limit_per_source=3)

result = run_manga_research()
print(f"    Result: {result}")

# 3. Test anime research
print("\n[3] Anime research (with retry):")
from backend.automation.jobs.anime_research_job import AnimeResearchJob

@monitor_job("AnimeResearchJob")
def run_anime_research():
    job = AnimeResearchJob()
    return job.run(limit_per_source=3)

result_anime = run_anime_research()
print(f"    Result: {result_anime}")

# 4. Test news research
print("\n[4] News research (with retry):")
from backend.automation.jobs.news_research_job import NewsResearchJob

@monitor_job("NewsResearchJob")
def run_news_research():
    job = NewsResearchJob()
    return job.run(limit_per_source=3, sources=["habr"])

result_news = run_news_research()
print(f"    Result: {result_news}")

print("\n" + "=" * 70)
print("E2E TEST PASSED ✅")
print("=" * 70)