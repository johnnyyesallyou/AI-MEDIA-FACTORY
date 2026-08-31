import sys
sys.path.insert(0, '/app')
from backend.automation.jobs.image_job import ImageJob

job = ImageJob()
result = job.run(channel=None, execution_id='test-final')

print('\\n=== Результат ImageJob ===')
for key, value in result.items():
    print(f'   {key}: {value}')