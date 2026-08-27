import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

# Реальные каналы (НЕ удалять)
KEEP_CHANNELS = [
    "news_bot_ag",       # Новости
    "Anime_news_ai",     # Anime news
    "manga_new_chapters", # Манга — новые главы
    "club240792540",     # VK AI Media Factory
]

db = SessionLocal()
channels = db.query(ChannelORM).all()

kept = []
deleted = []

for ch in channels:
    # Проверяем channel_id или name на совпадение
    is_real = False
    for keep in KEEP_CHANNELS:
        if keep in (ch.channel_id or "") or keep in (ch.name or ""):
            is_real = True
            break
    
    if is_real:
        kept.append(ch)
        print(f"  [KEEP] {ch.name} ({ch.channel_id}) - {ch.platform}")
    else:
        deleted.append(ch)
        print(f"  [DELETE] {ch.name} ({ch.channel_id}) - {ch.platform}")

print(f"\nKept: {len(kept)}, Deleted: {len(deleted)}")

# Подтверждение удаления
if deleted:
    for ch in deleted:
        db.delete(ch)
    db.commit()
    print("\n[OK] Тестовые каналы удалены!")
else:
    print("\n[i] Нечего удалять")

db.close()