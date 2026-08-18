import requests
import json

HEADERS = {"User-Agent": "Mozilla/5.0 (AI-Media-Factory/1.0)"}

print("=" * 70)
print("TELEGRAPH API PROBE")
print("=" * 70)

# 1. createAccount
print("\n[1] POST /createAccount:")
r = requests.post(
    "https://api.telegra.ph/createAccount",
    data={
        "short_name": "AI-Media-Factory",
        "author_name": "AI Media Factory",
        "author_url": "https://github.com/yourusername/ai-media-factory"
    },
    headers=HEADERS,
    timeout=15
)
print(f"  Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(f"  Response: {json.dumps(data, indent=2)}")
    
    if data.get("ok"):
        access_token = data["result"]["access_token"]
        print(f"\n  ? Access token: {access_token[:20]}...")
        
        # 2. createPage
        print("\n[2] POST /createPage:")
        r2 = requests.post(
            "https://api.telegra.ph/createPage",
            data={
                "access_token": access_token,
                "title": "Test Page from AI Media Factory",
                "author_name": "AI Media Factory",
                "content": json.dumps([
                    {"tag": "p", "children": ["This is a test page created by AI Media Factory."]},
                    {"tag": "p", "children": ["It supports full HTML-like content without character limits."]},
                    {"tag": "a", "attrs": {"href": "https://habr.com"}, "children": ["Link to Habr"]}
                ]),
                "return_content": "true"
            },
            headers=HEADERS,
            timeout=15
        )
        print(f"  Status: {r2.status_code}")
        
        if r2.status_code == 200:
            data2 = r2.json()
            print(f"  Response: {json.dumps(data2, indent=2)[:500]}")
            
            if data2.get("ok"):
                page_url = data2["result"]["url"]
                print(f"\n  ? Page URL: {page_url}")
        
        # 3. upload (image)
        print("\n[3] POST /upload (test image):")
        # ?????????? ???????????? ???????
        test_image = "/app/assets/2026/08/d99baea8-86a7-42bd-a980-02de66052f18.jpg"
        
        try:
            with open(test_image, "rb") as f:
                files = {"file": (test_image.split("/")[-1], f, "image/jpeg")}
                r3 = requests.post(
                    "https://telegra.ph/upload",
                    files=files,
                    headers=HEADERS,
                    timeout=15
                )
            
            print(f"  Status: {r3.status_code}")
            if r3.status_code == 200:
                data3 = r3.json()
                print(f"  Response: {json.dumps(data3, indent=2)}")
                
                if isinstance(data3, list) and data3:
                    uploaded_path = data3[0].get("src")
                    print(f"\n  ? Uploaded image: https://telegra.ph{uploaded_path}")
        except Exception as e:
            print(f"  ERROR: {e}")

else:
    print(f"  Response: {r.text[:300]}")

print("\n" + "=" * 70)
