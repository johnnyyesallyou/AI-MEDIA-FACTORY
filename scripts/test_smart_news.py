import sys
sys.path.insert(0, "/app")

from engines.smart_image_resolver import SmartImageResolver
from core.database import SessionLocal
from core.models.content_orm import ContentORM
from core.models.channel_orm import ChannelORM

print("=" * 70)
print("TEST: SmartImageResolver on news")
print("=" * 70)

db = SessionLocal()
resolver = SmartImageResolver()

# Берём news item без asset_id
item = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.source_url.like("%habr.com%"),
    ContentORM.asset_id == None
).first()

if not item:
    print("No news items without covers, trying any news...")
    item = db.query(ContentORM).filter(
        ContentORM.source_url.like("%habr.com%"),
        ContentORM.asset_id == None
    ).first()

if not item:
    print("No news items without covers at all")
    db.close()
    exit(0)

channel = db.query(ChannelORM).filter(ChannelORM.name.like("%Новости%")).first()

print(f"\nItem: {item.headline}")
print(f"Source: {item.source_url[:80]}")
print(f"Channel: {channel.name}")

result = resolver.resolve(
    content_id=item.id,
    source_url=item.source_url,
    channel=channel,
    metadata={}
)

if result:
    print(f"\n✅ SUCCESS:")
    print(f"  asset_id: {result.asset_id}")
    print(f"  source: {result.source}")
    print(f"  confidence: {result.confidence}")
    print(f"  type: {result.type}")
    
    # Обновляем content
    item.asset_id = result.asset_id
    db.commit()
    print(f"  Updated content.asset_id")
else:
    print("\n❌ FAILED: No image found")

db.close()
print("=" * 70)