import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.news_publish_job import NewsPublishJob

print("=" * 70)
print("TEST: NewsPublishJob (3 posts)")
print("=" * 70)

job = NewsPublishJob()
result = job.run(limit=3)

print(f"\nResult: {result}")
print("=" * 70)