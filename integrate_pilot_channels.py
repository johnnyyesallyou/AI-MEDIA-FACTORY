"""Sprint 69.1: Интеграция 10 pilot каналов в AI Media Factory.

Читает pilot_channels.json → создаёт profiles + channels + assign + smoke test.
"""
import json
import time
import requests
from pathlib import Path

BASE = "http://localhost:8000/api/v1"

# 1. Проверяем что backend жив
print("[1/5] Проверка backend...")
try:
    r = requests.get(f"{BASE}/channels/", timeout=5)
    print(f"  ✅ Backend OK (channels: {r.json().get('total', '?')})")
except Exception as e:
    print(f"  ❌ Backend недоступен: {e}")
    exit(1)

# 2. Загружаем pilot_channels.json
data = json.loads(Path("pilot_channels.json").read_text(encoding="utf-8"))
channels = data["channels"]
print(f"[2/5] Загружено {len(channels)} каналов из pilot_channels.json")

# 3. Создаём profiles + channels + assign
results = []
print(f"\n[3/5] Создание profiles + channels + assign...")

for i, ch in enumerate(channels, 1):
    print(f"\n  [{i}/{len(channels)}] {ch['title']}")
    
    # 3a. Создаём profile из шаблона
    overrides = {
        "name": f"Pilot: {ch['title']}",
        "theme": ch["theme"],
        "niche": ch["niche"],
        "description": ch.get("about", ""),
    }
    
    # Mode override в publishing
    if ch["mode"]:
        overrides["publishing"] = {"mode": ch["mode"]}
    
    r = requests.post(
        f"{BASE}/profiles/from-template/{ch['template']}",
        json=overrides,
        timeout=30,
    )
    
    if r.status_code == 201:
        profile_id = r.json()["id"]
        print(f"    ✅ Profile created: {profile_id[:12]}...")
    elif r.status_code == 409:
        # Уже существует — ищем по имени
        r2 = requests.get(f"{BASE}/profiles/?limit=100", timeout=30)
        prof = next((p for p in r2.json()["profiles"] if p["name"] == overrides["name"]), None)
        if prof:
            profile_id = prof["id"]
            print(f"    [i] Profile exists: {profile_id[:12]}...")
        else:
            print(f"    ❌ Profile conflict but not found: {r.text[:100]}")
            results.append((ch["title"], "FAILED", None, None))
            continue
    else:
        print(f"    ❌ Profile creation failed: {r.status_code} {r.text[:150]}")
        results.append((ch["title"], "FAILED", None, None))
        continue
    
    # 3b. Создаём channel
    channel_payload = {
        "name": ch["title"],
        "platform": "telegram",
        "language_search": "en",
        "language_publish": "ru",
        "style_profile": "minimal",
        "timezone": "UTC",
        "description": ch.get("about", ""),
        "bot_token": ch["bot_token"],
        "chat_id": str(ch["bot_chat_id"]),
    }
    
    r = requests.post(f"{BASE}/channels/", json=channel_payload, timeout=30)
    if r.status_code == 201:
        channel_id = r.json()["id"]
        print(f"    ✅ Channel created: {channel_id[:12]}...")
    elif r.status_code in (400, 409):
        # Уже существует — ищем по имени
        r2 = requests.get(f"{BASE}/channels/", timeout=30)
        chan = next((c for c in r2.json().get("channels", []) if c["name"] == ch["title"]), None)
        if chan:
            channel_id = chan["id"]
            print(f"    [i] Channel exists: {channel_id[:12]}...")
        else:
            print(f"    ❌ Channel conflict but not found: {r.text[:150]}")
            results.append((ch["title"], "FAILED", profile_id, None))
            continue
    else:
        print(f"    ❌ Channel creation failed: {r.status_code} {r.text[:150]}")
        results.append((ch["title"], "FAILED", profile_id, None))
        continue
    
    # 3c. Assign profile to channel
    r = requests.post(f"{BASE}/profiles/{profile_id}/assign/{channel_id}", timeout=30)
    if r.status_code == 200:
        print(f"    ✅ Profile assigned")
    else:
        print(f"    ⚠️  Assign: {r.status_code} {r.text[:100]}")
    
    results.append((ch["title"], "OK", profile_id, channel_id))

# 4. Smoke test: запускаем pipeline для каждого канала
print(f"\n[4/5] Smoke test: запуск /pipeline/{{id}}/run-universal для каждого канала...")
smoke_results = []
for title, status, prof_id, chan_id in results:
    if status != "OK" or not chan_id:
        smoke_results.append((title, "SKIP"))
        continue
    
    r = requests.post(f"{BASE}/pipeline/{chan_id}/run-universal", timeout=30)
    if r.status_code == 200:
        j = r.json()
        print(f"  ✅ {title}: {j.get('status')} (archetype={j.get('archetype')})")
        smoke_results.append((title, "OK"))
    else:
        print(f"  ⚠️  {title}: {r.status_code} {r.text[:100]}")
        smoke_results.append((title, f"WARN:{r.status_code}"))

# 5. Итоговая сводка
print(f"\n{'='*80}")
print(f"[5/5] Итоговая сводка Sprint 69.1")
print(f"{'='*80}")
ok = sum(1 for _, s, _, _ in results if s == "OK")
failed = sum(1 for _, s, _, _ in results if s == "FAILED")
smoke_ok = sum(1 for _, s in smoke_results if s == "OK")

print(f"  Channels created: {ok}/10")
print(f"  Failed: {failed}/10")
print(f"  Smoke test OK: {smoke_ok}/{ok}")
print(f"\n{'='*80}")
print(f"📋 Детали:")
print(f"{'#':<3} {'Channel':<30} {'Status':<8} {'Mode':<20}")
print("-" * 80)
for i, (title, status, _, _) in enumerate(results, 1):
    mode = next((c["mode"] for c in channels if c["title"] == title), "?")
    print(f"{i:<3} {title:<30} {status:<8} {mode:<20}")

print(f"\n{'='*80}")
if failed == 0 and smoke_ok >= ok * 0.8:
    print(f"✅ SPRINT 69.1 READY FOR COMMIT")
else:
    print(f"⚠️  Есть проблемы — нужно проверить")
print(f"{'='*80}")

# Сохраняем результат
with open("pilot_integration_result.json", "w", encoding="utf-8") as f:
    json.dump({
        "total_channels": len(channels),
        "created": ok,
        "failed": failed,
        "smoke_ok": smoke_ok,
        "results": [
            {"title": t, "status": s, "profile_id": p, "channel_id": c, "mode": ch_mode}
            for (t, s, p, c), ch_mode in zip(results, [ch["mode"] for ch in channels])
        ],
    }, f, indent=2, ensure_ascii=False)
print(f"\n📁 Результат сохранён в pilot_integration_result.json")