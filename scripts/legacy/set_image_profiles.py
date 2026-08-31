"""Set image_profile for active channels."""
import sys
import json
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM

# Image profiles
NEWS_PROFILE = {
    "mode": "source_first",
    "source_image": True,
    "search_image": True,
    "ai_generation": "fallback",
    "require_relevance": True,
    "prefer_official": False,
    "style": "news"
}

ANIME_PROFILE = {
    "mode": "source_first",
    "source_image": True,
    "search_image": True,
    "ai_generation": "fallback",
    "require_relevance": True,
    "prefer_official": True,
    "style": "anime"
}

ANIME_GENERAL_PROFILE = {
    "mode": "source_first",
    "source_image": True,
    "search_image": True,
    "ai_generation": "fallback",
    "require_relevance": True,
    "prefer_official": False,
    "style": "anime"
}

print("="*70)
print("SETTING IMAGE PROFILES FOR CHANNELS")
print("="*70)

db = SessionLocal()
try:
    channels = db.query(ChannelORM).filter(ChannelORM.is_active == True).all()
    
    for channel in channels:
        if channel.name == "АИ Новости":
            channel.image_profile = NEWS_PROFILE
            print(f"✅ {channel.name}: News profile")
        elif channel.name == "AI Anime News":
            channel.image_profile = ANIME_PROFILE
            print(f"✅ {channel.name}: Anime profile")
        elif channel.name == "Test VK Channel":
            channel.image_profile = ANIME_GENERAL_PROFILE
            print(f"✅ {channel.name}: Anime General profile")
        else:
            channel.image_profile = NEWS_PROFILE
            print(f"✅ {channel.name}: Default News profile")
    
    db.commit()
    
    print("\n" + "="*70)
    print("RESULT")
    print("="*70)
    
    channels = db.query(ChannelORM).filter(ChannelORM.is_active == True).all()
    for channel in channels:
        profile = channel.image_profile or {}
        print(f"{channel.name}:")
        print(f"  mode: {profile.get('mode')}")
        print(f"  ai_generation: {profile.get('ai_generation')}")
        print(f"  style: {profile.get('style')}")
        print()
    
    print("✅ Image profiles set successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
