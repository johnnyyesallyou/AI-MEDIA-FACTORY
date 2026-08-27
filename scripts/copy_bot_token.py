import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
db = SessionLocal()

# Берём bot_token у manga и копируем в news и anime
manga = db.query(ChannelORM).filter(ChannelORM.id == 'manga-channel-001').first()
news = db.query(ChannelORM).filter(ChannelORM.id == '24df0f84-46c2-4df4-ab39-d76881b35438').first()
anime = db.query(ChannelORM).filter(ChannelORM.id == '35a85a18-7a61-4386-9d96-c64fac0fa217').first()

if manga and manga.bot_token:
    if news and not news.bot_token:
        news.bot_token = manga.bot_token
        print(f"[OK] Скопирован bot_token в канал '{news.name}'")
    if anime and not anime.bot_token:
        anime.bot_token = manga.bot_token
        print(f"[OK] Скопирован bot_token в канал '{anime.name}'")
    db.commit()
else:
    print("[!] Manga channel не имеет bot_token — нужен из .env")

db.close()