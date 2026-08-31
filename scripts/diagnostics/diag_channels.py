import requests

BASE = "http://localhost:8000/api/v1/channels"
r = requests.get(BASE + "/", timeout=10)
data = r.json()
items = data if isinstance(data, list) else data.get("channels", [])

print("=" * 70)
print("PRODUCTION CHANNELS DIAGNOSTICS")
print("=" * 70)

for ch in items:
    cid = ch["id"]
    print(f"\n{ch['name']!r} (ID: {cid[:8]}...)")
    print(f"  platform: {ch['platform']}")
    print(f"  connected: {ch.get('is_connected')}")
    print(f"  bot_token: {'SET' if ch.get('telegram_bot_token') or ch.get('vk_access_token') else 'NOT SET'}")
    print(f"  chat_id: {ch.get('telegram_chat_id') or ch.get('vk_group_id') or 'NOT SET'}")
    
    # Schedule
    s = requests.get(f"{BASE}/{cid}/schedule", timeout=10)
    if s.status_code == 200:
        sched = s.json()
        print(f"  schedule: active={sched.get('is_active')}, cron={sched.get('cron_expression')}, next_run={sched.get('next_run')}")
    else:
        print(f"  schedule: NOT FOUND (404)")
    
    # Sources
    src = requests.get(f"{BASE}/{cid}/sources", timeout=10)
    if src.status_code == 200:
        sources = src.json()
        print(f"  sources: {len(sources)}")
        for s in sources:
            print(f"    - {s['name']} ({s['source_type']})")
    else:
        print(f"  sources: ERROR {src.status_code}")