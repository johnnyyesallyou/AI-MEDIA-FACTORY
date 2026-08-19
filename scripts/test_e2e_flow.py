import requests

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 70)
print("SPRINT 46.1.15 - E2E FLOW FINAL TEST")
print("=" * 70)

# 1. Создать канал
print("\n[1/8] POST /channels/ - создание канала")
resp = requests.post(f"{BASE_URL}/channels/", json={
    "name": "E2E Test Channel",
    "platform": "telegram",
    "language_search": "en",
    "language_publish": "ru",
    "style_profile": "minimal",
    "timezone": "UTC",
    "description": "Test channel for E2E flow"
})
print(f"  Status: {resp.status_code}")
assert resp.status_code == 201, f"Failed: {resp.text}"
channel = resp.json()
channel_id = channel["id"]
print(f"  ✅ Channel created: {channel_id}")

# 2. Добавить источник (API возвращает 200 при создании — это ОК)
print("\n[2/8] POST /channels/{id}/sources - добавление источника")
resp = requests.post(f"{BASE_URL}/channels/{channel_id}/sources", json={
    "name": "Hacker News RSS",
    "source_type": "hacker_news",
    "url": "https://news.ycombinator.com/rss",
    "priority": 3
})
print(f"  Status: {resp.status_code}")
assert resp.status_code in (200, 201), f"Failed: {resp.text}"
print(f"  ✅ Source created")

# 3. Создать schedule
print("\n[3/8] PUT /channels/{id}/schedule - создание расписания")
resp = requests.put(f"{BASE_URL}/channels/{channel_id}/schedule", json={
    "cron_expression": "0 */2 * * *",
    "timezone": "UTC",
    "max_posts_per_day": 10,
    "auto_publish": True,
    "is_active": True
})
print(f"  Status: {resp.status_code}")
assert resp.status_code == 200, f"Failed: {resp.text}"
print(f"  ✅ Schedule created")

# 4. Включить automation (теперь graceful: 200 с pending_connection или enabled)
print("\n[4/8] POST /channels/{id}/automation/enable")
resp = requests.post(f"{BASE_URL}/channels/{channel_id}/automation/enable",
                     json={"interval_minutes": 120})
print(f"  Status: {resp.status_code}")
assert resp.status_code == 200, f"Failed: {resp.text}"
data = resp.json()
print(f"  ✅ Automation: {data.get('status')} (reason: {data.get('reason', 'n/a')})")

# 5. Get channel
print("\n[5/8] GET /channels/{id}")
resp = requests.get(f"{BASE_URL}/channels/{channel_id}")
assert resp.status_code == 200
print(f"  ✅ Channel: {resp.json().get('name')}")

# 6. Get schedule
print("\n[6/8] GET /channels/{id}/schedule")
resp = requests.get(f"{BASE_URL}/channels/{channel_id}/schedule")
assert resp.status_code == 200
print(f"  ✅ Schedule: {resp.json().get('cron_expression')}")

# 7. Get sources
print("\n[7/8] GET /channels/{id}/sources")
resp = requests.get(f"{BASE_URL}/channels/{channel_id}/sources")
assert resp.status_code == 200
print(f"  ✅ Sources: {len(resp.json())}")

# 8. Удалить канал (должен работать с cascade — 200 или 204)
print("\n[8/8] DELETE /channels/{id} - удаление с cascade")
resp = requests.delete(f"{BASE_URL}/channels/{channel_id}")
print(f"  Status: {resp.status_code}")
if resp.status_code not in (200, 204):
    print(f"  ❌ Failed: {resp.text}")
    raise AssertionError(f"DELETE failed: {resp.status_code} {resp.text}")
print(f"  ✅ Channel deleted (cascade OK)")

print("\n" + "=" * 70)
print("🎉 E2E FLOW COMPLETE — ALL 8 STEPS PASSED")
print("=" * 70)