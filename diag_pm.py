import sys
sys.path.insert(0, '/app')

from core.models.analytics import PostMetric
import sqlalchemy

print("=== PostMetric schema ===")
print(f"Table: {PostMetric.__tablename__ if hasattr(PostMetric, '__tablename__') else 'n/a'}")
print("\nColumns:")
for col in PostMetric.__table__.columns:
    print(f"  {col.name}: {col.type}")

print("\nRelationships:")
for rel in PostMetric.__mapper__.relationships:
    print(f"  {rel.key}: {rel.direction.name}")

# Проверяем Content
try:
    from core.models.content_orm import ContentORM
    print("\n=== ContentORM schema ===")
    for col in ContentORM.__table__.columns:
        print(f"  {col.name}: {col.type}")
except Exception as e:
    print(f"ContentORM error: {e}")

# Реальные данные
from core.database import SessionLocal
db = SessionLocal()
try:
    count = db.query(PostMetric).count()
    print(f"\nTotal PostMetric rows: {count}")
    if count > 0:
        sample = db.query(PostMetric).first()
        print(f"\nSample PostMetric attrs:")
        for k in dir(sample):
            if not k.startswith('_'):
                try:
                    v = getattr(sample, k)
                    if not callable(v):
                        print(f"  {k} = {repr(v)[:100]}")
                except: pass
finally:
    db.close()