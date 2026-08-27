import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.channel_schedule_orm import ChannelScheduleORM

db = SessionLocal()
test_ch = db.query(ChannelORM).filter(ChannelORM.name == "Тестовый манга-канал").first()
if test_ch:
    db.query(ChannelScheduleORM).filter(ChannelScheduleORM.channel_id == test_ch.id).delete()
    db.delete(test_ch)
    db.commit()
    print("[OK] Тестовый канал удалён")
else:
    print("[i] Тестовый канал не найден (не критично)")
db.close()