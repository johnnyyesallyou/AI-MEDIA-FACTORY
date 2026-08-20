import requests

BASE = "http://localhost:8000/api/v1/channels"

print("=" * 70)
print("SPRINT 46.2 - TEMPLATES TEST")
print("=" * 70)

# 1. Список шаблонов
print("\n[1] GET /channels/templates")
resp = requests.get(f"{BASE}/templates")
print(f"  Status: {resp.status_code}")
if resp.status_code == 200:
    templates = resp.json()
    print(f"  ✅ Found {len(templates)} templates:")
    for t in templates:
        print(f"     - {t['id']}: {t['name']}")
else:
    print(f"  ❌ Failed: {resp.text}")

# 2. Создать канал из шаблона "news"
print("\n[2] POST /channels/from-template?template_id=news")
resp = requests.post(f"{BASE}/from-template", params={"template_id": "news"})
print(f"  Status: {resp.status_code}")
if resp.status_code == 201:
    channel = resp.json()
    channel_id = channel["id"]
    print(f"  ✅ Channel created: {channel['name']} (ID: {channel_id})")
    
    # 3. Проверить что источники добавлены
    print("\n[3] GET /channels/{id}/sources")
    resp = requests.get(f"{BASE}/{channel_id}/sources")
    if resp.status_code == 200:
        sources = resp.json()
        print(f"  ✅ Sources: {len(sources)}")
        for s in sources:
            print(f"     - {s['name']} ({s['source_type']})")
    
    # 4. Проверить schedule
    print("\n[4] GET /channels/{id}/schedule")
    resp = requests.get(f"{BASE}/{channel_id}/schedule")
    if resp.status_code == 200:
        sched = resp.json()
        print(f"  ✅ Schedule: {sched.get('cron_expression')}, active={sched.get('is_active')}")
    
    # 5. Удалить (cleanup)
    print("\n[5] DELETE /channels/{id}")
    resp = requests.delete(f"{BASE}/{channel_id}")
    print(f"  Status: {resp.status_code}")
    if resp.status_code in (200, 204):
        print(f"  ✅ Deleted")
else:
    print(f"  ❌ Failed: {resp.text}")

print("\n" + "=" * 70)
print("TEMPLATES TEST COMPLETE")
print("=" * 70)