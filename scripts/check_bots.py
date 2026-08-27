import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
db = SessionLocal()

manga = db.query(ChannelORM).filter(ChannelORM.id == 'manga-channel-001').first()
news = db.query(ChannelORM).filter(ChannelORM.id == '24df0f84-46c2-4df4-ab39-d76881b35438').first()
anime = db.query(ChannelORM).filter(ChannelORM.id == '35a85a18-7a61-4386-9d96-c64fac0fa217').first()

for ch in [manga, news, anime]:
    print(f"\n{ch.name}:")
    print(f"  is_connected: {ch.is_connected}")
    print(f"  chat_id: {ch.chat_id}")
    print(f"  bot_token set: {bool(ch.bot_token)}")
    if ch.bot_token:
        print(f"  bot_token preview: {ch.bot_token[:20]}...")
    else:
        print(f"  bot_token: NONE!")

db.close()