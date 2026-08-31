import requests, json

r = requests.get("http://localhost:8000/api/metrics/system", timeout=15)
print(f"Status: {r.status_code}")
data = r.json()

print("\n[SYSTEM]")
for k, v in data["system"].items():
    print(f"  {k}: {v}")

print("\n[HEALTH]")
print(f"  overall: {data['health']['status']}")
for name, status in data["health"]["components"].items():
    print(f"  {name}: {status}")