import pathlib

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

sprint14_step1 = """
🎨 Sprint 14 — Image Acquisition Pipeline
Статус: 🔄 В процессе

✅ Step 1: image_profile в ChannelORM (13 августа 2026)
   - Добавлено поле image_profile (JSON) в ChannelORM
   - SQL миграция через psql (обход SQLAlchemy FK issues)
   - 3 активных канала настроены:
     * АИ Новости: mode=source_first, style=news
     * AI Anime News: mode=source_first, style=anime
     * Test VK Channel: mode=source_first, style=anime
   - Исправлен IndentationError (создание файла через Python в контейнере)
   - Backend стартует без ошибок

⏳ Step 2: SourceImageResolver (in progress)
   - Извлечение og:image из source_url
   - Парсинг HTML (BeautifulSoup)
   - Валидация URL

⏳ Step 3: ImageSearchEngine (pending)
⏳ Step 4: RelevanceValidator (pending)
⏳ Step 5: Рефакторинг ImageEngine (pending)
⏳ Step 6: Обновление ImageJob (pending)
⏳ Step 7: Тестирование (pending)

🎯 Следующий шаг: Step 2 - SourceImageResolver
"""

if "Sprint 14" not in s:
    insert_marker = "Sprint 13.1"
    if insert_marker in s:
        insert_pos = s.find(insert_marker)
        # Находим конец блока Sprint 13.1
        end_pos = s.find("\n\n", insert_pos + len(insert_marker))
        if end_pos != -1:
            s = s[:end_pos+2] + sprint14_step1 + "\n" + s[end_pos+2:]
            f.write_text(s, encoding="utf-8")
            print("✅ STATUS.md updated (Sprint 14 Step 1 added)")
else:
    print("ℹ️ STATUS.md already has Sprint 14")