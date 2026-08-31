import sys
sys.path.insert(0, '/app')
from core.database import SessionLocal
from core.models.manga_knowledge import MangaTitle

db = SessionLocal()

# Проверяем первые 10 тайтлов
titles = db.query(MangaTitle).limit(10).all()
print(f"Checked {len(titles)} manga titles:\n")

for i, t in enumerate(titles, 1):
    desc = t.description or ""
    genres = t.genres or []
    cover = t.cover_url or "none"
    print(f"{i}. {t.canonical_title[:40]}")
    print(f"   description: {desc[:80] if desc else 'EMPTY'}")
    print(f"   genres: {genres[:5] if genres else 'EMPTY'}")
    print(f"   cover: {cover[:60] if cover != 'none' else 'NONE'}")
    print()

db.close()