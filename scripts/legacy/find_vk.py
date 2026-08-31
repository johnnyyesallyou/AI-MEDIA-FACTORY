from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from sqlalchemy import or_

db = SessionLocal()
try:
    # Ищем любые каналы связанные с VK или AI Media Factory
    results = db.query(ChannelORM).filter(
        or_(
            ChannelORM.platform == 'vk',
            ChannelORM.name.ilike('%media factory%'),
            ChannelORM.name.ilike('%ai media%'),
            ChannelORM.vk_group_id.isnot(None)
        )
    ).all()
    
    print(f"Found {len(results)} VK-related channels:")
    for ch in results:
        print(f"  - {ch.name!r} | platform={ch.platform} | vk_group_id={ch.vk_group_id}")
    
    if not results:
        print("\n[!] VK каналов в БД нет. Возможно был удалён раньше или в другой БД.")
        print("Проверим backup'ы...")
finally:
    db.close()