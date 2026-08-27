import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

db = SessionLocal()

print("ChannelORM columns:")
for col in ChannelORM.__table__.columns:
    print(f"  {col.name}: {col.type}")

print("\n\nAll channels:")
channels = db.query(ChannelORM).all()
for ch in channels:
    print(f"\n  ID: {ch.id}")
    print(f"  Name: {ch.name}")
    print(f"  Platform: {ch.platform}")
    # Проверяем все возможные поля для channel ID
    for attr in ['chat_id', 'group_id', 'channel_name', 'external_id', 'username']:
        val = getattr(ch, attr, None)
        if val:
            print(f"  {attr}: {val}")
    
    # Проверяем content_profile
    if hasattr(ch, 'content_profile') and ch.content_profile:
        print(f"  content_profile keys: {list(ch.content_profile.keys())}")
    
    # Проверяем meta
    if hasattr(ch, 'meta') and ch.meta:
        print(f"  meta keys: {list(ch.meta.keys())}")

db.close()