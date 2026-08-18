import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.manga_research_job import MangaResearchJob

print("=" * 70)
print("TEST: MangaResearchJob with MangaRegistry")
print("=" * 70)

job = MangaResearchJob()
result = job.run()

print(f"\nResult: {result}")
print("\n✅ MangaResearchJob works!")
print("=" * 70)