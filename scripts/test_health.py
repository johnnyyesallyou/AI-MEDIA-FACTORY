import sys
import json
sys.path.insert(0, "/app")

from core.health import health_check_endpoint

print("=" * 70)
print("TEST: Health checks")
print("=" * 70)

result = health_check_endpoint()
print(json.dumps(result, indent=2, ensure_ascii=False))

print("\n" + "=" * 70)
print(f"Overall status: {result['status']}")
print("=" * 70)