# AI Media Factory — Текущее состояние и план действий

**Дата:** 2026-09-11  
**Статус:** Verification Gate начат  
**Главный документ:** MASTER_ROADMAP.md

---

## 🎯 Главная цель

Превратить набор работающих модулей в управляемую, изолированную, наблюдаемую и масштабируемую платформу.

**Стратегия:**
```
Надёжный один pipeline (ТЕКУЩИЙ ЭТАП)
  ↓
Независимость каналов
  ↓
10 реальных каналов (Pilot Network)
  ↓
Масштабирование до 100+
```

---

## 📊 Текущее состояние

### Завершённые компоненты

✅ **Platform Core** (Event Bus, Engine SDK, Context Manager, DI)  
✅ **Research Layer** (RSS, дедупликация, скоринг, Source Discovery, Smart Selection)  
✅ **Writing & Intelligence** (LLM generation, FactGuard, Evaluation, Revision)  
✅ **Publishing** (Telegram, VK, Publication Layer, Renderers)  
✅ **Channel Profiles** (runtime config source)  
✅ **Automation** (Scheduler, Jobs, per-channel queues)  
✅ **Reliability** (CircuitBreaker, Retry, DLQ, Self-Healing, Health Checks)  

### Тестовое покрытие

- **194 tests passed** (Sprint 75–76)
- **2 tests skipped** (LLM-dependent, require Ollama)
- **0 tests failed**
- **Full regression working**

### Текущий спринт

**Sprint 76.2 — Smart Source Selection** ✅ ЗАВЕРШЁН

Что реализовано:
- `SmartSourceSelector` компонует качество, ротацию и diversity
- QualityRegistry хранит метрики источников
- API для selection, metrics, record-pick
- 13 новых тестов (все passed)

---

## ⚠️ Критическое разделение

> **Готов модуль ≠ интегрирован в pipeline ≠ работает на реальных данных ≠ production ready**

Например:
- ✅ `SmartSourceSelector` существует
- ❓ ResearchJob реально его использует?
- ❓ Selection влияет на фактический Research результат?
- ❓ Это работает с реальными данными?

---

## 🔍 Verification Gate (Sprint 76.V) — НУЖНО СЕЙЧАС

**Цель:** Доказать что Sprint 75.1–76.2 не просто существуют, а реально интегрированы

### Что проверять

1. **Profile Enforcement**
   - ResearchJob получает профиль и применяет его
   - WritingJob получает профиль и применяет его
   - EvaluationJob получает профиль и применяет его

2. **Cross-Channel Isolation**
   - Контент канала A не обрабатывается каналом B
   - Credentials не смешиваются
   - Rate limits независимы

3. **Source Selection Integration**
   - SmartSourceSelector реально вызывается из ResearchJob
   - Topic из профиля передаётся selector'у
   - Выбранные источники используются в Research
   - Rotation работает (разные источники разные дни)

4. **Sprint 60 Tests Status**
   - Два тета документированы
   - Причина статуса (skipped/xfail/fixed) ясна

### План проверки

**Документ:** `VERIFICATION_GATE_76V.md` (в корне проекта)

Содержит:
- Чек-лист для всех 7 проверок
- 3 тестовых сценария (code examples)
- Результаты после проверки

### Когда завершить

Verification Gate закрывается когда:
- ✅ Все 7 проверок пройдены
- ✅ Интеграционные тесты written и passed
- ✅ STATUS.md обновлён с результатами
- ✅ Рабочее дерево чистое

Только после этого → Sprint 76.3

---

## 📋 Ближайший план действий

### Этап 0: Verification (текущий)

**Sprint 76.V** — Verification Gate
- [ ] Проверить Profile Enforcement
- [ ] Проверить cross-channel isolation
- [ ] Проверить Source Selection integration
- [ ] Обновить документацию

**Ожидаемая длительность:** 2–3 часа

### Этап 1: Source Discovery Completion (Sprint 76.3–76.5)

**76.3** — Subscribe.ru discovery интеграция
- Source discovery API
- Нормализация результатов
- Валидация URL

**76.4** — Source Registry persistence
- QualityRegistry в PostgreSQL
- Сохранение после restart
- Миграция БД

**76.5** — Source Health & Quarantine
- Automatic health monitoring
- Source quarantine logic
- Fallback на известные источники

