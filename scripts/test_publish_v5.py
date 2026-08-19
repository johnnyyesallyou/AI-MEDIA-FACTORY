import sys
sys.path.insert(0, "/app")
from backend.automation.jobs.manga_publish_job import MangaPublishJob

print("=" * 70)
print("TEST: MangaPublishJob v5 (Publishing Layer) - 3 posts")
print("=" * 70)

job = MangaPublishJob()
result = job.run(limit=3)

print(f"\nResult: {result}")
print("=" * 70)