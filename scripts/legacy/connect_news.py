import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

db = SessionLocal()
news_channel = db.query(ChannelORM).filter(ChannelORM.id == "24df0f84-46c2-4df4-ab39-d76881b35438").first()
if news_channel:
    news_channel.is_connected = True
    news_channel.is_active = True
    db.commit()
    print(f"[OK] Канал {news_channel.name} подключен (is_connected=True)")
else:
    print("[!] Канал Новости не найден")
db.close()