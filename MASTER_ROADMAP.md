# AI Media Factory — Master Roadmap

**Версия:** 1.0  
**Дата:** 2026-09-11  
**Статус:** Основной документ стратегии развития

---

## Содержание

1. [Финальная цель](#финальная-цель-проекта)
2. [Принципиальная стратегия](#принципиальная-стратегия-развития)
3. [Уровни готовности](#уровни-готовности-каждого-компонента)
4. [Текущее состояние](#текущее-состояние-проекта)
5. [Фазы развития](#фазы-развития)
6. [Модель готовности](#финальная-модель-готовности-проекта)
7. [Последовательность спринтов](#итоговая-последовательность-спринтов)
8. [Немедленные действия](#что-делать-прямо-сейчас)

---

## Финальная цель проекта

AI Media Factory должна позволять пользователю:

1. Создать канал через Dashboard
2. Выбрать тематику из Channel Catalog
3. Выбрать или создать Channel Profile
4. Настроить язык, стиль, аудиторию, длину и частоту публикаций
5. Подключить Telegram или другую платформу
6. Настроить источники либо включить автоматический discovery
7. Нажать Start
8. Получить полностью автономный цикл:

```
Channel
  ↓
Channel Profile
  ↓
Source Discovery / Source Registry
  ↓
Research
  ↓
Deduplication / Scoring
  ↓
Decision Engine
  ↓
Content Brief
  ↓
Writing
  ↓
Evaluation
  ↓
Revision
  ↓
Image / Media
  ↓
Publishing
  ↓
Analytics
  ↓
Learning Loop
  ↓
Improved future decisions
```

---

## Принципиальная стратегия развития

**Неправильный путь:**
```
Добавили много функций
  ↓
Создали сотни каналов
  ↓
Пытаемся понять, почему всё нестабильно
```

**Правильный путь:**
```
Надёжный один pipeline
  ↓
Независимость каналов
  ↓
10 реальных каналов
  ↓
Автоматизация управления
  ↓
25 каналов
  ↓
50 каналов
  ↓
100+ каналов
  ↓
Мультплатформенность
  ↓
Полноценный SaaS / productization
```

**Главная цель ближайших этапов — не количество каналов, а предсказуемость поведения системы.**

---

## Уровни готовности каждого компонента

Каждая крупная функция считается завершённой только после прохождения четырёх уровней:

| Уровень | Что означает |
|---------|------------|
| **Implementation** | Код реализован |
| **Integration** | Код подключён к общему pipeline |
| **Reliability** | Есть тесты, fallback, retry и обработка отказов |
| **Production validation** | Проверено на реальных каналах и длительной работе |

**Важное разделение:**
> Готов модуль ≠ модуль подключён к реальному pipeline ≠ модуль доказал корректность на реальных данных ≠ платформа готова к масштабированию

Наличие `SmartSourceSelector` в проекте ещё не означает, что ResearchJob действительно использует его в рабочем автономном цикле.

---

## Текущее состояние проекта

### Platform Core
- Event Bus, Engine SDK, BaseEngine lifecycle
- Context Manager, Repository Layer, Dependency Injection
- Health System, Metrics System, Capability Registry

### Research
- RSS ingestion, дедупликация, scoring, importance score
- Сохранение в PostgreSQL, embeddings
- Source Discovery 76.1, Smart Source Selection 76.2

### Intelligence Layer
- Decision Engine, Content Brief Generator, Content Memory

### Writing и Evaluation
- Writing Engine v2, profile-aware prompts
- FactGuard, Grammar/Style validators, OutputGuard
- EvaluatorEngine, revision/re-evaluation flow

### Automation
- Automation Manager, Automation Runner, Scheduler
- ResearchJob, WritingJob, EvaluationJob, PublishJob
- per-channel queues, workers, RetryPolicy, RateLimitPolicy

### Telegram
- Telegram Publisher, bot token сохранение
- Публикация approved content, message ID tracking
- Content Page, Dashboard connection

### Channel Profiles
- Шаблоны, профили, runtime enforcement
- Исправлена cross-channel contamination (Sprint 75.3)

### Reliability
- Regression suite (194 passed, 2 skipped)
- Исправления изоляции каналов
- Обработка очередей и retry
- Health/metrics foundation

---

## Фазы развития

### Фаза 0: Verification текущей реализации

**Sprint 76.V — Verification Gate**

Подтвердить, что Sprint 75.1–76.2 не просто существуют в коде, а реально подключены:

- ✓ Profile Enforcement в Research, Writing, Evaluation jobs
- ✓ Cross-channel isolation
- ✓ Source Selection integration
- ✓ QualityRegistry persistence
- ✓ Статус двух Sprint 60 tests документирован

### Фаза 1: Завершение Source Discovery

- **Sprint 76.3** — Subscribe.ru Discovery Integration
- **Sprint 76.4** — Source Registry Persistence
- **Sprint 76.5** — Source Health и Quarantine

### Фаза 2: Learning Loop Foundation

- **Sprint 77** — Experience Store
- **Sprint 77.1** — Analytics Attribution
- **Sprint 77.2** — Learning Signals
- **Sprint 77.3** — Controlled Adaptation

### Фаза 3: Channel Catalog и Channel Profiles v2

- **Sprint 78** — Channel Catalog
- **Sprint 78.1** — Channel Profiles v2
- **Sprint 78.2** — Profile Versioning и Overrides

### Фаза 4: Universal Pipeline

- **Sprint 79** — Universal Content Model
- **Sprint 79.1** — Universal Pipeline Orchestrator
- **Sprint 79.2** — Platform Adapter Contract

### Фаза 5: Dashboard Onboarding и Readiness

- **Sprint 80** — Dashboard Onboarding
- **Sprint 80.1** — Channel Readiness
- **Sprint 80.2** — Dry Run и Preview

### Фаза 6: Production Reliability Gate

- **Sprint 81** — Reliability Hardening
- **Sprint 81.1** — Idempotent Publishing
- **Sprint 81.2** — Observability
- **Sprint 81.3** — Recovery и Operational Controls

### Фаза 7: Pilot Network — 10 реальных каналов

- **Sprint 82** — Pilot Network
- **Sprint 82.1** — Pilot Operations
- **Sprint 82.2** — Human-in-the-Loop

### Фаза 8: Image и Media Pipeline

- **Sprint 83** — Image Policy и Media Assets
- **Sprint 83.1** — Image Generation и Validation
- **Sprint 83.2** — Short Video Foundation

### Фаза 9: Analytics Dashboard и Control Center

- **Sprint 84** — Control Center
- **Sprint 84.1** — Performance Analytics

### Фаза 10: Smart Scaling

- **Sprint 85** — Scaling 10 → 25
- **Sprint 85.1** — Channel Operations Automation
- **Sprint 86** — Cost Control
- **Sprint 87** — Scaling 25 → 50

### Фаза 11: Security и Production Infrastructure

- **Sprint 88** — Security
- **Sprint 89** — Deployment Architecture
- **Sprint 89.1** — Backup и Recovery

### Фаза 12: Multi-platform Expansion

- **Sprint 90** — VK Adapter
- **Sprint 90.1** — Multi-platform Content Variants
- **Sprint 91** — Multi-platform Pilot

### Фаза 13: Advanced Learning Loop

- **Sprint 92** — Recommendation Engine
- **Sprint 92.1** — Controlled Experiments
- **Sprint 93** — A/B Testing

### Фаза 14: Scaling 50 → 100+

- **Sprint 94** — Scaling 50 → 100+

### Фаза 15: Production Hardening

- **Sprint 95** — Performance и Stability
- **Sprint 95.1** — API и Compatibility
- **Sprint 95.2** — Operational Runbooks

### Фаза 16: Productization

- **Sprint 96** — Multi-user Architecture
- **Sprint 96.1** — Billing и Quotas
- **Sprint 96.2** — Customer Onboarding

---

## Финальная модель готовности проекта

### Архитектура

- [ ] Universal Pipeline отделён от platform adapters
- [ ] Channel Profile — единый runtime source
- [ ] Нет cross-channel contamination
- [ ] Нет hardcoded channel-specific logic
- [ ] Есть единые контракты
- [ ] Состояние pipeline сохраняется
- [ ] Есть versioning и rollback

### Функциональность

- [ ] Создание канала через Dashboard
- [ ] Channel Catalog
- [ ] Channel Profiles
- [ ] Source Discovery
- [ ] Source Registry
- [ ] Smart Source Selection
- [ ] Research → Decision → Brief → Writing → Evaluation → Revision
- [ ] Image/Media Pipeline
- [ ] Publishing
- [ ] Analytics
- [ ] Learning Loop
- [ ] Pause/Resume, Retry, Manual Approval, Dry Run

### Надёжность

- [ ] Integration tests
- [ ] E2E tests
- [ ] Idempotent publishing
- [ ] Retry, timeout, recovery
- [ ] Graceful shutdown
- [ ] Worker restart
- [ ] Failure isolation
- [ ] Backup/restore
- [ ] Документированные skipped tests

### Безопасность

- [ ] Secrets management
- [ ] Credentials isolation
- [ ] Нет secrets в логах
- [ ] Access control
- [ ] Audit
- [ ] Secure production environment
- [ ] Credential rotation

### Масштабирование

- [ ] 10 каналов стабильно
- [ ] 25 каналов стабильно
- [ ] 50 каналов стабильно
- [ ] 100+ каналов без ручной настройки каждого
- [ ] Контролируемая стоимость
- [ ] Наблюдаемость
- [ ] Независимость каналов

### Эксплуатация

- [ ] Проект работает без постоянно включённого домашнего ПК
- [ ] Есть staging и production
- [ ] Есть backups
- [ ] Есть alerts
- [ ] Есть runbooks
- [ ] Есть recovery procedure
- [ ] Есть incident response
- [ ] Есть план обновления и rollback

---

## Итоговая последовательность спринтов

```
76.2 Smart Source Selection (ТЕКУЩИЙ)
  ↓
76.V Verification Gate
  ↓
76.3 Subscribe.ru Discovery Integration
  ↓
76.4 Source Registry Persistence
  ↓
76.5 Source Health / Quarantine
  ↓
77 Experience Store
  ↓
77.1 Analytics Attribution
  ↓
77.2 Learning Signals
  ↓
77.3 Controlled Adaptation
  ↓
78 Channel Catalog
  ↓
78.1 Channel Profiles v2
  ↓
78.2 Profile Versioning / Overrides
  ↓
79 Universal Content Model
  ↓
79.1 Universal Pipeline Orchestrator
  ↓
79.2 Platform Adapter Contract
  ↓
80 Dashboard Onboarding
  ↓
80.1 Channel Readiness
  ↓
80.2 Dry Run / Preview
  ↓
81 Reliability Hardening
  ↓
81.1 Idempotent Publishing
  ↓
81.2 Observability
  ↓
81.3 Recovery / Operational Controls
  ↓
82 Pilot Network — 10 Channels
  ↓
82.1 Pilot Operations
  ↓
82.2 Human-in-the-Loop
  ↓
83 Image / Media Pipeline
  ↓
84 Control Center / Analytics Dashboard
  ↓
85 Scaling 10 → 25
  ↓
85.1 Channel Operations Automation
  ↓
86 Cost Control
  ↓
87 Scaling 25 → 50
  ↓
88 Security
  ↓
89 Deployment
  ↓
89.1 Backup / Recovery
  ↓
90 VK Adapter
  ↓
90.1 Multi-platform Variants
  ↓
91 Multi-platform Pilot
  ↓
92 Advanced Learning Loop
  ↓
92.1 Controlled Experiments
  ↓
93 A/B Testing
  ↓
94 Scaling 50 → 100+
  ↓
95 Production Hardening
  ↓
95.1 API / Compatibility
  ↓
95.2 Operational Runbooks
  ↓
96 Multi-user Productization
  ↓
96.1 Billing / Quotas
  ↓
96.2 Customer Onboarding
```

---

## Что делать прямо сейчас

### Ближайший порядок действий

1. ✓ Провести Verification Gate для Sprint 75.1–76.2
2. ✓ Подтвердить, что `SmartSourceSelector` реально используется в ResearchJob
3. ✓ Проверить Profile → Research → Source Selection behavior
4. ✓ Проверить Profile → Writing → Evaluation behavior
5. ✓ Подтвердить cross-channel isolation
6. ✓ Разобраться со статусом двух Sprint 60 tests
7. → Завершить Sprint 76.3 (Subscribe.ru Discovery)
8. → Реализовать Source Registry persistence (76.4)
9. → Переходить к Learning Loop (77)
10. → **НЕ начинать Smart Scaling** до подтверждения корректности универсального pipeline

### Критерий перехода к следующему этапу

> **Сначала доказать, что система правильно работает с одним каналом и не смешивает данные между каналами. Затем доказать, что она стабильно работает с десятью реальными каналами. И только после этого масштабировать сеть.**

### Что НЕ делать сейчас

- ❌ Запускать сразу 100–300 каналов
- ❌ Делать все платформы одновременно
- ❌ Начинать billing и multi-tenant
- ❌ Покупать дорогую GPU-инфраструктуру без измерений
- ❌ Делать полноценный ML/fine-tuning
- ❌ Усложнять semantic diversity до доказательства базовой версии
- ❌ Добавлять новые фичи без integration tests
- ❌ Считать unit tests доказательством production readiness

---

## Стратегический вывод

Проект уже находится **не на стадии «сделать Telegram-бота»**. Базовая система автоматизации существует.

**Следующая задача — превратить набор работающих модулей в управляемую, изолированную, наблюдаемую и масштабируемую платформу.**

Главная последовательность:

> **Универсальный pipeline → изоляция каналов → стабильность 10 каналов → автоматизация управления → масштабирование до 100+**

Это позволит получить систему, которая надёжно масштабируется, а не требует постоянного ручного контроля и постепенно теряет качество.

---

**Версия документа:** 1.0  
**Последний обновление:** 2026-09-11  
**Статус:** Основной стратегический документ
