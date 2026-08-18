import sys, json
sys.path.insert(0, "/app")
from backend.automation.jobs.monitoring_job import MonitoringJob
result = MonitoringJob().run()
print(json.dumps(result, indent=2, ensure_ascii=False, default=str))