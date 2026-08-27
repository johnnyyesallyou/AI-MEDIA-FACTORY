import sys, json
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

db = SessionLocal()
channels = db.query(ChannelORM).all()
print(f"Total channels: {len(channels)}\n")

for ch in channels:
    profile = ch.content_profile or {}
    print(f"  {ch.name}")
    print(f"    ID: {ch.id}")
    print(f"    Platform: {ch.platform}")
    print(f"    Status: {ch.status}")
    print(f"    Active: {ch.is_active}")
    print(f"    Connected: {ch.is_connected}")
    if ch.chat_id:
        print(f"    Chat ID: {ch.chat_id}")
    if ch.vk_group_id:
        print(f"    VK Group ID: {ch.vk_group_id}")
    print(f"    Sources: {profile.get('sources', [])}")
    print(f"    Job type: {profile.get('job_type')}")
    print()

db.close()