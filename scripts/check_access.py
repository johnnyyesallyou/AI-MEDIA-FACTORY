import sys
sys.path.insert(0, '/app')
from engines.telegraph.publisher import TelegraphPublisher

t = TelegraphPublisher()
has_attr = hasattr(t, 'access_token')
token_val = getattr(t, 'access_token', None)
print(f"access_token attribute exists: {has_attr}")
if has_attr:
    print(f"access_token value: {token_val[:20] if token_val else None}...")
print(f"upload method exists: {hasattr(t, 'upload_images_to_telegraph')}")