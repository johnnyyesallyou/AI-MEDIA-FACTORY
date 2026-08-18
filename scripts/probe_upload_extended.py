import requests
import json
import os
import mimetypes

print("=" * 70)
print("TELEGRAPH UPLOAD EXTENDED DEBUG")
print("=" * 70)

test_image = "/app/assets/2026/08/d99baea8-86a7-42bd-a980-02de66052f18.jpg"

if not os.path.exists(test_image):
    print(f"ERROR: {test_image} not found")
    exit(1)

file_size = os.path.getsize(test_image)
print(f"\nFile: {test_image}")
print(f"Size: {file_size} bytes ({file_size / 1024:.2f} KB)")

# ??????? 1: ????????? PNG (???????? ?? ?????????????)
print("\n" + "="*70)
print("VARIANT 1: Upload JPEG ? ????? Content-Type")
print("="*70)

with open(test_image, "rb") as f:
    files = {"file": ("image.jpg", f, "image/jpeg")}
    r = requests.post("https://telegra.ph/upload", files=files, timeout=30)

print(f"Status: {r.status_code}")
print(f"Response: {r.text[:200]}")

# ??????? 2: ????????? ??? ???????? Content-Type
print("\n" + "="*70)
print("VARIANT 2: Upload ??? Content-Type (auto-detect)")
print("="*70)

with open(test_image, "rb") as f:
    files = {"file": ("image.jpg", f)}
    r = requests.post("https://telegra.ph/upload", files=files, timeout=30)

print(f"Status: {r.status_code}")
print(f"Response: {r.text[:200]}")

# ??????? 3: ????????? ?????? filename
print("\n" + "="*70)
print("VARIANT 3: Upload ? ?????? filename (test.jpg)")
print("="*70)

with open(test_image, "rb") as f:
    files = {"file": ("test.jpg", f, "image/jpeg")}
    r = requests.post("https://telegra.ph/upload", files=files, timeout=30)

print(f"Status: {r.status_code}")
print(f"Response: {r.text[:200]}")

# ??????? 4: ????????? ??????? PNG ?? JPEG
print("\n" + "="*70)
print("VARIANT 4: Convert to PNG and upload")
print("="*70)

try:
    from PIL import Image
    import io
    
    # ????????? JPEG ? ???????????? ? PNG
    img = Image.open(test_image)
    png_buffer = io.BytesIO()
    img.save(png_buffer, format="PNG")
    png_buffer.seek(0)
    
    print(f"Converted to PNG, size: {png_buffer.getbuffer().nbytes} bytes")
    
    files = {"file": ("image.png", png_buffer, "image/png")}
    r = requests.post("https://telegra.ph/upload", files=files, timeout=30)
    
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:200]}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"\n? SUCCESS: {json.dumps(data, indent=2)}")
        
except ImportError:
    print("PIL not available, skipping PNG conversion")
except Exception as e:
    print(f"ERROR: {e}")

# ??????? 5: ????????? ??????? ??????
print("\n" + "="*70)
print("VARIANT 5: Resize to smaller dimensions")
print("="*70)

try:
    from PIL import Image
    import io
    
    img = Image.open(test_image)
    # ????????? ?? 800px ?? ??????? ???????
    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
    
    jpeg_buffer = io.BytesIO()
    img.save(jpeg_buffer, format="JPEG", quality=85)
    jpeg_buffer.seek(0)
    
    print(f"Resized to {img.size}, size: {jpeg_buffer.getbuffer().nbytes} bytes")
    
    files = {"file": ("image.jpg", jpeg_buffer, "image/jpeg")}
    r = requests.post("https://telegra.ph/upload", files=files, timeout=30)
    
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:200]}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"\n? SUCCESS: {json.dumps(data, indent=2)}")
        
except ImportError:
    print("PIL not available, skipping resize")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*70)
