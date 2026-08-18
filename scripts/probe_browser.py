import requests
import json
import os
import subprocess

print("=" * 70)
print("TELEGRAPH UPLOAD - BROWSER HEADERS + CURL FALLBACK")
print("=" * 70)

test_image = "/app/assets/2026/08/d99baea8-86a7-42bd-a980-02de66052f18.jpg"

# ??????? 1: Browser-like headers
print("\n" + "="*70)
print("VARIANT 1: Browser-like headers (requests)")
print("="*70)

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru,en;q=0.9",
    "Origin": "https://telegra.ph",
    "Referer": "https://telegra.ph/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
}

with open(test_image, "rb") as f:
    files = {"file": ("image.jpg", f, "image/jpeg")}
    r = requests.post(
        "https://telegra.ph/upload",
        files=files,
        headers=BROWSER_HEADERS,
        timeout=30
    )

print(f"Status: {r.status_code}")
print(f"Response: {r.text[:200]}")

if r.status_code == 200:
    try:
        data = r.json()
        print(f"\n? SUCCESS: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"ERROR parsing: {e}")

# ??????? 2: curl (??????? requests ??????????)
print("\n" + "="*70)
print("VARIANT 2: curl (system-level)")
print("="*70)

try:
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://telegra.ph/upload",
        "-F", f"file=@{test_image};type=image/jpeg",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "-H", "Origin: https://telegra.ph",
        "-H", "Referer: https://telegra.ph/",
        "-w", "\nHTTP_CODE:%{http_code}",
    ]
    
    print(f"Running: {' '.join(cmd[:6])}...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr[:200] if result.stderr else '(empty)'}")
    
    if "HTTP_CODE:200" in result.stdout:
        print("\n? curl SUCCESS!")
    
except FileNotFoundError:
    print("curl not installed in container")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

# ??????? 3: ???????? IP ??????????
print("\n" + "="*70)
print("VARIANT 3: Container IP check")
print("="*70)

try:
    r = requests.get("https://api.ipify.org?format=json", timeout=10)
    print(f"Public IP: {r.json().get('ip')}")
except Exception as e:
    print(f"ERROR: {e}")

# ??????? 4: ?????? GET ?? telegra.ph (????????? ???????????)
print("\n" + "="*70)
print("VARIANT 4: GET telegra.ph (connectivity test)")
print("="*70)

try:
    r = requests.get("https://telegra.ph/", headers=BROWSER_HEADERS, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Title found: {'<title>' in r.text}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*70)
