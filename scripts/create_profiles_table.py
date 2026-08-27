import sys
sys.path.insert(0, '/app')

from core.database import engine
import sqlalchemy as sa

with engine.connect() as conn:
    result = conn.execute(sa.text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name='channel_profiles'
    """)).fetchone()
    
    if result:
        print("[i] Таблица channel_profiles уже существует")
    else:
        try:
            conn.execute(sa.text("""
                CREATE TABLE channel_profiles (
                    id VARCHAR PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    style_profile VARCHAR(50),
                    language_search VARCHAR(10),
                    language_publish VARCHAR(10),
                    timezone VARCHAR(50),
                    content_policy JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            print("[OK] Создана таблица channel_profiles")
        except Exception as e:
            print(f"[!] Error: {e}")
            conn.rollback()