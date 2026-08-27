import requests
base = 'http://localhost:8000/api/v1'

print('=== POST /wizard/suggest (manga) ===')
r = requests.post(f'{base}/wizard/suggest', json={'name': 'Манга — новые главы'})
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'  content_type: {data["content_type"]}')
    print(f'  topic: {data["topic"]}')
    print(f'  profile_key: {data["profile_key"]}')
    print(f'  sources: {data["sources"]}')
    print(f'  confidence: {data["confidence"]}')
else:
    print(f'  Error: {r.text}')

print('\n=== POST /wizard/suggest (anime) ===')
r = requests.post(f'{base}/wizard/suggest', json={'name': 'Anime news'})
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'  content_type: {data["content_type"]}')
    print(f'  sources: {data["sources"]}')

print('\n=== POST /wizard/suggest (news) ===')
r = requests.post(f'{base}/wizard/suggest', json={'name': 'Новости технологий'})
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'  content_type: {data["content_type"]}')
    print(f'  topic: {data["topic"]}')
    print(f'  sources: {data["sources"]}')

print('\n=== POST /wizard/suggest (unknown) ===')
r = requests.post(f'{base}/wizard/suggest', json={'name': 'Мой канал'})
print(f'Status: {r.status_code}')
if r.status_code == 400:
    print(f'  Error (expected): {r.json()["detail"]}')