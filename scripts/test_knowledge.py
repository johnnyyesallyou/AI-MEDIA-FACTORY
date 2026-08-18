import sys
sys.path.insert(0, "/app")

from engines.source_adapters.manga_registry import MangaRegistry
from engines.manga_knowledge_engine import MangaKnowledgeEngine
from engines.title_normalizer import TitleNormalizer
from core.database import SessionLocal
from core.models.manga_knowledge import MangaTitle, MangaChapter

print("=" * 70)
print("TEST: MangaKnowledgeEngine")
print("=" * 70)

# 1. Тест TitleNormalizer
print("\n[1] TitleNormalizer:")
normalizer = TitleNormalizer()
test_cases = [
    "One Piece",
    "ONE PIECE",
    "Ван Пис",
    "Ван-Пис!",
    "Attack on Titan",
]
for t in test_cases:
    print(f"  '{t}' → '{normalizer.normalize(t)}'")

# 2. Тест MangaKnowledgeEngine
print("\n[2] MangaKnowledgeEngine:")
engine = MangaKnowledgeEngine()

# Загружаем главы через registry
items = MangaRegistry.fetch_all(limit=10)
print(f"  Fetched {len(items)} items")

# Обрабатываем
new_titles, new_chapters, existing_chapters = engine.process_items(items)
print(f"\n  Results:")
print(f"    New titles: {new_titles}")
print(f"    New chapters: {new_chapters}")
print(f"    Existing chapters: {existing_chapters}")

# 3. Проверка БД
print("\n[3] DB stats:")
db = SessionLocal()
title_count = db.query(MangaTitle).count()
chapter_count = db.query(MangaChapter).count()
print(f"  Total titles: {title_count}")
print(f"  Total chapters: {chapter_count}")

# 4. Примеры тайтлов с главами
print("\n[4] Sample titles with chapters:")
titles = db.query(MangaTitle).limit(5).all()
for t in titles:
    ch_count = db.query(MangaChapter).filter(
        MangaChapter.manga_title_id == t.id
    ).count()
    print(f"  {t.canonical_title} ({ch_count} chapters)")

db.close()
print("\n✅ MangaKnowledgeEngine works!")
print("=" * 70)