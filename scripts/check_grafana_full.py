import requests
import json

auth = ('admin', 'admin123')

# 1. Datasources
print("=" * 60)
print("DATASOURCES:")
ds = requests.get('http://amf_grafana:3000/api/datasources', auth=auth, timeout=5).json()
for d in ds:
    print(f"  - {d.get('name')}: type={d.get('type')}, url={d.get('url')}, default={d.get('isDefault')}")

# 2. Dashboards
print("\nDASHBOARDS:")
dash = requests.get('http://amf_grafana:3000/api/search', auth=auth, timeout=5).json()
for d in dash:
    print(f"  - {d.get('title')} (uid={d.get('uid')})")
    print(f"    URL: http://localhost:3002{d.get('url')}")

# 3. Prometheus health через Grafana
print("\nPROMETHEUS через Grafana:")
try:
    r = requests.get('http://amf_grafana:3000/api/datasources/proxy/1/api/v1/query',
                     params={'query': 'amf_jobs_total'}, auth=auth, timeout=5)
    if r.status_code == 200:
        data = r.json().get('data', {}).get('result', [])
        print(f"  Found {len(data)} metric series")
        for s in data[:3]:
            labels = s.get('metric', {})
            value = s.get('value', ['?','?'])[1]
            print(f"    - {labels}: {value}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 60)
print("Откройте: http://localhost:3002/d/amf-overview")
print("=" * 60)