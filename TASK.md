# AI Media Factory
Current Task

Task:
Sprint 14 - Image Acquisition Pipeline

Status:
In Progress

Current Objective
Step 2: SourceImageResolver - извлечение og:image из source_url

Completed Steps
✅ Step 1: Добавили image_profile в ChannelORM
   - Поле JSON в БД и модели
   - Миграция через psql
   - 3 канала настроены (News/Anime profiles)
   - Backend работает без ошибок

Steps
Step 2: Создать SourceImageResolver (извлечение og:image из source_url)
Status: Active

Step 3: Создать ImageSearchEngine (поиск изображений по entity)
Status: Pending

Step 4: Создать RelevanceValidator (проверка соответствия новости)
Status: Pending

Step 5: Рефакторить ImageEngine с цепочкой resolver'ов
Status: Pending

Step 6: Обновить ImageJob для использования нового пайплайна
Status: Pending

Step 7: Тестирование и документация
Status: Pending

Rules
- Do not break existing publishing pipeline
- Image acquisition before image generation
- AssetManager is mandatory (local storage)
- Relevance validation is required
- Update STATUS.md after each step

End Task
