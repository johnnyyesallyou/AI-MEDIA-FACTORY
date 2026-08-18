import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.manga_publish_job import MangaPublishJob

print("=" * 70)
print("PUBLISHING WITH TELEGRAPH URL")
print("=" * 70)

job = MangaPublishJob()
result = job.run(limit=3)

print("\n" + "=" * 70)
print(f"RESULT: {result}")
if result.get("published_titles"):
    print("\nPublished titles:")
    for title in result["published_titles"]:
        print(f"  - {title}")
print("=" * 70)
