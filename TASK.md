# AI Media Factory — Current Tasks

**Last Updated:** 2026-09-09
**Current Sprint:** 74.5 — Reliability Dashboard + Alerting (completed)
**Next Sprint:** Sprint 75+ — Discovery Engine

---

## Current Focus

### ✅ Sprint 74.1: Reliability — Retry Logic + Dead-Letter Queue (COMPLETED, 2026-09-09)
- [x] `backend/core/reliability.py`: `with_retry()` / `@retry_async`, exponential backoff + jitter, per-platform политики (telegram/vk/external_api)
- [x] Retry только для TRANSIENT/NETWORK; PERMANENT/CONFIGURATION — fail fast; Retry-After (429) учитывается
- [x] `VKError` (error_code → ErrorType): flood/rate limit → retry, auth/params → fail fast
- [x] Интеграция в `telegram_publisher.py` и `vk_publisher.py`
- [x] `backend/core/dead_letter.py`: DLQ на `pipeline_failures` (enqueue/list/requeue/due_for_retry/stats)
- [x] API `/api/v1/reliability/*` (dead-letters CRUD + stats + circuit-breakers), роутер подключён
- [x] Тесты `tests/test_reliability.py`: 18 passed; imports backend.main OK

---

## Next Sprint

### ✅ Sprint 74.2: Circuit Breaker + Rate Limit Integration (COMPLETED, 2026-09-09)
**Goal:** Предотвращение каскадных сбоев — circuit breaker вокруг Telegram/VK API + интеграция rate limiter с retry-политиками

**Architecture Decision:** Один unified CircuitBreaker (CLOSED/OPEN/HALF_OPEN) в `backend/core/reliability.py`, единый реестр `CircuitBreakerRegistry` / `get_breaker()` — один источник истины. Publisher + Self-Healing используют один registry.

**Tasks:**
- [x] Circuit Breaker (closed/open/half-open) per-platform в `backend/core/reliability.py`
- [x] Автоматическое отключение канала при CONFIGURATION-ошибках (alert_disable) через error_logger
- [x] Self-healing worker: периодический `due_for_retry()` → повторная публикация из DLQ
- [x] Rate limiter ↔ retry: при 429 пауза на весь канал (не только запрос)
- [x] DLQ-виджет в dashboard (frontend)
- [x] Валидация: полный regression 22/22 passed, без зависаний и таймаутов (исправлен тест test_429_pauses_whole_channel через injected `sleep=fake_sleep`)

**Architecture Details:**
- ✅ `backend/core/reliability.py`: CircuitBreaker (CLOSED/OPEN/HALF_OPEN), регистр `get_breaker(platform)`, компаньон-прокси — один источник истины
- ✅ `telegram_publisher.py`, `vk_publisher.py`, `self_healing.py` — через `get_breaker(platform)` (один registry)
- ✅ Self-Healing: `SelfHealingWorker` читает `due_for_retry()` из DLQ, переотправляет content payload, уважает circuit breaker (OPEN → skip) и channel pause (skip). Лимит 5 попыток, backoff 15 мин
- ✅ Self-Healing в фоне при старте backend (`backend/main.py` lifespan), API `POST /api/v1/reliability/self-healing/run`, `GET /api/v1/reliability/self-healing/status`
- ✅ API `/api/v1/circuit-breakers`: unified breaker (primary source), `rate_limit_stats` (auxiliary diagnostics, не breaker state), `channel_pauses`
- ✅ `backend/core/rate_limiter.py`: compatibility proxy → `get_breaker(platform)` (без самостоятельного decision-making breaker)
- ✅ `/rate-limits` endpoint **не создаём** (оставляем за ненадобностью)

**Success Criteria:**
- [x] Circuit breaker открывается после N подряд TRANSIENT-файлов и не долбит API
- [x] Посты из DLQ переотправляются автоматически (self-healing) или вручную через API
- [x] 0 каскадных флуд-блокировок при прогоне всех каналов

---

### ✅ Sprint 74.3: Channel Pause (COMPLETED, 2026-09-09)
**Goal:** При 429 канал ставится на паузу; Automation Manager + Scheduler не запускают дорогой pipeline (Research → LLM → Evaluation) для канала на паузе

**Tasks:**
- [x] `channel_pause_key(channel)` / `channel_paused_for(channel)` в `reliability.py` — UUID канала → ключ паузы (`chat_id`/`vk_group_id`)
- [x] `automation_manager_v2._execute_task_internal`: скип канала на паузе до запуска пайплайна
- [x] `scheduler.run_channel_automation`: ранний exit `skipped: channel_paused`
- [x] Тесты `tests/test_reliability_74_3.py`: 12/12 passed

**Success Criteria:**
- [x] Канал на паузе (429) не запускает Research → LLM → Evaluation
- [x] После истечения паузы канал снова обрабатывается
- [x] Circuit breaker и pause согласованы (оба через reliability)

---

### ✅ Sprint 74.4: DLQ / Health Checks (COMPLETED, 2026-09-09)
**Goal:** Автоматическая запись в DLQ при исчерпании retry + health checks API + ручное управление паузой

