import requests
import json

base = 'http://localhost:8000/api/v1'

# Step 1: Suggest
print('=== Step 1: Suggest config ===')
r = requests.post(f'{base}/wizard/suggest', json={'name': 'Манга — новые главы'})
print(f'Status: {r.status_code}')
suggestion = r.json()
print(f'  Suggested: {suggestion}')

# Step 2: Validate
print('\n=== Step 2: Validate config ===')
config = {
    'content_type': suggestion['content_type'],
    'topic': suggestion['topic'],
    'language': suggestion['language'],
    'profile_key': suggestion['profile_key'],
    'sources': suggestion['sources'],
}
r = requests.post(f'{base}/wizard/validate', json=config)
print(f'Status: {r.status_code}')
print(f'  Result: {r.json()}')

# Step 3: Create
print('\n=== Step 3: Create channel ===')
create_req = {
    'name': 'Тестовый манга-канал',
    'config': config,
}
r = requests.post(f'{base}/wizard/create-from-wizard', json=create_req)
print(f'Status: {r.status_code}')
if r.status_code == 201:
    created = r.json()
    print(f'  Created channel: {created["id"]}')
    print(f'  Name: {created["name"]}')
    print(f'  Profile: {created["profile_key"]}')
    print(f'  Sources: {created["sources"]}')
    
    # Step 4: Verify in DB
    print('\n=== Step 4: Verify channel in DB ===')
    r2 = requests.get(f'{base}/channels/{created["id"]}')
    if r2.status_code == 200:
        ch = r2.json()
        print(f'  Channel from DB: {ch["name"]}')
        print(f'  Is active: {ch.get("is_active")}')
    else:
        print(f'  Could not fetch: {r2.status_code}')
else:
    print(f'  Error: {r.text}')

# Step 5: Validate invalid config
print('\n=== Step 5: Validate invalid config (should fail) ===')
bad_config = {
    'content_type': 'manga',
    'topic': 'new_chapters',
    'language': 'ru',
    'profile_key': 'nonexistent_profile',
    'sources': ['remanga', 'fake_source'],
}
r = requests.post(f'{base}/wizard/validate', json=bad_config)
print(f'Status: {r.status_code}')
print(f'  Result: {r.json()}')

print('\n=== Step 6: List all channels ===')
r = requests.get(f'{base}/channels/')
if r.status_code == 200:
    data = r.json()
    print(f'Total channels: {data.get("total", len(data.get("channels", [])))}')
    for ch in data.get('channels', []):
        print(f'  - {ch["name"]}')