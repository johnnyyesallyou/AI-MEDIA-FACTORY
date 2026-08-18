import sys
sys.path.insert(0, '/app')

try:
    from core.models.channel_orm import ChannelORM
    print("IMPORT OK")
except Exception as e:
    print(f"IMPORT FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from core.database import SessionLocal
    db = SessionLocal()
    channels = db.query(ChannelORM).filter(ChannelORM.is_active == True).all()
    print(f"LOADED CHANNELS: {len(channels)}")
    for ch in channels:
        profile = ch.image_profile or {}
        mode = profile.get('mode', 'N/A')
        style = profile.get('style', 'N/A')
        print(f"  - {ch.name}: mode={mode}, style={style}")
    db.close()
    print("SUCCESS")
except Exception as e:
    print(f"DB ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
