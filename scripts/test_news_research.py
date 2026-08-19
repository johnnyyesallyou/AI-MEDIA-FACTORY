import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.news_research_job import NewsResearchJob

print("=" * 70)
print("TEST: NewsResearchJob (Habr only, limit=5)")
print("=" * 70)

job = NewsResearchJob()
result = job.run(limit_per_source=5, sources=["habr"])

print(f"\nResult: {result}")
print("=" * 70)