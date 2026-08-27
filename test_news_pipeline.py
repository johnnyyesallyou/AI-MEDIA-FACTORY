import sys
sys.path.insert(0, '/app')
from backend.automation.jobs.news_pipeline_job import NewsPipelineJob

print("Running NewsPipelineJob...")
job = NewsPipelineJob()
result = job.run()
print(f"\nResult: {result}")