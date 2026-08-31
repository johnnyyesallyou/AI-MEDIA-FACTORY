import requests
base = 'http://localhost:8000/api/v1'

print('=== GET /channels/dashboard ===')
r = requests.get(f'{base}/channels/dashboard')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'  Total: {data["total_channels"]}, Active: {data["active_channels"]}')
    for ch in data["channels"]:
        print(f'  - {ch["name"]} ({ch["content_type"]}): connected={ch["is_connected"]}, published_24h={ch["published_24h"]}')

print('\n=== POST /channels/{id}/start (manga channel) ===')
r = requests.post(f'{base}/channels/manga-channel-001/start')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    print(f'  {r.json()["message"]}')

print('\n=== GET /channels/{id}/status ===')
r = requests.get(f'{base}/channels/manga-channel-001/status')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    status = r.json()
    print(f'  Name: {status["name"]}')
    print(f'  Connected: {status["is_connected"]}')
    print(f'  Today published: {status["today_published"]}')
    print(f'  Schedule: {status["schedule_cron"]}')

print('\n=== POST /channels/{id}/pause ===')
r = requests.post(f'{base}/channels/manga-channel-001/pause')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    print(f'  {r.json()["message"]}')