import requests
import json

endpoints = {
    "database": "http://localhost:8000/api/health/database",
    "sources": "http://localhost:8000/api/health/sources",
    "publishers": "http://localhost:8000/api/health/publishers",
    "automation": "http://localhost:8000/api/health/automation",
    "metrics": "http://localhost:8000/api/health/metrics",
}

print("=" * 70)
print("DETAILED HEALTH DIAGNOSTICS")
print("=" * 70)

for name, url in endpoints.items():
    print(f"\n[{name.upper()}]")
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        
        status = data.get("status", "unknown").upper()
        emoji = {"OK":"✓", "DEGRADED":"⚠", "ERROR":"✗"}.get(status, "?")
        
        print(f"  Status: {emoji} {status}")
        
        if "latency_ms" in data:
            print(f"  Latency: {data['latency_ms']}ms")
        
        if "details" in data:
            details = data["details"]
            if isinstance(details, dict):
                for key, value in list(details.items())[:5]:
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for k2, v2 in list(value.items())[:3]:
                            print(f"    {k2}: {v2}")
                    else:
                        print(f"  {key}: {value}")
        
        if "error" in data:
            print(f"  Error: {data['error']}")
            
        if "available" in data and "total" in data:
            print(f"  Available: {data['available']}/{data['total']}")
            
    except Exception as e:
        print(f"  ✗ Request failed: {type(e).__name__}: {e}")

print("\n" + "=" * 70)