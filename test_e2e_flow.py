import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 70)
print("SPRINT 46.1.4 - E2E FLOW TEST (исправленные payloads)")
print("=" * 70)

# 1. Создать канал
print("\n[1/8] POST /channels/ - создание канала")
channel_payload = {
    "name": "E2E Test Channel",
    "platform": "telegram",
    "language_search": "en",
    "language_publish": "ru",
    "style_profile": "minimal",
    "timezone": "UTC",
    "description": "Test channel for E2E flow"
}
resp = requests.post(f"{BASE_URL}/channels/", json=channel_payload)
print(f"  Status: {resp.status_code}")
if resp.status_code == 201:
    channel = resp.json()
    channel_id = channel["id"]
    print(f"  ✅ Channel created: {channel_id}")
else:
    print(f"  ❌ Failed: {resp.text}")
    exit(1)

# 2. Добавить источник знаний (ИСПРАВЛЕНО: url в body, не в config)
print("\n[2/8] POST /channels/{id}/sources - добавление источника")
source_payload = {
    "name": "Hacker News RSS",
    "source_type": "hacker_news",
    "url": "https://news.ycombinator.com/rss",  # ← ИСПРАВЛЕНО: url в body
    "priority": 3
}
resp = requests.post(f"{BASE_URL}/channels/{channel_id}/sources", json=source_payload)
print(f"  Status: {resp.status_code}")
if resp.status_code == 201:
    source = resp.json()
    print(f"  ✅ Source created: {source.get('id', 'N/A')}")
else:
    print(f"  ❌ Failed: {resp.text}")

# 3. Создать schedule
print("\n[3/8] PUT /channels/{id}/schedule - создание расписания")
schedule_payload = {
    "cron_expression": "0 */2 * * *",
    "timezone": "UTC",
    "max_posts_per_day": 10,
    "auto_publish": True,
    "is_active": True
}
resp = requests.put(f"{BASE_URL}/channels/{channel_id}/schedule", json=schedule_payload)
print(f"  Status: {resp.status_code}")
if resp.status_code == 200:
    schedule = resp.json()
    print(f"  ✅ Schedule created: {schedule.get('cron_expression', 'N/A')}")
else:
    print(f"  ❌ Failed: {resp.text}")

# 4. Включить automation (новый endpoint)
print("\n[4/8] POST /channels/{id}/automation/enable - включение автоматизации")
resp = requests.post(f"{BASE_URL}/channels/{channel_id}/automation/enable", 
                     json={"interval_minutes": 120})
print(f"  Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"  ✅ Automation enabled")
else:
    print(f"  ⚠️ Endpoint not found or error: {resp.status_code}")

# 5. Получить полное состояние канала
print("\n[5/8] GET /channels/{id} - полное состояние")
resp = requests.get(f"{BASE_URL}/channels/{channel_id}")
if resp.status_code == 200:
    channel = resp.json()
    print(f"  ✅ Channel: {channel.get('name')}")
    print(f"     Platform: {channel.get('platform')}")
    print(f"     Active: {channel.get('is_active')}")

# 6. Получить schedule
print("\n[6/8] GET /channels/{id}/schedule - проверка расписания")
resp = requests.get(f"{BASE_URL}/channels/{channel_id}/schedule")
if resp.status_code == 200:
    schedule = resp.json()
    print(f"  ✅ Schedule: cron={schedule.get('cron_expression')}, active={schedule.get('is_active')}")

# 7. Получить список sources
print("\n[7/8] GET /channels/{id}/sources - список источников")
resp = requests.get(f"{BASE_URL}/channels/{channel_id}/sources")
if resp.status_code == 200:
    sources = resp.json()
    print(f"  ✅ Sources: {len(sources)} source(s)")
    for s in sources:
        print(f"     - {s.get('name')} ({s.get('source_type')})")

# 8. Удалить канал (с каскадным удалением)
print("\n[8/8] DELETE /channels/{id} - удаление канала")
resp = requests.delete(f"{BASE_URL}/channels/{channel_id}")
print(f"  Status: {resp.status_code}")
if resp.status_code == 204:
    print(f"  ✅ Channel deleted (with cascade)")
else:
    print(f"  ❌ Failed: {resp.text}")

print("\n" + "=" * 70)
print("E2E FLOW TEST COMPLETE")
print("=" * 70)