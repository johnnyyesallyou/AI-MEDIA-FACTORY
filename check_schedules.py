import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.channel_schedule_orm import ChannelScheduleORM
db = SessionLocal()
for s in db.query(ChannelScheduleORM).all():
    print(f"  channel={s.channel_id} cron={getattr(s, 'cron_expression', None)} active={getattr(s, 'is_active', None)}")
db.close()