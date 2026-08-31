import pathlib, re

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

sprint16_block = """
🌐 Sprint 16 — MangaDex API Integration ✅ ЗАВЕРШЁН (13 августа 2026)

📦 Добавлено:
  ✅ MangaDexAdapter (https://api.mangadex.org, без auth)
    - /chapter (RU + safe/suggestive, order[readableAt]=desc)
    - /manga?ids[] (batch fetch 100 тайтлов для titles + covers)
    - Защитный парсинг (None-safe)
    - Фильтрация будущего (publishAt > NOW отсеивается)
  ✅ Интеграция в MangaResearchJob (ReManga + MangaDex вместе)
  ✅ Один pipeline публикует главы из обоих источников

📊 Метрики:
  - ReManga: 20 глав за запрос
  - MangaDex: 20 глав за запрос + batch titles
  - Всего за один прогон: 40 items, 20 обложек
  - RU-переводов в MangaDex: ~93k глав
  - Safe/Suggestive манги: ~5304 тайтла

🎯 Результат:
  - @manga_new_chapters: 28 постов (5 ReManga + MangaDex)
  - Источники: RU-манга (ReManga) + международная (MangaDex)
  - Backup: если один источник упадёт, второй работает

🐛 Решённые проблемы:
  - MangaDex publishAt = 2037 placeholder → используем readableAt
  - MangaDex relationships[].attributes = None → safe_get()
  - BOM в Python файлах → запись через Python, UTF8 без BOM
  - PowerShell encoding → [Console]::OutputEncoding = UTF8

📚 Sprint 15: Manga Chapter Release (завершён)
🌐 Sprint 16: MangaDex API Integration (завершён)
"""

if "Sprint 16" not in s:
    # Вставляем после Sprint 15
    if "Sprint 15" in s:
        s = s.replace("🚀 Следующий шаг: Sprint 16", sprint16_block + "\n🚀 Следующий шаг: Sprint 17")
        f.write_text(s, encoding="utf-8")
        print("STATUS.md updated with Sprint 16")
    else:
        print("Sprint 15 marker not found")
else:
    print("Sprint 16 already exists")