import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.anime_publish_job import AnimePublishJob

print("=" * 70)
print("TEST: AnimePublishJob (3 posts)")
print("=" * 70)

job = AnimePublishJob()
result = job.run(limit=3)

print(f"\nResult: {result}")
print("=" * 70)