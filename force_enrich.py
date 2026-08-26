import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.manga_knowledge import MangaTitle

db = SessionLocal()

# Очищаем description у 20 тайтлов для принудительного обогащения
titles = db.query(MangaTitle).limit(20).all()
for t in titles:
    t.description = None
    t.sources_data = {}

db.commit()
print(f"Cleared description for {len(titles)} manga titles")
db.close()