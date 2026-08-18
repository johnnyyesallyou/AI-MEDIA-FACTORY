import sys
sys.path.insert(0, "/app")

from sqlalchemy import text
from core.database import engine

print("=" * 70)
print("MIGRATION: creating anime_titles + anime_episodes")
print("=" * 70)

with engine.connect() as conn:
    # 1. anime_titles
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS anime_titles (
            id VARCHAR PRIMARY KEY,
            canonical_title VARCHAR(500) NOT NULL,
            title_romaji VARCHAR(500),
            title_english VARCHAR(500),
            title_native VARCHAR(500),
            title_slug VARCHAR(500),
            
            aliases JSONB DEFAULT '{}'::jsonb,
            external_ids JSONB DEFAULT '{}'::jsonb,
            sources_data JSONB DEFAULT '{}'::jsonb,
            
            description TEXT,
            genres JSONB DEFAULT '[]'::jsonb,
            cover_url VARCHAR,
            
            status VARCHAR(50),
            season VARCHAR(20),
            season_year INTEGER,
            episodes INTEGER,
            
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """))
    print("✅ anime_titles created")

    # 2. Индексы
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_anime_titles_canonical
        ON anime_titles (canonical_title)
    """))
    
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_anime_titles_status
        ON anime_titles (status)
    """))

    # 3. anime_episodes
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS anime_episodes (
            id VARCHAR PRIMARY KEY,
            anime_title_id VARCHAR NOT NULL REFERENCES anime_titles(id),
            
            episode_number VARCHAR(50) NOT NULL,
            season_number INTEGER DEFAULT 1,
            
            source VARCHAR(100) NOT NULL,
            external_id VARCHAR(255) NOT NULL,
            language VARCHAR(10) DEFAULT 'ja',
            
            title VARCHAR(500),
            description TEXT,
            
            aired_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """))
    print("✅ anime_episodes created")

    # 4. Уникальный индекс
    conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_anime_episode_unique
        ON anime_episodes (anime_title_id, episode_number, season_number, source)
    """))
    print("✅ Unique index created")

    conn.commit()

# Проверка
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT tablename FROM pg_tables
        WHERE tablename IN ('anime_titles', 'anime_episodes')
    """))
    tables = [r[0] for r in result]
    print(f"\n✅ Tables in DB: {tables}")

print("=" * 70)