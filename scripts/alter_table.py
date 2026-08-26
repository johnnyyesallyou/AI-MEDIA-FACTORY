import sys
sys.path.insert(0, '/app')

from core.database import engine
import sqlalchemy as sa

with engine.connect() as conn:
    # Проверяем существует ли колонка
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='content' AND column_name='telegraph_url'
    """)).fetchone()
    
    if result:
        print("[i] Column telegraph_url already exists")
    else:
        try:
            conn.execute(sa.text("""
                ALTER TABLE content 
                ADD COLUMN telegraph_url VARCHAR(500)
            """))
            conn.commit()
            print("[OK] Added column telegraph_url to content table")
        except Exception as e:
            print(f"[!] Error: {e}")
            conn.rollback()