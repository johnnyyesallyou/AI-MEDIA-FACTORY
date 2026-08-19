import requests
import time

print('=' * 60)
print('FINAL VERIFICATION: AI Media Factory Monitoring')
print('=' * 60)

# [1] Health check
print('\n[1] Health check:')
try:
    r = requests.get('http://localhost:8000/health', timeout=5)
    print(f'  Status: {r.status_code}')
    if r.status_code == 200:
        print('  ✅ Backend is healthy!')
except Exception as e:
    print(f'  ❌ Error: {e}')

# [2] /metrics endpoint
print('\n[2] /metrics endpoint:')
try:
    r = requests.get('http://localhost:8000/metrics', timeout=5)
    print(f'  Status: {r.status_code} (len={len(r.text)})')
    if r.status_code == 200:
        print('  ✅ Metrics endpoint works!')
        lines = [l for l in r.text.split('\n') if l.startswith('amf_')][:3]
        if lines:
            print('  Sample metrics:')
            for l in lines:
                print(f'    {l}')
        else:
            print('  (no amf_* metrics yet - will appear after first job)')
except Exception as e:
    print(f'  ❌ Error: {e}')

# [3] Prometheus targets
print('\n[3] Prometheus targets:')
try:
    r = requests.get('http://amf_prometheus:9090/api/v1/targets', timeout=5)
    data = r.json()
    active = data.get('data', {}).get('activeTargets', [])
    print(f'  Active targets: {len(active)}')
    for t in active:
        job = t.get('labels', {}).get('job', '?')
        health = t.get('health', '?')
        emoji = '✅' if health == 'up' else '⚠️'
        print(f'    {emoji} {job}: {health}')
except Exception as e:
    print(f'  ❌ Error: {e}')

# [4] Grafana health
print('\n[4] Grafana:')
try:
    r = requests.get('http://amf_grafana:3000/api/health', timeout=5)
    print(f'  Status: {r.status_code}')
    if r.status_code == 200:
        print('  ✅ Grafana is running!')
except Exception as e:
    print(f'  ❌ Error: {e}')

# [5] List installed packages
print('\n[5] Key packages:')
try:
    import bs4
    print(f'  ✅ bs4: {bs4.__version__}')
except: print('  ❌ bs4: not found')

try:
    import prometheus_client
    print(f'  ✅ prometheus_client: installed')
except: print('  ❌ prometheus_client: not found')

try:
    import torch
    print(f'  ✅ torch: {torch.__version__} (CUDA: {torch.cuda.is_available()})')
except: print('  ❌ torch: not found')

print('\n' + '=' * 60)
print('VERIFICATION COMPLETE')
print('=' * 60)