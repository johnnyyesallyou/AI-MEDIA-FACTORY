import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.content_orm import ContentORM
from engines.analytics import TelegramEngagementTracker, VKEngagementTracker

print("=" * 70)
print("TEST: Engagement Trackers")
print("=" * 70)

db = SessionLocal()

# 1. Тест Telegram
print("\n[1] Testing TelegramEngagementTracker:")
tg_channel = db.query(ChannelORM).filter(
    ChannelORM.platform == "telegram",
    ChannelORM.bot_token != None
).first()

if tg_channel:
    tracker = TelegramEngagementTracker(tg_channel.bot_token, tg_channel.chat_id)
    
    # Находим опубликованный пост
    tg_post = db.query(ContentORM).filter(
        ContentORM.channel_id == tg_channel.id,
        ContentORM.status == "published",
        ContentORM.telegram_message_id != None
    ).first()
    
    if tg_post:
        print(f"  Testing post: {tg_post.headline[:50]}")
        print(f"  Message ID: {tg_post.telegram_message_id}")
        
        metrics = tracker.collect_metrics(tg_post.telegram_message_id)
        
        print(f"  ✅ Metrics collected:")
        for key, value in metrics.items():
            if key != "text":  # пропускаем длинный текст
                print(f"     {key}: {value}")
    else:
        print("  ⚠️ No published Telegram posts found")
else:
    print("  ⚠️ No Telegram channel with bot_token found")

# 2. Тест VK
print("\n[2] Testing VKEngagementTracker:")
vk_channel = db.query(ChannelORM).filter(
    ChannelORM.platform == "vk",
    ChannelORM.vk_access_token != None
).first()

if vk_channel:
    tracker = VKEngagementTracker(vk_channel.vk_access_token, vk_channel.vk_group_id)
    
    # Находим опубликованный пост
    vk_post = db.query(ContentORM).filter(
        ContentORM.channel_id == vk_channel.id,
        ContentORM.status == "published"
    ).first()
    
    if vk_post and vk_post.source_url:
        # Извлекаем post_id из source_url (формат: https://vk.com/wall-123_456)
        import re
        match = re.search(r'wall(-?\d+_\d+)', vk_post.source_url)
        
        if match:
            post_id = match.group(1)
            print(f"  Testing post: {vk_post.headline[:50]}")
            print(f"  Post ID: {post_id}")
            
            metrics = tracker.collect_metrics(post_id)
            
            print(f"  ✅ Metrics collected:")
            for key, value in metrics.items():
                if key != "text":
                    print(f"     {key}: {value}")
        else:
            print(f"  ⚠️ Could not extract post_id from: {vk_post.source_url}")
    else:
        print("  ⚠️ No published VK posts found")
else:
    print("  ⚠️ No VK channel with access_token found")

db.close()
print("\n" + "=" * 70)
print("ENGAGEMENT TRACKERS TEST COMPLETED ✅")
print("=" * 70)