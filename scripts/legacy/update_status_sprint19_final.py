import pathlib

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

sprint19_final = """
📱 Sprint 19 — Telegram Improvements + RU-only ✅ ЗАВЕРШЁН (13 августа 2026)

📦 Добавлено:
  ✅ TelegramRateLimiter (engines/telegram/rate_limiter.py)
    - 2.5 сек между постами (24/мин)
    - Обработка 429 FloodWait
  ✅ TelegramPublisher v2 (engines/telegram/publisher.py)
    - Inline-кнопки (Telegraph + Источник)
  ✅ RU-only фильтр
    - Пропуск тайтлов без кириллицы
    - Пропуск английских описаний
    - 145 EN постов помечены как skipped_en
  ✅ Enrichment (MangaDex + ReManga)
    - Описания из API (RU/EN)
    - Жанры (теги)
    - Обложки (скачивание с CDN)
  ✅ Fix "Unknown" titles (141 item)

📊 Метрики:
  - 107 RU постов опубликовано
  - 101 ReManga + 6 MangaDex
  - 145 EN постов пропущено
  - Inline-кнопки во всех постах
  - Rate limit: 24 постов/мин

🎯 Результат:
  - Bulk publish без Telegram-банов
  - Только русские посты в канале
  - Полные описания + хэштеги
  - Inline-кнопки для быстрого доступа

⚠️ Ограничения:
  - Превью первых глав не работает (все image hosting блокируют IP)
  - Для превью нужен собственный прокси-сервер (Sprint 20+)

📱 Sprint 19: Telegram Improvements + RU-only (завершён)
"""

if "Sprint 19" not in s:
    if "Sprint 18" in s:
        s = s.replace("🚀 Следующий шаг: Sprint 19", sprint19_final + "\n🚀 Следующий шаг: Sprint 20")
        f.write_text(s, encoding="utf-8")
        print("✅ STATUS.md updated with Sprint 19")
    else:
        print("Sprint 18 marker not found")
else:
    print("Sprint 19 already exists")