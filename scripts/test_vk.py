import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from engines.publishing import get_publisher_for_channel, Publication, PublicationButton

db = SessionLocal()
vk_channel = db.query(ChannelORM).filter(ChannelORM.platform == "vk").first()

print("=" * 70)
print("TEST: VK Publishing")
print("=" * 70)

if not vk_channel:
    print("⚠️ No VK channel found")
    db.close()
    sys.exit(0)

print(f"Channel: {vk_channel.name}")
print(f"Group ID: {vk_channel.vk_group_id}")
print(f"Has token: {bool(vk_channel.vk_access_token)}")

publisher = get_publisher_for_channel(vk_channel)
print(f"Publisher platform: {publisher.platform}")

pub = Publication(
    text=" Тестовый пост AI Media Factory\n\nUnified Publisher работает: один Publication → Telegram и VK.",
    image_url=None,
    buttons=[PublicationButton(text="🔗 Источник", url="https://remanga.org/")],
)

result = publisher.publish(pub)
print(f"\nResult: {result}")
print("=" * 70)
db.close()