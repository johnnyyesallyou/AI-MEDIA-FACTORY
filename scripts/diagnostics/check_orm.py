import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.content_orm import ContentORM

db = SessionLocal()

print("ContentORM columns:")
for col in ContentORM.__table__.columns:
    print(f"  {col.name}: {col.type}")

# Ищем поле связанное с Telegraph
print("\n\nПоля связанные с Telegraph/publication:")
for col in ContentORM.__table__.columns:
    if any(word in col.name.lower() for word in ['telegraph', 'publish', 'url', 'link']):
        print(f"  {col.name}: {col.type}")

db.close()