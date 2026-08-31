import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM

db = SessionLocal()

# Контент который должен обрабатываться image job
items = db.query(ContentORM).filter(
    ContentORM.status == "research",
    ContentORM.image_url == None
).limit(10).all()

print(f"Items needing image processing: {len(items)}\n")
for item in items[:5]:
    print(f"  {item.headline[:60]}")
    print(f"    status: {item.status}")
    print(f"    image_url: {item.image_url}")
    print(f"    anime_episode_id: {item.anime_episode_id}")
    print(f"    manga_chapter_id: {item.manga_chapter_id}")
    print()

db.close()