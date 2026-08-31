import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM

db = SessionLocal()

# Ищем JSONB поля
jsonb_fields = []
for col in ContentORM.__table__.columns:
    if 'JSON' in str(col.type):
        jsonb_fields.append(col.name)

print(f"JSONB fields in ContentORM: {jsonb_fields}")

# Проверяем publish_platform_data
item = db.query(ContentORM).first()
if hasattr(item, 'publish_platform_data'):
    print(f"\npublish_platform_data example: {item.publish_platform_data}")
else:
    print("\npublish_platform_data field NOT FOUND")

db.close()