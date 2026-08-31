import pathlib

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

sprint13_1_final = """
🎨 Sprint 13.1 — Image Domain Stabilization
Статус: ✅ ЗАВЕРШЁН
Дата завершения: 13 августа 2026
Продолжительность: 1 день

✅ Реализовано
1. AssetManager интеграция в ImageJob
   - Все картинки скачиваются локально через AssetManager
   - Fallback: если AssetManager упал → внешний URL
   - Результат: 69 assets в БД (было 2 до Sprint 13.1)

2. Определение формата файла по Content-Type
   - PNG/JPEG/WebP определяется автоматически
   - Правильное расширение в filename
   - Результат: реальные форматы в БД

3. Фильтрация на уровне БД
   - ImageJob берёт только posts без image_url (SQL WHERE)
   - Исправлена пагинация
   - Idempotency подтверждена (3 runs → 1 asset)

4. Параметры канала (style/platform)
   - ImageJob читает style_profile и platform из ChannelORM
   - Маппинг: minimal→minimal, anime→anime, realistic→realistic
   - Результат: разные каналы имеют разные стили

5. End-to-End тест
   - Research → Writing → Image → Publish
   - Результат: 13 новостей создано, 3 изображения сгенерировано
   - PublishJob пропущен (rate limit: 10/10 сегодня)

📈 Метрики Sprint 13.1

До Sprint 13.1:
- assets: 2
- content.image_url: 41 (все внешние URL)
- content.asset_id: 1
- Ratio: 4.9%

После Sprint 13.1:
- assets: 69
- content.image_url: 119 (69 локальных + 50 внешних)
- content.asset_id: 69
- Ratio: 58% (значительно улучшено)

E2E тест:
- Research: 13 новостей создано
- Writing: 13 items обработано
- Image: 3 сгенерировано, 3 assets создано
- Publish: пропущен (rate limit)

🎯 Следующий шаг: Sprint 14 — Image Acquisition Pipeline
- Source-first подход (source image → search → AI fallback)
- Image Profile (News/Anime Episodes/Anime General)
- Relevance Validator (entity matching)
"""

if "Sprint 13.1" not in s:
    insert_marker = "Sprint 13 — ComfyUI"
    if insert_marker in s:
        insert_pos = s.find(insert_marker)
        s = s[:insert_pos] + sprint13_1_final + "\n" + s[insert_pos:]
        f.write_text(s, encoding="utf-8")
        print("✅ STATUS.md updated (Sprint 13.1 finalized)")
else:
    print("ℹ️ STATUS.md already has Sprint 13.1")