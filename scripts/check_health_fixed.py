import requests
import json

print('=' * 70)
print('HEALTH CHECK AFTER FIXES')
print('=' * 70)

r = requests.get('http://localhost:8000/api/health/summary', timeout=10)
data = r.json()

print(f"\nOverall status: {data['status'].upper()}")
print(f"OK: {data['components_ok']}")
print(f"DEGRADED: {data['components_degraded']}")
print(f"ERROR: {data['components_error']}")

print('\n[DETAILED]')
r = requests.get('http://localhost:8000/api/health', timeout=10)
data = r.json()

for name, comp in data['components'].items():
    status = comp['status'].upper()
    emoji = {'OK':'[OK]', 'DEGRADED':'[WARN]', 'ERROR':'[FAIL]'}.get(status, '?')
    print(f'  {emoji} {name}: {status}')
    
    if name == 'sources' and 'available' in comp:
        print(f'    Available: {comp["available"]}/{comp["total"]}')
        # Показать проблемные
        for src_name, src_detail in comp.get('details', {}).items():
            if src_detail.get('status') != 'ok':
                print(f'      {src_name}: {src_detail.get("status")} (code={src_detail.get("status_code")})')
    elif name == 'publishers' and 'available' in comp:
        print(f'    Available: {comp["available"]}/{comp["total"]}')
        for pub_name, pub_detail in comp.get('details', {}).items():
            print(f'      {pub_name}: {pub_detail.get("status")} ({pub_detail.get("reason", pub_detail.get("error", ""))})')
    elif name == 'automation' and 'channels' in comp:
        ch = comp['channels']
        print(f'    Total: {ch["total"]}, Active: {ch["active"]}, Paused: {ch["paused"]}')
        if 'recent_posts_24h' in comp:
            print(f'    Recent posts (24h): {comp["recent_posts_24h"]}')

print('=' * 70)