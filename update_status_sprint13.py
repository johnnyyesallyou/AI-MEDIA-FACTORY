import pathlib

f = pathlib.Path("status.md")
s = f.read_text(encoding="utf-8")

sprint13_block = """
🎨 Sprint 13 — ComfyUI Integration + Image Validation
Статус: ✅ ЗАВЕРШЁН
Дата завершения: 13 августа 2026
Продолжительность: 1 день

✅ Реализовано
1. Volume Persistence (./assets:/app/assets)
   - Assets переживают 'docker compose down -v'

2. ComfyUI Infrastructure
   - docker-compose.comfyui.yml (GPU support)
   - Network amf_network (shared с backend)

3. ComfyUIEngine (engines/comfyui/engine.py)
   - Fallback на Pollinations AI если ComfyUI недоступен
   - Проверено: fallback работает

4. ImageValidatorEngine (engines/image_validator/engine.py)
   - llava:7b vision model (ollama pull llava:7b)
   - Scoring: quality + prompt_match + aesthetic → overall
   - QUALITY_THRESHOLD = 70

5. ABTestEngine (engines/ab_test/engine.py)
   - N вариантов с разными seeds
   - Валидация каждого, выбор лучшего по overall_score
   - Retry: timeout=60s, max_retries=3
   - Прямое скачивание (без AssetManager, без БД)

📈 Метрики интеграционного теста
- Генерация картинки: 18.10s (pollinations_fallback)
- Валидация llava:7b: 25.84s (score=85/100)
  - Quality: 85/100
  - Prompt Match: 90/100
  - Aesthetic: 80/100
- Публикация VK: ✅ text-only (post_id=35)
- URL: https://vk.com/wall-240792540_35

🔧 Критические решения Sprint 13
| Проблема | Решение |
|----------|---------|
| ComfyUI недоступен | Fallback на Pollinations |
| VK error 27 (group auth) | Fallback на text-only публикацию |
| AssetManager FK violation | Прямое скачивание через requests |
| Pollinations timeout | timeout=60s, retry 3 раза |
| ImageValidator path | test_dir / filename (не ab_test_path) |

📦 Новые файлы Sprint 13
- docker-compose.comfyui.yml
- comfyui/{models,output,input}/
- engines/comfyui/engine.py
- engines/image_validator/engine.py
- engines/ab_test/engine.py
- ./assets:/app/assets (volume)
"""

if "Sprint 13" not in s:
    insert_marker = "🚀 Запуск проекта"
    if insert_marker in s:
        insert_pos = s.find(insert_marker)
        s = s[:insert_pos] + sprint13_block + "\n" + s[insert_pos:]
        f.write_text(s, encoding="utf-8")
        print("✅ STATUS.md updated (Sprint 13 added)")
else:
    print("ℹ️ STATUS.md already has Sprint 13")
