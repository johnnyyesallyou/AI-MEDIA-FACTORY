import requests

r = requests.get('http://localhost:8000/metrics', timeout=5)
print(f'Status: {r.status_code}')
ct = r.headers.get('content-type', '')
print(f'Content-Type: {ct}')
print('\nFirst AMF metrics:')
lines = r.text.split('\n')
count = 0
for line in lines:
    if line.startswith('amf_') or (line.startswith('#') and 'amf' in line):
        print(f'  {line}')
        count += 1
        if count >= 10:
            break