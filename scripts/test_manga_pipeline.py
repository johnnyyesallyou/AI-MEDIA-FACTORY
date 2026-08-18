import sys
sys.path.insert(0, "/app")

from backend.automation.jobs.manga_pipeline_job import MangaPipelineJob

print("=" * 70)
print("TESTING MangaPipelineJob")
print("=" * 70)

job = MangaPipelineJob()
result = job.run()

print("\n" + "=" * 70)
print("PIPELINE RESULT:")
print(f"  Research: {result['research'].get('status')} - {result['research']}")
print(f"  Image:    {result['image'].get('status')} - {result['image']}")
print(f"  Publish:  {result['publish'].get('status')} - {result['publish']}")
print("=" * 70)
