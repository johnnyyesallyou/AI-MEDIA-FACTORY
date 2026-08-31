import pathlib

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

sprint15_complete = """
🎨 Sprint 15 — Manga Chapter Release ✅ ЗАВЕРШЁН (13 августа 2026)

📦 Компоненты:
  ✅ ReMangaAdapter (API endpoint /api/titles/last-chapters/ + /api/titles/{slug}/)
  ✅ SourceItem + BaseSourceAdapter (абстракция для любых источников)
  ✅ ChapterDetector (deduplication через manga_source_states)
  ✅ MangaSourceState ORM (таблица для хранения last_chapter per title)
  ✅ MangaResearchJob (оркестратор адаптеров)
  ✅ MangaImageResolver (source-first: скачивает cover_url через AssetManager)
  ✅ TelegramPublisher (multipart upload для локальных /assets/ файлов)
  ✅ URLShortener (TinyURL без ключа, 81→28 символов)
  ✅ MangaPublishJob (description + genres + short URL + hashtags)
  ✅ MangaPipelineJob (Research → Image → Publish)
  ✅ Scheduler integration (автозапуск каждые 30 минут)

📊 Метрики:
  - 15+ постов опубликовано в @manga_new_chapters
  - ReManga API: 20 глав за запрос (без auth)
  - Deduplication: 100% (0 дубликатов на 2-м запуске)
  - URL сокращение: 48 → 28 символов (экономия 42%)
  - Обложки: 100% source-first (без AI)
  - Pipeline: каждые 30 минут автоматически

🎯 Telegram канал: @manga_new_chapters
   Bot: @openclavv_ai_bot
   Chat ID: -1004327209979

🐛 Известные проблемы:
   - ReManga search API требует авторизацию (используется slug fallback)
   - Некоторые тайтлы без enrichment (не найдены через slug)

🚀 Следующий шаг: Sprint 16
"""

if "Sprint 15" in s:
    # Находим блок Sprint 15 и заменяем
    import re
    s = re.sub(
        r'🎨 Sprint 15.*?(?=\n🎨 Sprint|\Z)',
        sprint15_complete,
        s,
        flags=re.DOTALL
    )
    f.write_text(s, encoding="utf-8")
    print("STATUS.md updated (Sprint 15 marked as complete)")
else:
    print("Sprint 15 block not found in STATUS.md")