import sys, os, json
sys.path.insert(0, "/app")
from engines.monitoring.engine import HealthCheckEngine

engine = HealthCheckEngine(
    ollama_url=os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434")
)
result = engine.run_all()
print(json.dumps(result, indent=2, ensure_ascii=False))