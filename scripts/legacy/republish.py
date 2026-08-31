import sys, time
sys.path.insert(0, "/app")

from backend.automation.jobs.manga_publish_job import MangaPublishJob

print("=" * 70)
print("REPUBLISH: fixed posts")
print("=" * 70)

start = time.time()
job = MangaPublishJob()
result = job.run(limit=10)
elapsed = time.time() - start

print(f"\nElapsed: {elapsed:.1f}s")
print(f"Published: {result.get('published')}")
print("=" * 70)