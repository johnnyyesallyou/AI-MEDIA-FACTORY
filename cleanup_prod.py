import requests

BASE = "http://localhost:8000/api/v1/channels"
KEEP_MARKERS = ["новост", "anime", "аниме", "манга", "manga", "ai media factory"]

r = requests.get(BASE + "/", timeout=10)
data = r.json()
items = data if isinstance(data, list) else data.get("channels", [])

keep, delete = [], []
for ch in items:
    name = (ch.get("name") or "").lower()
    if any(m in name for m in KEEP_MARKERS):
        keep.append(ch)
    else:
        delete.append(ch)

print("=" * 70)
print("CURRENT CHANNELS (plan)")
print("=" * 70)
for ch in items:
    tag = "KEEP  " if ch in keep else "DELETE"
    print(f"[{tag}] {ch['name']!r:42} platform={ch['platform']:9} connected={ch.get('is_connected')}")

print(f"\nKeep: {len(keep)} | Delete: {len(delete)}")
for ch in delete:
    print(f"  to delete: {ch['name']!r} ({ch['id'][:8]}...)")

ans = input("\nProceed with deletion? (y/n): ").strip().lower()
if ans != "y":
    print("Aborted.")
    raise SystemExit(0)

for ch in delete:
    d = requests.delete(f"{BASE}/{ch['id']}", timeout=10)
    print(f"deleted {ch['name']!r}: {d.status_code}")

# Финальное состояние production-каналов
r = requests.get(BASE + "/", timeout=10)
data = r.json()
items = data if isinstance(data, list) else data.get("channels", [])

print("\n" + "=" * 70)
print("FINAL PRODUCTION CHANNELS")
print("=" * 70)
for ch in items:
    s = requests.get(f"{BASE}/{ch['id']}/schedule", timeout=10)
    sched = s.json() if s.status_code == 200 else None
    nxt = (sched or {}).get("next_run")
    act = (sched or {}).get("is_active")
    print(f"  {ch['name']!r:42} platform={ch['platform']:9} connected={ch.get('is_connected')} schedule_active={act} next_run={nxt}")