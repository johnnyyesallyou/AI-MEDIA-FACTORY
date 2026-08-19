import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.channel_orm import ChannelORM
from core.models.content_orm import ContentORM
import requests

print("=" * 70)
print("DISCOVERY: API capabilities for engagement tracking")
print("=" * 70)

db = SessionLocal()

# 1. Находим Telegram канал с bot_token
tg_channel = db.query(ChannelORM).filter(
    ChannelORM.platform == "telegram",
    ChannelORM.bot_token != None
).first()

if tg_channel:
    print(f"\n[1] Telegram channel: {tg_channel.name}")
    print(f"    Bot token: {tg_channel.bot_token[:20]}...")
    
    # Проверяем доступные методы
    methods_to_test = [
        "getMe",
        "getChat",
        "getChatMemberCount",
    ]
    
    for method in methods_to_test:
        try:
            url = f"https://api.telegram.org/bot{tg_channel.bot_token}/{method}"
            params = {"chat_id": tg_channel.chat_id} if method != "getMe" else {}
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            
            if data.get("ok"):
                print(f"    ✅ {method}: available")
                if method == "getChat" and "result" in data:
                    print(f"       Type: {data['result'].get('type')}")
                    print(f"       Title: {data['result'].get('title')}")
            else:
                print(f"    ❌ {method}: {data.get('description', 'unknown error')}")
        except Exception as e:
            print(f"    ⚠️ {method}: {type(e).__name__}")
    
    # Находим опубликованный пост
    published = db.query(ContentORM).filter(
        ContentORM.status == "published",
        ContentORM.telegram_message_id != None
    ).first()
    
    if published:
        print(f"\n[2] Published post found:")
        print(f"    Message ID: {published.telegram_message_id}")
        
        # Пробуем forwardMessage для получения метрик
        try:
            url = f"https://api.telegram.org/bot{tg_channel.bot_token}/forwardMessage"
            # Используем getChat для проверки что пост существует
            url = f"https://api.telegram.org/bot{tg_channel.bot_token}/getChat"
            r = requests.get(url, params={"chat_id": tg_channel.chat_id}, timeout=10)
            print(f"    ✅ Can access channel")
        except Exception as e:
            print(f"    ⚠️ {type(e).__name__}")

# 2. Находим VK канал
vk_channel = db.query(ChannelORM).filter(
    ChannelORM.platform == "vk"
).first()

if vk_channel:
    print(f"\n[3] VK channel: {vk_channel.name}")
    print(f"    Group ID: {vk_channel.vk_group_id}")
    
    # Находим пост
    vk_post = db.query(ContentORM).filter(
        ContentORM.channel_id == vk_channel.id,
        ContentORM.status == "published"
    ).first()
    
    if vk_post:
        print(f"    Published post found")
        
        # Пробуем wall.getById
        try:
            url = "https://api.vk.com/method/wall.getById"
            params = {
                "posts": f"-{vk_channel.vk_group_id}_{vk_post.source_url.split('_')[-1] if '_' in vk_post.source_url else ''}",
                "access_token": vk_channel.vk_access_token,
                "v": "5.131"
            }
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            
            if "response" in data:
                print(f"    ✅ wall.getById: available")
                print(f"       Response keys: {list(data['response'][0].keys()) if data['response'] else 'empty'}")
            else:
                print(f"    ❌ wall.getById: {data.get('error', {}).get('error_msg', 'unknown')}")
        except Exception as e:
            print(f"    ⚠️ wall.getById: {type(e).__name__}")

db.close()
print("\n" + "=" * 70)