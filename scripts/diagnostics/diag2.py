import sys
sys.path.insert(0, '/app')

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.channel_schedule_orm import ChannelScheduleORM

db = SessionLocal()
try:
    for ch in db.query(ChannelORM).all():
        sched = db.query(ChannelScheduleORM).filter_by(channel_id=ch.id).first()
        print()
        print("NAME:", repr(ch.name), "| id:", ch.id[:8], "| platform:", ch.platform)
        print("  connected:", ch.is_connected, "| active:", ch.is_active)
        bt = ch.bot_token
        print("  bot_token:", ("SET " + bt[:6] + "...") if bt else "NOT SET")
        print("  chat_id:", ch.chat_id or "NOT SET")
        print("  vk_group:", ch.vk_group_id or "NOT SET", "| vk_token:", "SET" if ch.vk_access_token else "NOT SET")
        if sched:
            print("  schedule: active =", sched.is_active, "| cron =", sched.cron_expression)
        else:
            print("  schedule: NOT FOUND")
finally:
    db.close()