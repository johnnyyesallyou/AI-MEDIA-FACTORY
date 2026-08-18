import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.manga_research_job import MangaResearchJob

print("=" * 70)
print("E2E TEST: Run #1 (clean DB)")
print("=" * 70)

job = MangaResearchJob()
result = job.run(limit_per_source=10)

print(f"\nResult: {result}")
print("=" * 70)