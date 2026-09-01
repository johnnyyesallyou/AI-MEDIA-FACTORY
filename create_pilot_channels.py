"""
Sprint 69.1: Создание 10 pilot каналов + добавление бота-админа.

Читает credentials из .env (безопасно, не коммитится).
Бот @openclavv_ai_bot становится админом во всех 10 каналах.
"""
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Загружаем .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    print("❌ python-dotenv не установлен: pip install python-dotenv")
    sys.exit(1)

try:
    from telethon import TelegramClient
    from telethon.tl.functions.channels import CreateChannelRequest, EditAdminRequest
    from telethon.tl.types import ChatAdminRights
    from telethon.errors import FloodWaitError
except ImportError:
    print("❌ telethon не установлен: pip install telethon")
    sys.exit(1)


# Читаем credentials из .env
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Валидация
if not API_ID or API_ID == "YOUR_API_ID_HERE":
    print("❌ TELEGRAM_API_ID не настроен в .env")
    print("   Получите на https://my.telegram.org → API development tools")
    sys.exit(1)
if not API_HASH or API_HASH == "YOUR_API_HASH_HERE":
    print("❌ TELEGRAM_API_HASH не настроен в .env")
    sys.exit(1)
if not BOT_USERNAME:
    print("❌ TELEGRAM_BOT_USERNAME не настроен в .env")
    sys.exit(1)

# Конвертируем api_id в int
try:
    API_ID = int(API_ID)
except ValueError:
    print(f"❌ TELEGRAM_API_ID должен быть числом, получено: {API_ID}")
    sys.exit(1)


# Матрица 10 каналов из PILOT_PLAN.md
PILOT_CHANNELS = [
    {"title": "Anime News Daily", "about": "Daily anime news, releases, and updates from the world of Japanese animation",
     "template": "news", "mode": "auto", "theme": "entertainment", "niche": "anime"},
    {"title": "Manga Releases Tracker", "about": "Track new manga chapter releases, recommendations, and updates",
     "template": "releases", "mode": "approval_required", "theme": "entertainment", "niche": "manga"},
    {"title": "Gaming News Hub", "about": "Latest gaming news, patches, announcements, and trailers",
     "template": "news", "mode": "approval_required", "theme": "entertainment", "niche": "gaming"},
    {"title": "Movie & Series News", "about": "Breaking news about movies, TV series, trailers, and casting",
     "template": "news", "mode": "approval_required", "theme": "entertainment", "niche": "movies"},
    {"title": "AI News Daily", "about": "Daily artificial intelligence news, research breakthroughs, and industry updates",
     "template": "news", "mode": "approval_required", "theme": "technology", "niche": "ai"},
    {"title": "Tech News Today", "about": "Technology news covering gadgets, software, hardware, and startups",
     "template": "news", "mode": "auto", "theme": "technology", "niche": "tech"},
    {"title": "Space & Science Daily", "about": "Space exploration, astronomy, and scientific discoveries",
     "template": "news", "mode": "approval_required", "theme": "science", "niche": "space"},
    {"title": "Science Facts", "about": "Fascinating science facts, explanations, and educational content",
     "template": "educational", "mode": "approval_required", "theme": "science", "niche": "general"},
    {"title": "Auto News Daily", "about": "Automotive news: new cars, EVs, Tesla, BMW, Mercedes, motorsport",
     "template": "news", "mode": "approval_required", "theme": "industry", "niche": "automotive"},
    {"title": "Entertainment Memes", "about": "Best memes, funny content, and viral entertainment",
     "template": "viral", "mode": "manual", "theme": "entertainment", "niche": "memes"},
]


