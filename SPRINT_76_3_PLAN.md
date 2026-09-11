# Sprint 76.3 — Subscribe.ru Discovery Integration

**Дата начала:** 2026-09-11  
**Статус:** IN PROGRESS  
**Цель:** Интегрировать Subscribe.ru для автоматического discovery источников

---

## План реализации

### 1. Subscribe.ru Adapter

**Файл:** `engines/source_adapters/subscribe_ru_adapter.py`

Функционал:
- Запросить Subscribe.ru API для topic/category
- Парсить результаты
- Нормализовать в единый формат
- Валидировать URL как RSS

### 2. Discovery Integration

**Файл:** `engines/source_discovery_integrators.py` (новый)

Функционал:
- Получить результаты от Subscribe.ru
- Нормализовать URL
- Удалить дубликаты
- Оценить качество
- Вернуть отсортированный список

### 3. API Endpoint

**Файл:** `backend/app/api/v1/sources.py` (расширить)

Endpoint:
- `POST /discover/subscribe-ru` — запустить Subscribe.ru discovery
- `GET /discover/subscribe-ru/status` — статус discovery

### 4. Tests

**Файл:** `tests/test_subscribe_ru_discovery.py`

Тесты:
- Subscribe.ru API запрос
- Парсинг результатов
- Нормализация URL
- Дедупликация
- Валидация как RSS

---

## Архитектура

```
User Input (topic, language)
  ↓
SubscribeRuAdapter.discover(topic, language)
  ↓
API Request to Subscribe.ru
  ↓
Parse Results
  ↓
Normalize URLs
  ↓
Validate as RSS/Atom
  ↓
Score Results
  ↓
Deduplicate
  ↓
Return Sorted List
```

---

## Subscribe.ru API Research

Subscribe.ru предоставляет:
- Search API (поиск по категориям/тегам)
- Catalog API (каталог источников)
- RSS feeds (прямые ссылки на фиды)

Нужно:
1. Найти правильный endpoint
2. Понять формат запроса/ответа
3. Извлечь RSS URLs
4. Валидировать

---

## Acceptance Criteria

- [ ] Subscribe.ru adapter реализован
- [ ] Discovery интегрирован в pipeline
- [ ] API endpoint работает
- [ ] Тесты написаны и passed
- [ ] Результаты валидируются как RSS
- [ ] Дедупликация работает
- [ ] Падение Subscribe.ru не ломает pipeline (fallback на известные источники)

---

**Статус:** Начинаю реализацию  
**Документация:** Обновляется по мере разработки
