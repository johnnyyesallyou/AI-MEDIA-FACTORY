"""Генерирует pilot_channels.json с финальными данными."""
import json
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")

CHANNELS = [
    {"title": "Anime News Daily", "template": "news", "mode": "auto",
     "theme": "entertainment", "niche": "anime", "channel_id": 3529920052,
     "about": "Daily anime news, releases, and updates from the world of Japanese animation"},
    {"title": "Manga Releases Tracker", "template": "releases", "mode": "approval_required",
     "theme": "entertainment", "niche": "manga", "channel_id": 4293360589,
     "about": "Track new manga chapter releases, recommendations, and updates"},
    {"title": "Gaming News Hub", "template": "news", "mode": "approval_required",
     "theme": "entertainment", "niche": "gaming", "channel_id": 4412856598,
     "about": "Latest gaming news, patches, announcements, and trailers"},
    {"title": "Movie & Series News", "template": "news", "mode": "approval_required",
     "theme": "entertainment", "niche": "movies", "channel_id": 4383377965,
     "about": "Breaking news about movies, TV series, trailers, and casting"},
    {"title": "AI News Daily", "template": "news", "mode": "approval_required",
     "theme": "technology", "niche": "ai", "channel_id": 4466408770,
     "about": "Daily artificial intelligence news, research breakthroughs, and industry updates"},
    {"title": "Tech News Today", "template": "news", "mode": "auto",
     "theme": "technology", "niche": "tech", "channel_id": 4347585295,
     "about": "Technology news covering gadgets, software, hardware, and startups"},
    {"title": "Space & Science Daily", "template": "news", "mode": "approval_required",
     "theme": "science", "niche": "space", "channel_id": 4414961343,
     "about": "Space exploration, astronomy, and scientific discoveries"},
    {"title": "Science Facts", "template": "educational", "mode": "approval_required",
     "theme": "science", "niche": "general", "channel_id": 3917163030,
     "about": "Fascinating science facts, explanations, and educational content"},
    {"title": "Auto News Daily", "template": "news", "mode": "approval_required",
     "theme": "industry", "niche": "automotive", "channel_id": 3773589347,
     "about": "Automotive news: new cars, EVs, Tesla, BMW, Mercedes, motorsport"},
    {"title": "Entertainment Memes", "template": "viral", "mode": "manual",
     "theme": "entertainment", "niche": "memes", "channel_id": 4439385502,
     "about": "Best memes, funny content, and viral entertainment"},
]

result = {
    "created_at": datetime.now().isoformat(),
    "bot_username": BOT_USERNAME,
    "bot_token": BOT_TOKEN,
    "total": len(CHANNELS),
    "channels": [
        {
            **ch,
            "telegram_channel_id": ch["channel_id"],
            "bot_chat_id": int(f"-100{ch['channel_id']}"),
            "bot_token": BOT_TOKEN,
            "bot_username": BOT_USERNAME,
            "created_at": datetime.now().isoformat(),
        }
        for ch in CHANNELS
    ],
}

with open("pilot_channels.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"✅ pilot_channels.json создан ({len(CHANNELS)} каналов)")
print(f"\n📋 Сводка:")
print(f"{'#':<3} {'Channel':<30} {'Mode':<20} {'Bot Chat ID'}")
print("-" * 80)
for i, ch in enumerate(CHANNELS, 1):
    print(f"{i:<3} {ch['title']:<30} {ch['mode']:<20} -100{ch['channel_id']}")