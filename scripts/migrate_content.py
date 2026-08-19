import sys
sys.path.insert(0, "/app")

from sqlalchemy import text
from core.database import engine

print("=" * 70)
print("MIGRATION: adding manga_chapter_id to content")
print("=" * 70)

with engine.connect() as conn:
    conn.execute(text("""
        ALTER TABLE content 
        ADD COLUMN IF NOT EXISTS manga_chapter_id VARCHAR
    """))
    conn.commit()
    print("✅ manga_chapter_id column added")

    # Проверяем
    result = conn.execute(text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'content' AND column_name = 'manga_chapter_id'
    """))
    if list(result):
        print("✅ Column exists in DB")
    else:
        print("❌ Column not found")

print("=" * 70)