import pathlib

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

sprint18_final = """
📰 Sprint 18 — Telegraph Integration + Chapter Preview ✅ ЗАВЕРШЁН (13 августа 2026)

📦 Добавлено:
  ✅ TelegraphPublisher (engines/telegraph/publisher.py)
    - Создание Telegraph страниц с внешними URL
    - Превью первой главы (5 страниц)
    - Поддержка полного HTML-like контента
  ✅ ReMangaAdapter.fetch_first_chapter_preview()
    - Извлечение первых 5 страниц первой главы
    - API: /api/titles/{slug}/ → first_chapter → /api/titles/chapters/{id}/
    - Обработка pages как списка списков [[{link}], ...]
  ✅ Интеграция в MangaPublishJob v3
    - Каждый пост создаёт Telegraph страницу с превью
    - manga_title_slug сохраняется в metadata
  ✅ TELEGRAPH_ACCESS_TOKEN в docker-compose.yml

📊 Метрики:
  - Telegraph pages: создаются автоматически
  - Превью первой главы: 5 страниц (ReManga CDN без Referer)
  - Telegram posts: с Telegraph ссылками
  - Эмодзи: работают правильно (UTF8 без BOM)

🎯 Результат:
  - @manga_new_chapters: посты с Telegraph страницами
  - Telegraph страницы: обложка + описание + превью + ссылки
  - Превью первой главы: легально (как "Look Inside")

🐛 Решённые проблемы:
  - Telegraph upload 400 → внешние URL
  - PowerShell ASCII → UTF8 без BOM
  - YAML duplicate key → добавили в существующую секцию
  - ReManga API: slug вместо ID для /api/titles/{slug}/
  - pages структура: список списков [[{link}], ...]

🖼️ Sprint 17: Image Acquisition Pipeline (завершён)
📰 Sprint 18: Telegraph Integration + Chapter Preview (завершён)
"""

if "Sprint 18" not in s:
    if "Sprint 17" in s:
        s = s.replace("🚀 Следующий шаг: Sprint 18", sprint18_final + "\n🚀 Следующий шаг: Sprint 19")
        f.write_text(s, encoding="utf-8")
        print("✅ STATUS.md updated with Sprint 18")
    else:
        print("Sprint 17 marker not found")
else:
    print("Sprint 18 already exists")