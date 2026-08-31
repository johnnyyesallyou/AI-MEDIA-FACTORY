import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.manga_publish_job import MangaPublishJob

print("=" * 70)
print("BULK PUBLISH: все research items")
print("=" * 70)

job = MangaPublishJob()
result = job.run(limit=100)  # берём все

print(f"\nResult: {result}")
print("=" * 70)