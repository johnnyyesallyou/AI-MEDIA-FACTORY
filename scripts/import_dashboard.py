import requests
import json
import uuid

# Загружаем dashboard
with open('/app/monitoring/grafana/dashboards/overview.json') as f:
    dash = json.load(f)

# Меняем UID на случайный (чтобы не конфликтовал с provisioned)
new_uid = 'amf-overview-' + str(uuid.uuid4())[:8]
dash['uid'] = new_uid
dash['id'] = None
dash['title'] = 'AI Media Factory Overview (manual)'

payload = {
    'dashboard': dash,
    'overwrite': True,
    'folderId': 0
}

r = requests.post(
    'http://amf_grafana:3000/api/dashboards/db',
    json=payload,
    auth=('admin', 'admin123'),
    timeout=10
)
print(f"Import: {r.status_code}")
print(f"Response: {r.text[:200]}")

if r.status_code == 200:
    url = r.json().get('url', '')
    print(f"\n✅ Open: http://localhost:3002{url}")