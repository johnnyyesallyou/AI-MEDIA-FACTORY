import requests
base = 'http://localhost:8000/api/v1'

print('=== GET /posts/history/{channel_id} ===')
r = requests.get(f'{base}/posts/history/manga-channel-001')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    posts = r.json()
    print(f'  Posts count: {len(posts)}')
else:
    print(f'  Response: {r.text[:200]}')

print('\n=== GET /posts/metrics/{channel_id} ===')
r = requests.get(f'{base}/posts/metrics/manga-channel-001')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    metrics = r.json()
    print(f'  Period: {metrics["period_days"]} days')
    print(f'  Total posts: {metrics["total_posts"]}')
    print(f'  Total views: {metrics["total_views"]}')
    print(f'  Top patterns: {metrics["top_patterns"]}')

print('\n=== GET /posts/learnings/{channel_id} ===')
r = requests.get(f'{base}/posts/learnings/manga-channel-001')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    learnings = r.json()
    print(f'  Learnings count: {len(learnings)}')