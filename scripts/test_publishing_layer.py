import sys
sys.path.insert(0, "/app")

from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM
from engines.publishing import (
    Publication, PublicationButton,
    TelegramPlatformPublisher, PublicationImageResolver,
)
from engines.channel_profiles import resolve_channel_profile

print("=" * 70)
print("TEST: Publishing layer (Sprint 25.2)")
print("=" * 70)

db = SessionLocal()
channel = db.query(ChannelORM).filter(ChannelORM.name.like("%Манга%")).first()
profile = resolve_channel_profile(channel)

print(f"\nProfile: {profile['profile_key']}")
print(f"  source_policy: {profile['source_policy']}")
print(f"  enrichment_policy: {profile['enrichment_policy']}")
print(f"  formatting: unescape_html={profile['formatting_profile']['unescape_html']}")

# Берём research item с knowledge link
item = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.manga_chapter_id != None,
).first()

if item:
    resolver = PublicationImageResolver()
    image_url = resolver.resolve(item, channel)
    print(f"\nImage resolved via policy: {str(image_url)[:70]}")

    # Строим Publication (dry run, без отправки)
    pub = Publication(
        text="📚 Тестовый пост",
        image_url=image_url,
        buttons=[
            PublicationButton(text="📖 Читать на Telegraph", url="https://telegra.ph/test"),
            PublicationButton(text="🔗 Источник", url="https://remanga.org/test"),
        ],
        source_url=item.source_url,
        metadata={"manga_chapter_id": item.manga_chapter_id},
    )
    print(f"Publication: text={pub.text!r}, buttons={len(pub.buttons)}, image={bool(pub.image_url)}")

    # Проверяем адаптер
    publisher = TelegramPlatformPublisher(channel.bot_token, channel.chat_id)
    print(f"Publisher platform: {publisher.platform}")
    print("\n✅ Publishing layer работает (dry run)")
else:
    print("\n⚠️ Нет research items с manga_chapter_id")

db.close()
print("=" * 70)