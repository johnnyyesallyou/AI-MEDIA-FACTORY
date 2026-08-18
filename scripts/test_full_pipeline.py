import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.manga_pipeline_job import MangaPipelineJob

print("=" * 70)
print("PIPELINE TEST: ReManga + MangaDex")
print("=" * 70)

job = MangaPipelineJob()
result = job.run()

print("\n" + "=" * 70)
print("FINAL RESULT:")
r = result["research"]
i = result["image"]
p = result["publish"]
print(f"  Research: {r.get('status')} - {r.get('new_chapters', 0)} new items")
print(f"  Image:    {i.get('status')} - {i.get('downloaded', 0)} covers downloaded")
print(f"  Publish:  {p.get('status')} - {p.get('published', 0)} posts published")
if p.get("published_titles"):
    print("\n  Published titles:")
    for t in p["published_titles"]:
        print(f"    - {t}")
print("=" * 70)
