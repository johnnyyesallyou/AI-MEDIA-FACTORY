import requests

# Check Grafana is up
r = requests.get('http://grafana:3000/api/health', timeout=10, auth=('admin', 'admin123'))
print(f"Grafana health: {r.status_code}")
print(f"Response: {r.text}")

# Check datasources
r2 = requests.get('http://grafana:3000/api/datasources', timeout=10, auth=('admin', 'admin123'))
print(f"\nDatasources ({r2.status_code}):")
for ds in r2.json():
    print(f"  - {ds.get('name')}: {ds.get('type')} (default={ds.get('isDefault')})")