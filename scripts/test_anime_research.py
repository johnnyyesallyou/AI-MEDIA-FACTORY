import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.anime_research_job import AnimeResearchJob

print("=" * 70)
print("TEST: AnimeResearchJob")
print("=" * 70)

job = AnimeResearchJob()
result = job.run(limit_per_source=10)

print(f"\nResult: {result}")
print("=" * 70)