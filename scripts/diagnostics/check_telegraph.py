import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM

db = SessionLocal()

# Ищем контент с Telegraph URL
telegraph_items = db.query(ContentORM).filter(
    ContentORM.telegraph_url != None,
    ContentORM.telegraph_url != ""
).limit(10).all()

print(f"Found {len(telegraph_items)} items with Telegraph URL:\n")
for item in telegraph_items:
    print(f"Title: {item.headline[:60]}")
    print(f"Telegraph: {item.telegraph_url}")
    print(f"Status: {item.status}")
    print()

db.close()