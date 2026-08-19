import requests

for code in (429, 404, 401):
    try:
        r = requests.get(f"https://httpbin.org/status/{code}", timeout=8)
        print(f"[{code}] no exception, got status: {r.status_code}")
        r.raise_for_status()
    except Exception as e:
        resp = getattr(e, "response", None)
        print(f"[{code}] type={type(e).__name__} | isinstance_HTTPError={isinstance(e, requests.HTTPError)} | response={resp.status_code if resp is not None else None}")