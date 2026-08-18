import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.manga_pipeline_job import MangaPipelineJob

print("=" * 70)
print("FULL PIPELINE WITH TELEGRAPH")
print("=" * 70)

job = MangaPipelineJob()
result = job.run()

print("\n" + "=" * 70)
print("PIPELINE RESULT:")
r = result["research"]
i = result["image"]
p = result["publish"]
print(f"  Research: {r.get('status')} - {r.get('new_chapters', 0)} new items")
print(f"  Image:    {i.get('status')} - {i.get('downloaded', 0)} covers")
print(f"  Publish:  {p.get('status')} - {p.get('published', 0)} posts")

if p.get("published_titles"):
    print("\n  Published titles:")
    for t in p["published_titles"][:5]:
        print(f"    - {t}")
print("=" * 70)
