import sys, json
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

db = SessionLocal()

# Реальные каналы (по ID из БД или name)
REAL_CHANNELS = {
    "24df0f84-46c2-4df4-ab39-d76881b35438": {
        "name": "Новости 📰",
        "platform": "telegram",
        "chat_id": "@news_bot_ag",  # или другое поле
        "sources": ["vc.ru", "habr", "3dnews", "ixbt"],
        "job_type": "news_pipeline",
        "schedule": "*/30 * * * *",
    },
    "35a85a18-7a61-4386-9d96-c64fac0fa217": {
        "name": "Anime news",
        "platform": "telegram",
        "chat_id": "@Anime_news_ai",
        "sources": ["anilist", "myanimelist", "animenewsnetwork"],
        "job_type": "anime_pipeline",
        "schedule": "*/30 * * * *",
    },
    "manga-channel-001": {
        "name": "Манга — новые главы",
        "platform": "telegram",
        "chat_id": "@manga_new_chapters",
        "sources": ["remanga", "mangadex", "readmanga"],
        "job_type": "manga_pipeline",
        "schedule": "*/30 * * * *",
    },
    "b76c7996-b904-4210-ab1f-c68699d004fb": {
        "name": "AI Media Factory",
        "platform": "vk",
        "group_id": "-240792540",
        "sources": ["vc.ru", "habr"],
        "job_type": "news_pipeline",
        "schedule": "0 */2 * * *",
    },
}

channels = db.query(ChannelORM).all()
print(f"Total channels before cleanup: {len(channels)}\n")

# Удаляем каналы которых нет в REAL_CHANNELS
to_delete = []
for ch in channels:
    if ch.id not in REAL_CHANNELS:
        to_delete.append(ch)
        print(f"  [DELETE] {ch.name} (ID: {ch.id})")

for ch in to_delete:
    db.delete(ch)

if to_delete:
    db.commit()
    print(f"\nDeleted {len(to_delete)} test channels\n")

# Настраиваем реальные каналы
channels = db.query(ChannelORM).all()
for ch in channels:
    if ch.id in REAL_CHANNELS:
        cfg = REAL_CHANNELS[ch.id]
        ch.name = cfg["name"]
        ch.platform = cfg["platform"]
        
        # Устанавливаем chat_id или group_id
        if "chat_id" in cfg:
            ch.chat_id = cfg["chat_id"]
        if "group_id" in cfg:
            ch.group_id = cfg["group_id"]
        
        # Сохраняем в content_profile
        ch.content_profile = {
            "sources": cfg["sources"],
            "job_type": cfg["job_type"],
            "schedule": cfg["schedule"],
        }
        
        ch.status = "active"
        print(f"  [OK] {ch.name} ({ch.id}) - {ch.platform}")

db.commit()

# Проверяем результат
print(f"\n\nFinal channels ({len(channels)}):")
channels = db.query(ChannelORM).all()
for ch in channels:
    profile = ch.content_profile or {}
    print(f"\n  {ch.name}")
    print(f"    ID: {ch.id}")
    print(f"    Platform: {ch.platform}")
    print(f"    Status: {ch.status}")
    if hasattr(ch, 'chat_id') and ch.chat_id:
        print(f"    Chat ID: {ch.chat_id}")
    if hasattr(ch, 'group_id') and ch.group_id:
        print(f"    Group ID: {ch.group_id}")
    print(f"    Sources: {profile.get('sources', [])}")
    print(f"    Job type: {profile.get('job_type')}")
    print(f"    Schedule: {profile.get('schedule')}")

db.close()