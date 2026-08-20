import requests
try:
    r = requests.get('http://localhost:8000/api/v1/metrics/debug/jobs', timeout=10)
    print('Status:', r.status_code)
    if r.status_code == 200:
        data = r.json()
        print('count:', data['count'])
        print('keys:', data['keys'])
    else:
        print('Error:', r.text)
except Exception as e:
    print('Network error:', e)