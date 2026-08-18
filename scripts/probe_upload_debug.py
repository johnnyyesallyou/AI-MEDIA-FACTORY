import requests
import json
import os

HEADERS = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}

print("=" * 70)
print("TELEGRAPH UPLOAD DEBUG")
print("=" * 70)

# ????????? ????
test_image = "/app/assets/2026/08/d99baea8-86a7-42bd-a980-02de66052f18.jpg"
print(f"\nTest image: {test_image}")
print(f"  Exists: {os.path.exists(test_image)}")

if os.path.exists(test_image):
    file_size = os.path.getsize(test_image)
    print(f"  Size: {file_size} bytes")
    
    # ?????? ?????? ????? ??? ???????? ????
    with open(test_image, "rb") as f:
        header = f.read(16)
        print(f"  Header (hex): {header[:8].hex()}")
        print(f"  Header (bytes): {list(header[:8])}")
    
    # ??????? upload ? ????????? ????????????
    print("\n[POST] https://telegra.ph/upload")
    
    with open(test_image, "rb") as f:
        files = {"file": ("test.jpg", f, "image/jpeg")}
        r = requests.post(
            "https://telegra.ph/upload",
            files=files,
            timeout=30
        )
    
    print(f"  Status: {r.status_code}")
    print(f"  Headers: {dict(r.headers)}")
    print(f"  Response: {r.text[:500]}")
    
    if r.status_code == 200:
        try:
            data = r.json()
            print(f"\n  ? Success: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"  ERROR parsing JSON: {e}")

print("\n" + "=" * 70)
