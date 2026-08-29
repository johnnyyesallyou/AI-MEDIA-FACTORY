import sys
sys.path.insert(0, '/app')

from core.database import engine
from sqlalchemy import text, inspect

with engine.begin() as conn:
    # Проверяем существует ли колонка
    result = conn.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='content' AND column_name='video_url'"
    ))
    exists = result.fetchone() is not None
    
    if exists:
        print("[i] video_url column already exists in content table")
    else:
        conn.execute(text("ALTER TABLE content ADD COLUMN video_url VARCHAR(2000)"))
        print("[OK] video_url column added to content table")

# Проверяем что SQLAlchemy видит новую колонку
inspector = inspect(engine)
columns = [c['name'] for c in inspector.get_columns('content')]
print(f"\nContent columns ({len(columns)}):")
for c in columns:
    marker = " <-- NEW" if c == "video_url" else ""
    print(f"  - {c}{marker}")