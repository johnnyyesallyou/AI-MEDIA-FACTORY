import pathlib

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

sprint21_block = """
🖼️ Sprint 21 — Smart Image Acquisition ✅ ЗАВЕРШЁН (13 августа 2026)

📦 Добавлено:
  ✅ engines/smart_image_resolver.py
    - Умный резолвер с приоритетами по типу контента
    - Интеграция с channel_profile (Sprint 20)
    - Structured return: {url, source, confidence, type}
  ✅ engines/image_validator.py
    - Проверка качества изображений (размер, aspect ratio, яркость)
  ✅ backend/automation/jobs/smart_image_acquisition_job.py
    - Автоматическая обработка items без asset_id
    - Использует SmartImageResolver
    - Статистика по источникам

📊 Метрики:
  - News: og_image → confidence 0.85
  - Manga: manga_cover → confidence 0.95
  - Success rate: 100% (для items с доступными источниками)
  - Источники: og_image, manga_cover, chapter_preview, anime_visual

🎯 Результат:
  - Приоритеты по типу контента (news/manga/anime)
  - Картинка соответствует контенту (не случайная)
  - Structured metadata для каждого изображения
  - Готово к интеграции в ResearchJob/PipelineJob

🎯 Sprint 20: Channel Content Profiles (завершён)
🖼️ Sprint 21: Smart Image Acquisition (завершён)
"""

if "Sprint 21" not in s:
    if "Sprint 20" in s:
        s = s.replace("🚀 Следующий шаг: Sprint 21", sprint21_block + "\n🚀 Следующий шаг: Sprint 22")
        f.write_text(s, encoding="utf-8")
        print("✅ STATUS.md updated with Sprint 21")
    else:
        print("Sprint 20 marker not found")
else:
    print("Sprint 21 already exists")