### Этап 2: Learning Loop Foundation (Sprint 77–77.3)

**77** — Experience Store
- Сохранение решений (выбранная тема, источник, angle, результат)
- Attribution (что выбрали → какой результат)

**77.1** — Analytics Attribution
- Сбор Telegram metrics
- Связывание публикации с её результатом
- Performance baseline

**77.2** — Learning Signals
- Pattern extraction (какие темы успешны)
- Recommendations engine
- Controlled adaptation (без автоматических изменений без feature flag)

### Этап 3: Universal Pipeline & Channels (Sprint 78–80)

**78** — Channel Catalog
- Структурированный каталог тематик
- Tier-модель (Tier 1–4)
- Templates для создания каналов

**78.1–78.2** — Channel Profiles v2
- Единый runtime contract
- Versioning и rollback

**79–79.2** — Universal Pipeline
- Отделение от Telegram-specific логики
- Platform Adapter contract
- Multi-platform ready

**80–80.2** — Dashboard Onboarding & Readiness
- Create Channel flow в dashboard
- Readiness checks перед Start
- Dry Run mode

### Этап 4: Reliability Gate (Sprint 81–82)

**81** — Production Reliability
- Idempotent publishing
- Observability (structured logs, metrics)
- Recovery procedures

**82** — Pilot Network (10 каналов)
- Запустить реальную сеть
- Проверить независимость
- Операционные процедуры

---

## 🗂️ Важные документы

### Стратегические

- **MASTER_ROADMAP.md** — полный план до productization (96 спринтов, 16 фаз)
- **ARCHITECTURE.md** — система архитектура
- **STATUS.md** — текущий статус и история спринтов

### Операционные

- **VERIFICATION_GATE_76V.md** — чек-лист проверок (этот спринт)
- **AI_CONTEXT.md** — правила разработки
- **TASK.md** — текущие задачи и backlog

### Относящиеся к памяти

- `memory/MEMORY.md` — index
- `memory/master-roadmap.md` — краткая справка (загружается в каждую сессию)

---

## 🔧 Как работать с проектом

### Перед началом работы

1. Прочитай **MASTER_ROADMAP.md** (общее видение)
2. Прочитай **STATUS.md** (текущее состояние)
3. Прочитай **VERIFICATION_GATE_76V.md** (если работаешь на 76.V)

### При добавлении новой функции

1. Есть ли она в MASTER_ROADMAP? (Если нет — согласовать)
2. В какой фазе/спринте она?
3. Какой уровень готовности нужен? (Implementation → Integration → Reliability → Production validation)
4. После реализации — обновить STATUS.md

### Перед коммитом

- Пройти тесты: `pytest tests/ -v`
- Обновить STATUS.md с результатами
- Проверить что нет регрессии: `194 passed, 2 skipped`
- Заголовок коммита отражает что сделано и зачем

---

## 🚀 Стратегический момент

Проект находится в **критической точке:**

✅ Все основные компоненты реализованы  
✅ Код компилируется и тесты passed  
❓ **Но:** Нужно доказать что всё реально работает вместе

**Следующие 4 недели:**
1. Verification Gate (убедиться что интеграция настоящая)
2. Source Discovery completion (закончить источники)
3. Learning Loop (начать улучшать на основе опыта)
4. Dashboard + Pilot Network (переход к реальному использованию)

После этого → масштабирование и productization

---

## 📞 Что делать если что-то неясно

1. Проверь `MASTER_ROADMAP.md` — там есть ответ на большинство вопросов
2. Посмотри `memory/master-roadmap.md` — краткая версия
3. Проверь `VERIFICATION_GATE_76V.md` — если вопрос про текущий спринт
4. Читай `AI_CONTEXT.md` — правила разработки

---

## ✨ Главный принцип

> **Не количество каналов, а предсказуемость поведения системы**

Правильный путь:
- 1 надёжный pipeline ✅ (в процессе верификации)
- 10 реальных каналов (будет)
- 25 → 50 → 100+ каналов (потом)

Неправильный путь:
- Много функций + много каналов + никто не знает почему это ломается ❌

---

**Текущий фокус:** Sprint 76.V Verification Gate  
**Следующий фокус:** Sprint 76.3 Subscribe.ru Integration  
**Главный документ:** MASTER_ROADMAP.md
