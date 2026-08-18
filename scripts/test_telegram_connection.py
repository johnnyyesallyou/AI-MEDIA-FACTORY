import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from engines.telegram.publisher import TelegramPublisher

print("=" * 70)
print("TESTING Telegram Connection")
print("=" * 70)

db = SessionLocal()
channel = db.query(ChannelORM).filter(
    ChannelORM.name == "Манга — новые главы"
).first()
db.close()

if not channel:
    print("Channel not found!")
    sys.exit(1)

print(f"\nChannel: {channel.name}")
print(f"  chat_id: {channel.chat_id}")
print(f"  is_connected: {channel.is_connected}")

publisher = TelegramPublisher(channel.bot_token, channel.chat_id)

print("\n[1] getMe (bot info):")
try:
    me = publisher.get_me()
    if me.get("ok"):
        bot = me["result"]
        print(f"  Bot: @{bot['username']} ({bot['first_name']})")
    else:
        print(f"  ERROR: {me}")
        sys.exit(1)
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

print("\n[2] getChat (channel info):")
try:
    chat = publisher.get_chat()
    if chat.get("ok"):
        ch = chat["result"]
        print(f"  Channel: {ch.get('title')} (@{ch.get('username')})")
        print(f"  Type: {ch.get('type')}")
        print(f"  Chat ID: {ch.get('id')}")
    else:
        print(f"  ERROR: {chat}")
        sys.exit(1)
except Exception as e:
    print(f"  ERROR: {e}")
    print("  HINT: бот добавлен в канал как администратор?")
    sys.exit(1)

print("\n" + "=" * 70)
print("TELEGRAM CONNECTION OK")
print("=" * 70)
