import requests

r = requests.get("http://localhost:8000/api/v1/channels/", timeout=10)
chs = r.json()
items = chs if isinstance(chs, list) else chs.get("channels", [])
for ch in items:
    if ch["name"].startswith("E2E Test"):
        d = requests.delete("http://localhost:8000/api/v1/channels/" + ch["id"], timeout=10)
        print("deleted", ch["name"], d.status_code)
print("remaining channels:", len(items))