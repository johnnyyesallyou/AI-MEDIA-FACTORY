import sys
sys.path.insert(0, "/app")

from sqlalchemy import text
from core.database import engine

print("=" * 70)
print("MIGRATION: creating manga_titles + manga_chapters")
print("=" * 70)

with engine.connect() as conn:
    # 1. manga_titles
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS manga_titles (
            id VARCHAR PRIMARY KEY,
            canonical_title VARCHAR(500) NOT NULL,
            title_slug VARCHAR(500),
            aliases JSONB DEFAULT '{}'::jsonb,
            external_ids JSONB DEFAULT '{}'::jsonb,
            description TEXT,
            genres JSONB DEFAULT '[]'::jsonb,
            cover_url VARCHAR,
            cover_asset_id VARCHAR,
            available_languages JSONB DEFAULT '[]'::jsonb,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """))
    print("✅ manga_titles created")
    
    # 2. Индекс на canonical_title
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_manga_titles_canonical 
        ON manga_titles (canonical_title)
    """))
    
    # 3. manga_chapters
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS manga_chapters (
            id VARCHAR PRIMARY KEY,
            manga_title_id VARCHAR NOT NULL REFERENCES manga_titles(id),
            chapter_number VARCHAR(50) NOT NULL,
            volume VARCHAR(50),
            source VARCHAR(100) NOT NULL,
            external_id VARCHAR(255) NOT NULL,
            language VARCHAR(10) DEFAULT 'ru',
            url VARCHAR,
            published_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """))
    print("✅ manga_chapters created")
    
    # 4. Уникальный индекс на (manga_title_id, chapter_number, source, language)
    conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_chapter_unique 
        ON manga_chapters (manga_title_id, chapter_number, source, language)
    """))
    print("✅ Unique index created")
    
    conn.commit()

# Проверка
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT tablename FROM pg_tables 
        WHERE tablename IN ('manga_titles', 'manga_chapters')
    """))
    tables = [r[0] for r in result]
    print(f"\n✅ Tables in DB: {tables}")

print("=" * 70)