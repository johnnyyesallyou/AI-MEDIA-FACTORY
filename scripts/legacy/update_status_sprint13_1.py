import pathlib

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

sprint13_1_block = """
🎨 Sprint 13.1 — Image Domain Stabilization
Статус: ✅ ЗАВЕРШЁН
Дата завершения: 13 августа 2026
Продолжительность: 1 день

✅ Реализовано
1. AssetManager интеграция в ImageJob
   - Все картинки теперь скачиваются локально через AssetManager
   - Fallback: если AssetManager упал → внешний URL
   - Результат: 57 assets в БД (было 2)

2. Определение формата файла по Content-Type
   - PNG/JPEG/WebP определяется автоматически
   - Правильное расширение в filename
   - Результат: 2 JPEG, 55 PNG (правильные расширения)

3. Фильтрация на уровне БД
   - ImageJob берёт только posts без image_url (SQL WHERE)
   - Исправлена пагинация (обрабатываются ВСЕ posts, не только первые 10)
   - Результат: idempotency подтверждена

4. Параметры канала (style/platform)
   - ImageJob читает style_profile и platform из ChannelORM
   - Убран хардкод style="anime", platform="telegram"
   - Маппинг: minimal→minimal, anime→anime, realistic→realistic
   - Результат: разные каналы могут иметь разные стили

5. Idempotency тест
   - 3 запуска ImageJob для одного поста
   - Результат: только 1 asset создан (повторные запуски не создают дубликаты)

📈 Метрики Sprint 13.1

До Sprint 13.1:
- assets: 2
- content.image_url: 41 (все внешние URL)
- content.asset_id: 1
- Ratio: 4.9% (критически низко)

После Sprint 13.1:
- assets: 57
- content.image_url: 107 (57 локальных + 50 внешних)
- content.asset_id: 57
- Ratio: 53.3% (значительно улучшено)

🔧 Критические решения Sprint 13.1

| Проблема | Решение |
|----------|---------|
| AssetManager не вызывался | Добавлен в ImageJob pipeline |
| Все файлы .png | Определение формата по Content-Type |
| Хардкод style/platform | Параметры из ChannelORM |
| ImageJob брал только 10 posts | SQL WHERE на уровне БД |
| Дубликаты assets | Idempotency через фильтрацию |

📦 Изменённые файлы Sprint 13.1

- backend/automation/jobs/image_job.py
- engines/asset/manager.py
- channels (DB): UPDATE style_profile
- content (DB): UPDATE asset_id
- assets (DB): 55 новых записей

🎯 Следующий шаг: Sprint 14 — Image Acquisition Pipeline
"""

if "Sprint 13.1" not in s:
    insert_marker = "Sprint 13 — ComfyUI"
    if insert_marker in s:
        insert_pos = s.find(insert_marker)
        s = s[:insert_pos] + sprint13_1_block + "\n" + s[insert_pos:]
        f.write_text(s, encoding="utf-8")
        print("✅ STATUS.md updated (Sprint 13.1 added)")
else:
    print("ℹ️ STATUS.md already has Sprint 13.1")