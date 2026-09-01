"""Удаляет 20 дубликатов каналов (оставляет только 10 правильных)."""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.channels import DeleteChannelRequest
from telethon.errors import FloodWaitError

load_dotenv(Path(__file__).parent / ".env")

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

# Все созданные ID (30 штук) в порядке появления
ALL_IDS = [
    # Anime News Daily (3 шт)
    3529920052,   # ← ОСТАВИТЬ
    4382397772,   # удалить
    3933394190,   # удалить
    # Manga Releases (3 шт)
    4293360589,   # ← ОСТАВИТЬ
    3872099659,   # удалить
    4432841283,   # удалить
    # Gaming News (3 шт)
    4412856598,   # ← ОСТАВИТЬ
    4391729464,   # удалить
    3982275581,   # удалить
    # Movie Series (3 шт)
    4383377965,   # ← ОСТАВИТЬ
    4394057455,   # удалить
    4390440533,   # удалить
    # AI News (3 шт)
    4466408770,   # ← ОСТАВИТЬ
    3984630360,   # удалить
    4377709593,   # удалить
    # Tech News (3 шт)
    4347585295,   # ← ОСТАВИТЬ
    3710781696,   # удалить
    4315211541,   # удалить
    # Space Science (3 шт)
    4414961343,   # ← ОСТАВИТЬ
    3897391667,   # удалить
    4292130964,   # удалить
    # Science Facts (3 шт)
    3917163030,   # ← ОСТАВИТЬ
    3995934229,   # удалить
    3591670936,   # удалить
    # Auto News (3 шт)
    3773589347,   # ← ОСТАВИТЬ
    4296832883,   # удалить
    4452136558,   # удалить
    # Memes (3 шт)
    4439385502,   # ← ОСТАВИТЬ
    4483175089,   # удалить
    4366094003,   # удалить
]

# Правильные 10 (первые из каждой тройки)
KEEP_IDS = {3529920052, 4293360589, 4412856598, 4383377965, 4466408770,
            4347585295, 4414961343, 3917163030, 3773589347, 4439385502}

TO_DELETE = [cid for cid in ALL_IDS if cid not in KEEP_IDS]


async def main():
    proxy = None
    proxy_type = os.getenv("TELEGRAM_PROXY_TYPE", "").strip().lower()
    if proxy_type:
        proxy = {
            "proxy_type": proxy_type,
            "addr": os.getenv("TELEGRAM_PROXY_HOST", "127.0.0.1"),
            "port": int(os.getenv("TELEGRAM_PROXY_PORT", "10808")),
        }

    client = TelegramClient("pilot_session", API_ID, API_HASH, proxy=proxy)
    await client.start()
    print(f"✅ Удаляю {len(TO_DELETE)} дубликатов каналов...")

    deleted = 0
    for i, cid in enumerate(TO_DELETE, 1):
        try:
            channel = await client.get_entity(cid)
            await client(DeleteChannelRequest(channel))
            print(f"  [{i}/{len(TO_DELETE)}] Удалён: {channel.title} (id={cid})")
            deleted += 1
            await asyncio.sleep(3)
        except FloodWaitError as e:
            print(f"  ⏳ FloodWait {e.seconds}s")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"  ❌ {cid}: {e}")

    print(f"\n{'='*60}")
    print(f"✅ Удалено {deleted}/{len(TO_DELETE)} дубликатов")
    print(f"✅ Осталось 10 правильных каналов")
    print(f"{'='*60}")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())