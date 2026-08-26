import sys
sys.path.insert(0, '/app')

from backend.automation.jobs.manga_pipeline_job import MangaPipelineJob

print("Running MangaPipelineJob...")
job = MangaPipelineJob()
result = job.run()
print(f"Result: {result}")