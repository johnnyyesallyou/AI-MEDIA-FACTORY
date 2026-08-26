import sys
sys.path.insert(0, '/app')
from backend.automation.jobs.anime_pipeline_job import AnimePipelineJob

print("Running AnimePipelineJob...")
job = AnimePipelineJob()
result = job.run()
print(f"Result: {result}")