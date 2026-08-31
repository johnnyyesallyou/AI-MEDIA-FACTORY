from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.channel_schedule_orm import ChannelScheduleORM

db = SessionLocal()
try:
    channels = db.query(ChannelORM).all()
    print("=" * 90)
    print("DIRECT DB QUERY (real state)")
    print("=" * 90)
    for ch in channels:
        bot_token = getattr(ch, 'bot_token', None) or getattr(ch, 'telegram_bot_token', None)
        chat_id = getattr(ch, 'chat_id', None) or getattr(ch, 'telegram_chat_id', None)
        vk_group = getattr(ch, 'vk_group_id', None)
        vk_token = getattr(ch, 'vk_access_token', None)
        
        # Schedule
        sched = db.query(ChannelScheduleORM).filter(ChannelScheduleORM.channel_id == ch.id).first()
        
        print(f"\n  {ch.name!r:42} id={ch.id[:8]}...")
        print(f"    platform={ch.platform:9} is_connected={ch.is_connected} is_active={ch.is_active}")
        print(f"    bot_token={'SET ('+bot_token[:8]+'...)' if bot_token else 'NOT SET'}")
        print(f"    chat_id={chat_id!r if chat_id else 'NOT SET'}")
        print(f"    vk_group_id={vk_group!r if vk_group else 'NOT SET'}")
        print(f"    vk_token={'SET' if vk_token else 'NOT SET'}")
        print(f"    sources_count={len(ch.sources) if ch.sources else 0}")
        if sched:
            print(f"    schedule: active={sched.is_active}, cron={sched.cron_expression}, next_run={sched.last_run}")
        else:
            print(f"    schedule: NOT FOUND")
        print(f"    template_id={ch.template_id!r}")
finally:
    db.close()