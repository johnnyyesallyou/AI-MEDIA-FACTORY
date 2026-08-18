import pathlib

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

sprint20_block = """
🎯 Sprint 20 — Channel Content Profiles ✅ ЗАВЕРШЁН (13 августа 2026)

📦 Добавлено:
  ✅ engines/channel_profiles.py
    - Конфигурационный слой для каналов
    - 3 базовых профиля: ai_news, anime_news, manga_releases
    - Deep-merge: БД-конфиг + дефолты по ключу
    - guess_profile_key() — автоопределение по имени канала
  ✅ ChannelORM.content_profile (JSONB колонка)
    - Хранение profile_key + overrides
    - Миграция ALTER TABLE ADD COLUMN
    - Seed: все каналы привязаны к профилям

📊 Метрики:
  - 5 каналов сконфигурированы
  - Профили: ai_news (3), anime_news (1), manga_releases (1)
  - Deep-merge работает корректно
  - Backend перезапустился без ошибок

🎯 Результат:
  - Pipeline теперь читает профиль канала
  - Разные правила для разных каналов:
    * manga_releases: RU-only, Telegraph, inline кнопки
    * ai_news: og:image → AI fallback, без RU-фильтра
    * anime_news: anime_visual, стиль anime
  - Один Research → разные Publishing rules

📱 Sprint 19: Telegram Improvements + RU-only (завершён)
🎯 Sprint 20: Channel Content Profiles (завершён)
"""

if "Sprint 20" not in s:
    if "Sprint 19" in s:
        s = s.replace("🚀 Следующий шаг: Sprint 20", sprint20_block + "\n🚀 Следующий шаг: Sprint 21")
        f.write_text(s, encoding="utf-8")
        print("✅ STATUS.md updated with Sprint 20")
    else:
        print("Sprint 19 marker not found")
else:
    print("Sprint 20 already exists")