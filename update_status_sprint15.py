import pathlib

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

sprint15_step4 = """
🎨 Sprint 15 — Manga Chapter Release
Статус: 🔄 В процессе

✅ Step 1: Probe + разведка источников (13 августа 2026)
   - ReManga: официальный API /api/titles/last-chapters/ (без auth)
   - ZazaZa: SPA, API заблокирован → отложено (Playwright/ReadManga позже)
   - Решение: начинаем с ReManga

✅ Step 2: Source Adapter Framework (13 августа 2026)
   - BaseSourceAdapter (абстрактный)
   - SourceItem (унифицированная модель данных)
   - ReMangaAdapter (реальное API, cover URLs, title URLs)
   - Файлы: engines/source_adapters/{base.py, remanga_adapter.py, __init__.py}

✅ Step 3: ChapterDetector (13 августа 2026)
   - MangaSourceStateORM (таблица manga_source_states)
   - Детектор группирует по (source, title_id), берёт MAX chapter
   - Deduplication: 2-й запуск создаёт 0 новых записей
   - Файлы: engines/chapter_detector.py, core/models/manga_source_state_orm.py

✅ Step 4: MangaResearchJob (13 августа 2026)
   - Оркестратор: адаптеры → детектор → ContentORM
   - Манга-канал создаётся через SQL (обход SQLAlchemy FK issues)
   - Метаданные в source_text (JSON)
   - Тест: 10 research items, deduplication работает
   - Файл: backend/automation/jobs/manga_research_job.py

⏳ Step 5: ImageResolver (source-first для обложек)
⏳ Step 6: Интеграция с Writing/Evaluation pipeline
⏳ Step 7: Telegram-канал + credentials
⏳ Step 8: PublishJob интеграция
⏳ Step 9: E2E тест + scheduler

📊 Метрики Sprint 15
- ReManga API: 20 глав за запрос (без auth)
- Deduplication: 10 → 0 (2-й запуск)
- Research items создано: 10
- Уникальных тайтлов: 6 (Акула, Я вышел из игры, ...)

🐛 Известные баги
- URL артефакт у "Акула": <29.04.2026>shark_ (санитизация нужна)
"""

if "Sprint 15" not in s:
    insert_marker = "Sprint 14"
    if insert_marker in s:
        insert_pos = s.find(insert_marker)
        end_pos = s.find("\n\n", insert_pos + len(insert_marker))
        if end_pos != -1:
            s = s[:end_pos+2] + sprint15_step4 + "\n" + s[end_pos+2:]
            f.write_text(s, encoding="utf-8")
            print("STATUS.md updated")
else:
    print("Sprint 15 already in STATUS.md")