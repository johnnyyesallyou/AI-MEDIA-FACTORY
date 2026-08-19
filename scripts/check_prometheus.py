import requests
import json

# Prometheus API: check targets
r = requests.get('http://prometheus:9090/api/v1/targets', timeout=10)
data = r.json()

print(f"Status: {r.status_code}")
active = data.get('data', {}).get('activeTargets', [])
print(f"\nActive targets: {len(active)}")
for t in active:
    labels = t.get('labels', {})
    job = labels.get('job', '?')
    health = t.get('health', '?')
    last_scrape = t.get('lastScrape', '?')
    print(f"  - {job}: {health} (last: {last_scrape[:19] if isinstance(last_scrape, str) else '?'})")

# Check our metrics are being scraped
print("\nQuerying amf_jobs_total:")
q = requests.get('http://prometheus:9090/api/v1/query', params={'query': 'amf_jobs_total'}, timeout=10)
if q.status_code == 200:
    result = q.json().get('data', {}).get('result', [])
    print(f"  Found {len(result)} series")