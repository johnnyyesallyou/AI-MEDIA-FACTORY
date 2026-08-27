import sys, json
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

db = SessionLocal()

# Конфигурация реальных каналов
CHANNEL_CONFIG = {
    "news_bot_ag": {
        "name": "Новости 📰",
        "platform": "telegram",
        "channel_id": "@news_bot_ag",
        "status": "active",
        "sources": ["vc.ru", "habr", "3dnews", "ixbt"],
        "job_type": "news_pipeline",
        "schedule": "*/30 * * * *",
    },
    "Anime_news_ai": {
        "name": "Anime news",
        "platform": "telegram",
        "channel_id": "@Anime_news_ai",
        "status": "active",
        "sources": ["anilist", "myanimelist", "animenewsnetwork"],
        "job_type": "anime_pipeline",
        "schedule": "*/30 * * * *",
    },
    "manga_new_chapters": {
        "name": "Манга — новые главы",
        "platform": "telegram",
        "channel_id": "@manga_new_chapters",
        "status": "active",
        "sources": ["remanga", "mangadex", "readmanga"],
        "job_type": "manga_pipeline",
        "schedule": "*/30 * * * *",
    },
    "club240792540": {
        "name": "AI Media Factory",
        "platform": "vk",
        "channel_id": "-240792540",
        "status": "active",
        "sources": ["vc.ru", "habr"],
        "job_type": "news_pipeline",
        "schedule": "0 */2 * * *",
    },
}

channels = db.query(ChannelORM).all()
updated = 0

for ch in channels:
    # Ищем конфигурацию
    config = None
    for key, cfg in CHANNEL_CONFIG.items():
        if key in (ch.channel_id or "") or key in (ch.name or ""):
            config = cfg
            break
    
    if config:
        ch.name = config["name"]
        ch.platform = config["platform"]
        ch.channel_id = config["channel_id"]
        ch.status = config["status"]
        # Сохраняем sources в meta
        meta = json.loads(ch.meta or "{}")
        meta["sources"] = config["sources"]
        meta["job_type"] = config["job_type"]
        meta["schedule"] = config["schedule"]
        ch.meta = json.dumps(meta, ensure_ascii=False)
        updated += 1
        print(f"  [OK] {ch.name} ({ch.channel_id}) - {ch.platform}")

db.commit()
print(f"\nUpdated: {updated} channels")

# Если какой-то канал отсутствует — создаём
existing_ids = [ch.channel_id for ch in channels]
for key, cfg in CHANNEL_CONFIG.items():
    if cfg["channel_id"] not in existing_ids:
        from uuid import uuid4
        new_ch = ChannelORM(
            id=str(uuid4()),
            name=cfg["name"],
            platform=cfg["platform"],
            channel_id=cfg["channel_id"],
            status=cfg["status"],
            meta=json.dumps({
                "sources": cfg["sources"],
                "job_type": cfg["job_type"],
                "schedule": cfg["schedule"],
            }, ensure_ascii=False),
        )
        db.add(new_ch)
        print(f"  [NEW] {cfg['name']} ({cfg['channel_id']})")
        
db.commit()
db.close()