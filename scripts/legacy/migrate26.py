import sys
sys.path.insert(0, "/app")
from sqlalchemy import text
from core.database import engine

with engine.connect() as conn:
    conn.execute(text("""
        ALTER TABLE manga_titles 
        ADD COLUMN IF NOT EXISTS sources_data JSONB DEFAULT '{}'::jsonb
    """))
    conn.commit()
    print("✅ manga_titles.sources_data added")