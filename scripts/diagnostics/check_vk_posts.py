import sys
sys.path.insert(0, '/app')

from backend.automation.publishers.vk import VkPublisher

pub = VkPublisher()
# Пробуем получить последние посты группы через wall.get
import requests

payload = {
    'owner_id': '-240792540',
    'count': 15,
    'access_token': 'vk1.a.Dj8bVmWpOX8sg7fWjqE587ha1F9gP-FuimHxR8e80g18trZ0_dEJWrHG-11dFk4eGEooviCwBFhjFiHKNUIJr-FRW8VmHd3H2r_HVzjA01WwPVZKM_35RFXMr0UcVOZmkIx5FPs2IKNcUcqZedHnIy1peBXvGqt1BzzYI8PDx2WrjyUURG5puU-oa4xHdygSqkH2Ny-191U1FFG3a19OKA',
    'v': '5.199'
}

r = requests.post('https://api.vk.com/method/wall.get', data=payload, timeout=10)
data = r.json()

if 'error' in data:
    print(f'VK API error: {data["error"]}')
else:
    posts = data.get('response', {}).get('items', [])
    print(f'Найдено постов: {len(posts)}')
    for i, post in enumerate(posts[:10], 1):
        text = post.get('text', '')[:80].replace('\\n', ' ')
        post_id = post.get('id')
        print(f'{i}. [{post_id}] {text}...')