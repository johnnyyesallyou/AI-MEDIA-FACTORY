import pathlib

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

sprint22_block = """
🔌 Sprint 22 — Manga Sources Expansion ✅ ЗАВЕРШЁН (17 августа 2026)

📦 Добавлено:
  ✅ engines/source_adapters/base_manga_adapter.py
    - BaseMangaAdapter (абстрактный базовый класс)
    - MangaItem dataclass (единая структура для всех источников)
  ✅ engines/source_adapters/manga_registry.py
    - MangaRegistry (единая точка доступа)
    - fetch_from(source), fetch_all(), fetch_with_dedup()
    - Автоматическая дедупликация по (source, external_id)
  ✅ Рефакторинг ReMangaAdapter + MangaDexAdapter
    - Наследование от BaseMangaAdapter
    - Новый метод fetch_latest_chapters_manga()
    - Конвертация SourceItem → MangaItem

📊 Метрики:
  - 2 источника: remanga + mangadex
  - Единый интерфейс для всех адаптеров
  - Дедупликация работает (5+5=10 unique)
  - MangaResearchJob использует registry

🎯 Результат:
  - Все manga sources через единый интерфейс
  - MangaRegistry.fetch_all() возвращает главы со всех источников
  - Дедупликация предотвращает повторные публикации
  - Легко добавлять новые источники (ZazaZa, ReadManga в будущем)

🖼️ Sprint 21: Smart Image Acquisition (завершён)
🔌 Sprint 22: Manga Sources Expansion (завершён)
"""

if "Sprint 22" not in s:
    if "Sprint 21" in s:
        s = s.replace("🚀 Следующий шаг: Sprint 22", sprint22_block + "\n🚀 Следующий шаг: Sprint 23")
        f.write_text(s, encoding="utf-8")
        print("✅ STATUS.md updated with Sprint 22")
    else:
        print("Sprint 21 marker not found")
else:
    print("Sprint 22 already exists")