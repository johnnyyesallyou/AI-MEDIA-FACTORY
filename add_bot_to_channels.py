"""Добавляет @openclavv_ai_bot как админа в 10 существующих каналов."""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights, InputPeerChannel
from telethon.errors import FloodWaitError

load_dotenv(Path(__file__).parent / ".env")

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")

# 10 ПРАВИЛЬНЫХ каналов (первые из каждой тройки)
CHANNELS = [
    ("Anime News Daily",         3529920052),
    ("Manga Releases Tracker",   4293360589),
    ("Gaming News Hub",          4412856598),
    ("Movie & Series News",      4383377965),
    ("AI News Daily",            4466408770),
    ("Tech News Today",          4347585295),
    ("Space & Science Daily",    4414961343),
    ("Science Facts",            3917163030),
    ("Auto News Daily",          3773589347),
    ("Entertainment Memes",      4439385502),
]


async def main():
    proxy = None
    proxy_type = os.getenv("TELEGRAM_PROXY_TYPE", "").strip().lower()
    if proxy_type:
        proxy = {
            "proxy_type": proxy_type,
            "addr": os.getenv("TELEGRAM_PROXY_HOST", "127.0.0.1"),
            "port": int(os.getenv("TELEGRAM_PROXY_PORT", "10808")),
        }
        print(f"Прокси: {proxy_type}://{proxy['addr']}:{proxy['port']}")

    client = TelegramClient("pilot_session", API_ID, API_HASH, proxy=proxy)
    await client.start()
    print("✅ Авторизация (использует кэшированную сессию)")

    bot_entity = await client.get_entity(BOT_USERNAME)
    print(f"✅ Бот: @{BOT_USERNAME}")

    admin_rights = ChatAdminRights(
        post_messages=True, edit_messages=True, delete_messages=True,
        invite_users=True, change_info=False, pin_messages=True,
        add_admins=False, manage_call=False, anonymous=False,
    )

    results = []
    for name, channel_id in CHANNELS:
        try:
            channel = await client.get_entity(channel_id)
            access_hash = channel.access_hash
            
            # ВАЖНО: user_id вместо user (новый API слой 155+)
            await client(EditAdminRequest(
                channel=InputPeerChannel(channel_id=channel_id, access_hash=access_hash),
                user_id=bot_entity,
                admin_rights=admin_rights,
                rank="bot",
            ))
            print(f"  ✅ {name}: бот добавлен как админ")
            results.append((name, channel_id, True))
            await asyncio.sleep(2)
        except FloodWaitError as e:
            print(f"  ⏳ {name}: FloodWait {e.seconds}s")
            await asyncio.sleep(e.seconds)
            try:
                channel = await client.get_entity(channel_id)
                await client(EditAdminRequest(
                    channel=InputPeerChannel(channel_id=channel_id, access_hash=channel.access_hash),
                    user_id=bot_entity,
                    admin_rights=admin_rights,
                    rank="bot",
                ))
                print(f"  ✅ {name}: бот добавлен (после ожидания)")
                results.append((name, channel_id, True))
            except Exception as e2:
                print(f"  ❌ {name}: {e2}")
                results.append((name, channel_id, False))
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            results.append((name, channel_id, False))

    ok = sum(1 for _, _, s in results if s)
    print(f"\n{'='*60}")
    print(f"✅ Бот добавлен в {ok}/10 каналов")
    print(f"{'='*60}")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())