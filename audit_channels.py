import requests, json

BASE = "http://localhost:8000/api/v1"

print("=== Channel Management E2E audit ===")

# 1. Список каналов
r = requests.get(f"{BASE}/channels/", timeout=10)
print(f"\n[1] GET /channels/ -> {r.status_code}")
channels = r.json() if r.status_code == 200 else []
if isinstance(channels, dict):
    channels = channels.get("channels", channels.get("items", []))
print(f"    channels: {len(channels)}")
for ch in channels[:5]:
    cid = ch.get("id")
    print(f"    - {ch.get('name')} | platform={ch.get('platform')} | automation={ch.get('automation_enabled', ch.get('automation_active', '?'))}")

# 2. Создание тестового канала
payload = {
    "name": "E2E Test Channel 46",
    "platform": "telegram",
    "content_type": "news",
}
r = requests.post(f"{BASE}/channels/", json=payload, timeout=10)
print(f"\n[2] POST /channels/ -> {r.status_code}")
created = r.json() if r.status_code in (200, 201) else {}
new_id = created.get("id")
print(f"    created id: {new_id}")

if new_id:
    # 3. Добавление источника
    r = requests.post(f"{BASE}/channels/{new_id}/sources",
                      json={"source_type": "habr", "config": {}}, timeout=10)
    print(f"\n[3] POST sources -> {r.status_code} {r.text[:120]}")

    # 4. Schedule
    r = requests.get(f"{BASE}/channels/{new_id}/schedule", timeout=10)
    print(f"\n[4] GET schedule -> {r.status_code} {r.text[:120]}")

    # 5. Удаление тестового канала (cleanup)
    r = requests.delete(f"{BASE}/channels/{new_id}", timeout=10)
    print(f"\n[5] DELETE channel -> {r.status_code}")

print("\n=== audit complete ===")