async def main():
    print(f"[{datetime.now().isoformat()}] Запуск создания 10 pilot каналов...")
    print(f"  Бот: @{BOT_USERNAME}")
    print(f"  API ID: {API_ID}")
    
    # Прокси из .env (для обхода блокировок MTProto)
    proxy = None
    proxy_type = os.getenv("TELEGRAM_PROXY_TYPE", "").strip().lower()
    if proxy_type:
        proxy = {
            "proxy_type": proxy_type,
            "addr": os.getenv("TELEGRAM_PROXY_HOST", "127.0.0.1"),
            "port": int(os.getenv("TELEGRAM_PROXY_PORT", "1080")),
            "username": os.getenv("TELEGRAM_PROXY_USER") or None,
            "password": os.getenv("TELEGRAM_PROXY_PASS") or None,
        }
        print(f"  Прокси: {proxy_type}://{proxy['addr']}:{proxy['port']}")

    client = TelegramClient("pilot_session", API_ID, API_HASH, proxy=proxy)
    await client.start()  # Интерактивный запрос телефона/кода (один раз, потом session кэшируется)
    print("✅ Telegram авторизация успешна")
    
    try:
        bot_entity = await client.get_entity(BOT_USERNAME)
        print(f"✅ Бот найден: @{BOT_USERNAME}")
    except Exception as e:
        print(f"❌ Не удалось найти бота @{BOT_USERNAME}: {e}")
        return
    
    admin_rights = ChatAdminRights(
        post_messages=True, edit_messages=True, delete_messages=True,
        invite_users=True, change_info=False, pin_messages=True,
        add_admins=False, manage_call=False, anonymous=False,
    )
    
    created_channels = []
    
    for i, ch_cfg in enumerate(PILOT_CHANNELS, 1):
        print(f"\n[{i}/10] Создаю: {ch_cfg['title']}...")
        
        for attempt in range(3):
            try:
                result = await client(CreateChannelRequest(
                    title=ch_cfg["title"], about=ch_cfg["about"], megagroup=False,
                ))
                channel = result.chats[0]
                channel_id = channel.id
                bot_chat_id = int(f"-100{channel_id}")
                print(f"  ✅ Канал создан: channel_id={channel_id}, bot_chat_id={bot_chat_id}")
                
                await asyncio.sleep(3)
                
                # Добавление бота как админа
                try:
                    await client(EditAdminRequest(
                        channel=channel, user=bot_entity, admin_rights=admin_rights, rank="bot",
                    ))
                    print(f"  ✅ Бот @{BOT_USERNAME} добавлен как админ")
                except FloodWaitError as e:
                    print(f"  ⏳ FloodWait {e.seconds}s при добавлении бота...")
                    await asyncio.sleep(e.seconds)
                    await client(EditAdminRequest(
                        channel=channel, user=bot_entity, admin_rights=admin_rights, rank="bot",
                    ))
                    print(f"  ✅ Бот добавлен после ожидания")
                
                created_channels.append({
                    **ch_cfg,
                    "telegram_channel_id": channel_id,
                    "bot_chat_id": bot_chat_id,
                    "bot_token": BOT_TOKEN,
                    "bot_username": BOT_USERNAME,
                    "created_at": datetime.now().isoformat(),
                })
                
                if i < 10:
                    await asyncio.sleep(5)  # FloodWait protection
                break  # Успех — выходим из retry
                
            except FloodWaitError as e:
                print(f"  ⏳ FloodWait {e.seconds}s, жду...")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"  ❌ Попытка {attempt+1}/3: {e}")
                if attempt < 2:
                    await asyncio.sleep(5)
                else:
                    print(f"  ⚠️  Канал {ch_cfg['title']} не создан после 3 попыток")
    
    # Сохранение
    output = Path(__file__).parent / "pilot_channels.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "created_at": datetime.now().isoformat(),
            "bot_username": BOT_USERNAME,
            "bot_token": BOT_TOKEN,
            "total": len(created_channels),
            "channels": created_channels,
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print(f"✅ Создано {len(created_channels)}/10 каналов")
    print(f"📁 Результат: {output.name}")
    print(f"{'='*70}")
    
    if created_channels:
        print(f"\n📋 Сводка:")
        print(f"{'#':<3} {'Channel':<30} {'Mode':<20} {'Bot Chat ID':<15}")
        print("-" * 70)
        for i, ch in enumerate(created_channels, 1):
            print(f"{i:<3} {ch['title']:<30} {ch['mode']:<20} {ch['bot_chat_id']:<15}")
    
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())