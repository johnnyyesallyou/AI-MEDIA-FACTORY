import requests
base = 'http://localhost:8000/api/v1'

print('=== GET /sources/ ===')
r = requests.get(f'{base}/sources/')
print(f'Status: {r.status_code}, count: {len(r.json())}')

print('\n=== GET /sources/?content_type=manga ===')
r = requests.get(f'{base}/sources/', params={'content_type': 'manga'})
print(f'Status: {r.status_code}, count: {len(r.json())}')
for s in r.json():
    print(f'  - {s["id"]}: {s["capabilities"]}')

print('\n=== GET /sources/remanga ===')
r = requests.get(f'{base}/sources/remanga')
print(f'Status: {r.status_code}')
print(f'  name: {r.json()["name"]}')
print(f'  capabilities: {r.json()["capabilities"]}')

print('\n=== POST /sources/validate ===')
r = requests.post(f'{base}/sources/validate', json=['remanga', 'invalid'])
print(f'Status: {r.status_code}')
print(f'  result: {r.json()}')