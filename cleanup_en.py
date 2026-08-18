import sys, json, re, requests
sys.path.insert(0, "/app")
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM

print("=" * 70)
print("CLEANUP: deleting EN-only published posts")
print("=" * 70)

db = SessionLocal()
channel = db.query(ChannelORM).filter(ChannelORM.id == "manga-channel-001").first()
token, chat_id = channel.bot_token, channel.chat_id

items = db.query(ContentORM).filter(
    ContentORM.status == "published",
    ContentORM.source_url.like("%mangadex.org%")
).all()

deleted = 0
kept = 0
for it in items:
    meta = json.loads(it.source_text)
    title = meta.get("manga_title_name", "") or it.headline
    
    if not re.search(r"[а-яА-ЯёЁ]", title):
        ok = True
        if it.telegram_message_id:
            try:
                r = requests.post(
                    f"https://api.telegram.org/bot{token}/deleteMessage",
                    json={"chat_id": chat_id, "message_id": int(it.telegram_message_id)},
                    timeout=15
                )
                ok = r.json().get("ok", False)
            except Exception:
                ok = False
        it.status = "skipped_en"
        deleted += 1
        print(f"  {'✅' if ok else '❌'} deleted: {title[:50]}")
    else:
        kept += 1

db.commit()
print(f"\n✅ Deleted: {deleted} EN posts | Kept: {kept} RU posts")
db.close()
print("=" * 70)