**Tasks:**
- [x] `backend/core/health.py` — `check_telegram`, `check_vk`, `check_all` с латентностью
- [x] `GET /api/v1/reliability/health` endpoint
- [x] DLQ auto-enqueue в `telegram_publisher.py` (`_enqueue_dlq`) и `vk_publisher.py` (`_enqueue_dlq_vk`)
- [x] Manual pause API: `POST .../pause`, `POST .../resume`, `GET .../pause`
- [x] `reset_channel_pauses(channel_id=None)` — снятие паузы одного канала
- [x] Тесты `tests/test_reliability_74_4.py`: 12/12 passed

**Success Criteria:**
- [x] При исчерпании retry контент автоматически попадает в DLQ (self-healing)
- [x] Health check endpoint возвращает статус + латентность для telegram/vk
- [x] Оператор может вручную поставить/снять паузу с канала через API

---

### ✅ Sprint 74.5: Reliability Dashboard + Alerting (COMPLETED, 2026-09-09)
**Goal:** Расширить frontend-виджет + добавить Telegram-алерты при критических событиях

**Tasks:**
- [x] `ReliabilityWidget.tsx` — Health Check button, detailed pause list, DLQ by_channel
- [x] `backend/core/alerts.py` — `send_alert()` + 3 event types (breaker opened, channel disabled, DLQ exhausted)
- [x] Wired into `CircuitBreaker._open()`, `_alert_disable_channel()`, `SelfHealingWorker._process_one()`
- [x] Env config: `ALERT_ENABLED`, `ALERT_TELEGRAM_BOT_TOKEN`, `ALERT_TELEGRAM_CHAT_ID`

**Success Criteria:**
- [x] Оператор видит состояние API (health check) в dashboard
- [x] Критические события приходят в Telegram (opt-in)
- [x] 64 reliability tests pass без warnings

---

## Short-term Backlog

### Follow-ups (из 73.3)
- [ ] Единый `execution_id`: ChannelTask.execution_id (uuid) vs pipeline execution_id — пробросить task id в pipeline вместо генерации второго
- [ ] Инструментация остальных Ollama call-sites (evaluator, image_prompt, formatters, jobs) — сейчас метрики покрывают только production writing path
- [ ] LLM-метрики в summary-агрегатах `/metrics/pipeline/summary/all`


---

## Long-term Backlog

### Sprint 75+: Discovery Engine
- [ ] Subscribe.ru integration (discovery only)
- [ ] RSS feed validation
- [ ] Source scoring algorithm
- [ ] Automatic source recommendations

### Sprint 76+: Learning Loop
- [ ] Analytics collection (engagement, CTR)
- [ ] A/B testing framework
- [ ] Performance correlation analysis
- [ ] Automatic strategy optimization

### Sprint 77+: Smart Scaling
- [ ] Gradual scaling (10 → 25 → 50 → 100)
- [ ] Distributed architecture (worker pools, Redis queues)
- [ ] Load balancing
- [ ] Resource quotas

---

## Technical Debt

### High Priority
- [ ] **GenericPublishingStrategy migration** — currently not using Publication Layer
- [ ] **Observability gap** — no metrics or monitoring

### Medium Priority
- [ ] **Legacy engines/research/engine.py** — unused, should be removed
- [ ] **Old channel.sources field** — use content_profile["sources"] instead
- [ ] **Synchronous VK publishing** — should be async for better performance
- [ ] **Scheduler get_next_run() complexity** — needs refactoring

### Low Priority
- [ ] **Image generation** — currently using placeholders
- [ ] **Video support** — not implemented
- [ ] **Multi-language support** — currently Russian only
- [ ] **Advanced deduplication** — semantic similarity

---

## Known Issues

### Resolved
- ✅ DetachedInstanceError in NewsPublishingStrategy (Sprint 72.4)
- ✅ VK post status not updating (Sprint 71)
- ✅ Telegram 401 Unauthorized for 3 channels (Sprint 70)
- ✅ Pydantic ValidationError for ChannelScheduleResponse (Sprint 70.5)

### Open
- ⚠️ GenericPublishingStrategy not using Publication Layer
- ⚠️ No metrics or observability
- ⚠️ Pipeline reports "0 published" even when posts succeed (cosmetic)

---

## Ideas / Future Work

- **Content scheduling optimization** — learn best posting times per channel
- **Audience segmentation** — different content for different audience segments
- **Cross-platform syndication** — publish same content to multiple platforms
- **Content series** — multi-part stories across multiple posts
- **User-generated content** — accept submissions from users
- **Collaboration features** — multiple editors per channel
- **Content templates** — reusable templates for common post types
- **Advanced media** — GIFs, carousels, stories

---

## Notes

### Architecture Decisions
- **Publication Layer:** Separate contract from rendering (Sprint 72)
- **Archetype-based defaults:** Profile > archetype > global defaults
- **Platform renderers:** Telegram and VK have different rendering logic
- **Database updates:** Immediate after successful publication

### Testing Strategy
- Manual testing for each sprint
- Regression testing before major releases
- Real-world testing on actual channels
- Automated testing (future, Sprint 73+)

### Documentation
- Update STATUS.md after each sprint
- Update ROADMAP.md after each phase
- Update ARCHITECTURE.md for architectural changes
- Update AI_CONTEXT.md for AI-assisted development rules
