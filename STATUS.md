# AI Media Factory — Status

**Last Updated:** 2026-09-11 (Sprint 76.2 Smart Source Selection completed)
**Current Sprint:** 76.2 (completed)
**Next Sprint:** 76.3 — Source Discovery (Subscribe.ru discovery-интеграция) [Discovery Engine Phase 10]

> ⚠️ **Нумерационная заметка:** ROADMAP.md резервировал «Sprint 75» под Фазу 10 «Discovery Engine»
> (75.1 Source Discovery / 75.2 Smart Source Selection). Эти номера были заняты фактически
> реализованной серией **«Sprint 75.x — Channel Profile как runtime config source»**
> (75.1 профиль→поведение, 75.2 A/B-тесты, 75.3 изоляция каналов). Discovery Engine при этом
> сдвинут на будущее (Sprint 76+); ROADMAP синхронизирован (09.09).

---

## Current State

### Sprint 76.2 — Smart Source Selection (completed, 2026-09-11)
- ✅ `engines/source_selection.py` — `SmartSourceSelector` компонует скоринг (76.1) с: качеством (`QualityRegistry`: acc/fail → adjustment после ≥3 попыток, target rate 0.7, clamp −10..+8), ротацией (`selection_count` → penalty 3/использование), diversity (штраф за редундантный coverage-caps+language), topic-based matching (встроен в base score).
- ✅ Поправлен `CAPABILITY_RELEVANCE` (anime `episodes/covers/descriptions/genres`, news `articles/summaries/covers`) — скор теперь соответствует реальным capability источников.
- ✅ API (`sources.py`): `GET /sources/discover/select`, `POST /sources/metrics`, `POST /sources/select/record-pick`. Заметка: `GET /discover/select` (двухсегментный) — т.к. `GET /sources/{source_id}` перехватывал бы односегментный `/select`.
- ✅ Тесты: `tests/test_source_selection.py` — **13 passed** (registry, порядок, diversity ru+en, rotation-альтернация, quality-падение ненадёжного, API). Discovery+Selection вместе **29 passed**.
- ✅ Полный регресс: **194 passed, 2 skipped, 0 failed** (181 + 13 Selection).
- ℹ️ QualityRegistry — in-memory (runtime); персистентность в БД — отдельный шаг.
- ⏭️ Осталось (Sprint 76.3): Subscribe.ru discovery-интеграция.

### Sprint 76.1 — Source Discovery (completed, 2026-09-11)
- ✅ `engines/source_scoring.py` — детерминированный скоринг источников (0..100): content_type 40, topic 20, language 10, capabilities 20 (по CAPABILITY_RELEVANCE), rate_limit headroom 10, penalty −15 за requires_api_key. `SourceDiscoveryEngine.recommend(content_type, topic, language, top_k)` — ранжированные рекомендации.
- ✅ `engines/source_validation.py` — RSS/Atom валидация: `validate_feed(url, fetch=None)` (fetch инжектируется для тестов, default httpx). Детект rss/atom/html, title, item_count, graceful error на сетевых сбоях.
- ✅ API (`backend/app/api/v1/sources.py`): `GET /sources/discover/recommend?content_type=&topic=&language=&top_k=` и `POST /sources/discover/validate` `{urls:[...]}`.
- ✅ Тесты: `tests/test_source_discovery.py` — **16 passed** (скоринг, рекомендации, RSS/Atom/HTML/network-fail, httpx default, оба эндпоинта без реальной сети).
- ✅ Полный регресс: **181 passed, 2 skipped, 0 failed** (165 + 16 Discovery).
- ⏭️ Осталось (Sprint 76.2): Subscribe.ru discovery-интеграция, topic-based matching, quality metrics, diversity, source rotation.

### Sprint 75.4 — Sprint 60 flake fix + regression green (completed, 2026-09-11)
- ✅ Закрыты 2 известных pre-existing Sprint 60 фейла (`test_generate_news_post`, `test_generate_manga_post_no_video`): это были integration-тесты, требующие живого Ollama (`host.docker.internal:11434`, 503 при его отсутствии). Навешен маркер `requires_llm` (= `skipif(APP_ENV=="test")`, Sprint 66.4), который был создан для таких тестов, но на эти два пропущен.
- ✅ Полный регресс: **165 passed, 2 skipped, 0 failed** (2 скипа — LLM-dependent integration; при наличии Ollama и non-test APP_ENV выполняются реально).

### Sprint 75.3 — Cross-channel isolation fix (completed, 2026-09-11)
- ✅ **Production-баг (из Sprint 75.2 finding) исправлен:** `WritingJob`, `EvaluatorJob`, `ImageJob`, `PublishJob`, `RevisionJob`, `ReEvaluationJob` получали items ВСЕХ каналов (`repo.list_all(status=...)` без фильтра), из-за чего прогон канала A генерировал/оценивал/публиковал драфты канала B со стилем профиля A (и публиковал чужие approved с credentials канала A).
- ✅ Фикс: во все `list_all(...)` добавлен `channel_id=getattr(channel, "id", None) if channel else None` — `ContentRepository.list_all` уже поддерживал фильтр, jobs просто не передавали его.
- ✅ Тесты: `tests/test_profile_ab_behavior.py` A/B-тесты переписаны с проверкой изоляции (прогон канала обрабатывает только СВОИ items); итого профильные тесты **14 passed**.
- ✅ Полный регресс: **165 passed, 2 failed** (only известные Sprint 60: `test_generate_news_post`, `test_generate_manga_post_no_video`).

### Sprint 75.2 — Channel Profile A/B behavior tests (completed, 2026-09-11)
- ✅ `tests/test_profile_ab_behavior.py` — 5 тестов: два профиля (Analytical Deep Dive 2500/analytical vs Casual Manga Buzz 800/casual) → разное поведение в Research (sources/freshness), Writing (tone/length/style), Evaluation (target_style); инвариант детерминизма.
- ✅ Найден и задокументирован cross-channel production-баг (см. 75.3).

### Sprint 75.1 / 75.1.x — Channel Profile as runtime config source (completed, 2026-09-11)
- ✅ `backend/automation/profile_config.py::load_profile_config` — единый runtime-контракт: Priority 1 = ChannelProfileORM (source=profile) > content_profile > legacy fallback; стиль-aware `target_style` для LLM-as-a-Judge.
- ✅ Research/Writing/Evaluator jobs завязаны на `load_profile_config` (профильные источники, style_profile, target_style).
- ✅ Миграция `migrations/003_recreate_channel_profiles.py` (идемпотентная, idempotent data-protection; применена на реальной БД).
- ✅ Тесты: `tests/test_profile_config.py` — 9 passed (isolated_db + sync-фиксы).

### Sprint 74.5 — Reliability Dashboard + Alerting (completed, 2026-09-09)
- ✅ `backend/core/reliability.py`: async retry-движок — `with_retry()` / `@retry_async`, exponential backoff с jitter, per-platform политики (`telegram` 4 attempts, `vk` 4 attempts, `external_api` 3), retry только для TRANSIENT/NETWORK (fail fast для PERMANENT/CONFIGURATION), поддержка Retry-After (429)
- ✅ `VKError` с map error_code → ErrorType (1/6/9/10/29 → transient; 5/7/17 → configuration; 15/100/200 → permanent)
- ✅ Интеграция: `telegram_publisher.py` (send_message/send_photo через `_post` + retry) и `vk_publisher.py` (wall.post с retry)
- ✅ `backend/core/dead_letter.py`: DLQ поверх `pipeline_failures` — enqueue/list/requeue/due_for_retry/mark_resolved/stats (SQLite-совместимая фильтрация по `context.dlq`)
- ✅ API `/api/v1/reliability/*`: GET dead-letters, GET dead-letters/stats, POST dead-letters/{id}/requeue, POST dead-letters/{id}/resolve, GET circuit-breakers
- ✅ Тесты: `tests/test_reliability.py` — 18 passed (политики, классификация VK, retry-поведение, DLQ на in-memory SQLite)
### Sprint 74.2 — Reliability: Unified Circuit Breaker + Rate Limit Integration (completed, 2026-09-09)
- ✅ Архитектурное решение: **один unified CircuitBreaker** (CLOSED/OPEN/HALF_OPEN) в `backend/core/reliability.py`, единый реестр `CircuitBreakerRegistry` / `get_breaker()` — один источник истины
- ✅ Publisher + Self-Healing используют один registry: `telegram_publisher.py`, `vk_publisher.py`, `self_healing.py` — все через `get_breaker(platform)`
- ✅ CircuitBreaker: ПОДРЯДНЫХ TRANSIENT/NETWORK failures → OPEN; после recovery_timeout → HALF_OPEN (probe); успех → CLOSED, провал → OPEN. threshold=5 (telegram/vk), half_open_max_calls=1
- ✅ AUTOMATIC DISABLE: при CONFIGURATION-ошибке (401/403/... → не retry) — `alert_disable_channel()` ставит `ChannelORM.is_active=False`, планировщик больше не запускает канал, ошибка пишется в pipeline_failures
- ✅ Channel-wide pause: `ChannelPausedError`, `pause_channel(channel_id, seconds)`, `channel_paused(channel_id)` — при Retry-After (429) пауза НА ВЕСЬ КАНАЛ, а не только на запрос. Publisher + Self-Healing получают `ChannelPausedError` и не делают запрос
- ✅ Self-Healing: `backend/core/self_healing.py` — `SelfHealingWorker` читает `due_for_retry()` из DLQ, переотправляет content payload без регенерации, уважает circuit breaker (OPEN → skip) и channel pause (skip). Лимит 5 попыток, backoff 15 мин
- ✅ Self-Healing запускается в фоне при старте backend (`backend/main.py` lifespan), API для ручного запуска и статуса: `POST /api/v1/reliability/self-healing/run`, `GET /api/v1/reliability/self-healing/status`
- ✅ API `/api/v1/circuit-breakers`: unified breaker из reliability.py — primary source; `rate_limit_stats` (auxiliary diagnostics из rate_limiter.py, не breaker state); `channel_pauses`
- ✅ Compatibility proxy: `backend/core/rate_limiter.py` больше не содержит самостоятельный decision-making breaker — delegates на `get_breaker(platform)` из reliability.py (record_success/failure/get_stats)
- ✅ `/rate-limits` endpoint **не создаём** (оставляем за ненадобностью на текущем этапе)
- ✅ Frontend: DLQ-виджет ReliabilityWidget (`frontend/src/components/ReliabilityWidget.tsx`), монтируется в Dashboard.tsx, подгружает `/api/v1/reliability/circuit-breakers` + `/api/v1/reliability/dead-letters/stats` + `/api/v1/reliability/self-healing/status`, кнопка "Запустить Self-Healing"
- ✅ Тесты: `tests/test_reliability_74_2.py` — **22/22 passed** (circuit breaker unit, with_retry integration, channel pause, alert-disable, self-healing), без зависаний и таймаутов (исправлен тест test_429_pauses_whole_channel через injected `sleep=fake_sleep`)
- ⚠️ Next: Sprint 74.3 — Channel Pause (channel-wide pause on 429 + self-healing integration + frontend status)

### Sprint 74.3 — Reliability: Channel Pause production integration (completed, 2026-09-09)
- ✅ **Production-пробел закрыт**: при 429 publisher ставит паузу; Automation Manager и Scheduler теперь НЕ запускают дорогой pipeline (Research → LLM → Evaluation) для канала на паузе
- ✅ `channel_pause_key(channel)` — UUID канала → ключ паузы (`chat_id` для Telegram, нормализованный `-vk_group_id` для VK)
- ✅ `channel_paused_for(channel)` — сколько секунд канал ещё на паузе (принимает ChannelORM, сопоставляет с паузой publisher'а)
- ✅ `automation_manager_v2._execute_task_internal`: проверка `channel_paused_for(channel)` ДО запуска пайплайна → скип (task FAILED с "Channel paused (429)")
- ✅ `scheduler.run_channel_automation`: ранний exit `{"status":"skipped","reason":"channel_paused","remaining_seconds":N}` до вызова runner
- ✅ Тесты: `tests/test_reliability_74_3.py` — **12/12 passed** (сопоставление ключей telegram/vk, детект по chat_id/vk_group_id, истечение, изоляция каналов)
- ✅ Полный reliability-регресс: **52 passed** (74.1: 18 + 74.2: 22 + 74.3: 12) за 1.92s, без зависаний и таймаутов

### Sprint 74.4 — Reliability: DLQ auto-enqueue + Health Checks + Manual Pause API (completed, 2026-09-09)
- ✅ **Health Checks:** `backend/core/health.py` — `check_telegram(bot_token)`, `check_vk(access_token, group_id)`, `check_all(platforms)` с латентностью; endpoint `GET /api/v1/reliability/health?platforms={...}`
- ✅ **DLQ auto-enqueue:** при исчерпании retry publisher'ы автоматически записывают контент в DLQ через `_enqueue_dlq()` (telegram) / `_enqueue_dlq_vk()` (vk) — self-healing может переотправить без регенерации
- ✅ **Manual Pause API:** `POST /api/v1/reliability/channels/{id}/pause?seconds=N`, `POST .../resume`, `GET .../pause` — ручное управление паузой канала
- ✅ `reset_channel_pauses(channel_id=None)` — поддержка снятия паузы одного канала (resume endpoint)
- ✅ Тесты: `tests/test_reliability_74_4.py` — **12/12 passed** (health checks telegram/vk, manual pause API, DLQ auto-enqueue, channel pause for key)
- ✅ Полный reliability-регресс: **64 passed** (74.1: 18 + 74.2: 22 + 74.3: 12 + 74.4: 12) за 3.38s, без зависаний и таймаутов

### Sprint 74.5 — Reliability: Dashboard + Alerting (completed, 2026-09-09)
- ✅ **Frontend widget expansion:** `ReliabilityWidget.tsx` — Health Check button, detailed pause list (channel ID + remaining time), DLQ by_channel breakdown, conditional coloring
- ✅ **Telegram Alerts:** `backend/core/alerts.py` — `send_alert()` + 3 event types:
  - `alert_breaker_opened` — circuit breaker OPEN (platform, failures, last error)
  - `alert_channel_disabled` — auto-disable при CONFIGURATION error
  - `alert_dlq_exhausted` — self-healing исчерпал попытки
- ✅ **Wired into production paths:** `CircuitBreaker._open()`, `_alert_disable_channel()`, `SelfHealingWorker._process_one()` — fire-and-forget через daemon thread
- ✅ **Конфигурация через env:** `ALERT_ENABLED`, `ALERT_TELEGRAM_BOT_TOKEN`, `ALERT_TELEGRAM_CHAT_ID` (opt-in, по умолчанию disabled)
- ✅ Полный reliability-регресс: **64 passed** за 3.75s, без warnings (coroutine устранён переходом на threading)

---

### Automation/Scheduler tail — CLOSED (Sprint 72.6)
- ✅ Fixed `revision_job.py` IndentationError (backend crash loop)
- ✅ Fixed DetachedInstanceError in NewsPublishingStrategy reporting (published counter now correct)
- ✅ Task timeout raised 600s → 1800s; global concurrency limit = 3 tasks (semaphore)
- ✅ Full regression on all 14 channels via `/api/v1/automation-v2/run-all-channels`: **~130 posts published, 0 DetachedInstance errors**
- ⚠️ ~10 min per channel (10 topics × LLM) — see Sprint 73 for metrics
- ⚠️ Known degradations: VK_TOKEN not set (1 channel), AniList 403 / ReadManga 402 (sources)

### Sprint 73.1 — Timing Instrumentation (completed)
- ✅ `PipelineResult.stage_timings` + лог с процентами по стадиям (research/writing/media/publishing)
- ✅ Таблица `pipeline_run_metrics` (ORM: `core/models/pipeline_run_metrics_orm.py`), метрики пишутся после каждого прогона
- ✅ API: `GET /api/v1/metrics/pipeline/{channel_id}`, `/summary/all`, `/slowest/top`

### Sprint 73.2 — Multi-channel Baseline (completed, 2026-09-08)
- ✅ Прогон всех 14 каналов через `run-all-channels` (семафор 3), метрики в `pipeline_run_metrics`
- **Network baseline (10 продуктивных прогонов):** 62 поста опубликовано, 0 errors; Avg=486.7s, **P50=507.6s, P95=779.6s**
- **Writing share = 97.5%** (research 0.9%, publishing 1.7%), LLM ≈ 74–81s на пост
- Top каналы по времени: Gaming 829s/10 постов, Movie 719s/9, Манга 620s/8
- Без постов (дедупликация отсекла все темы): Новости 📰, Science Facts, Manga Releases Tracker; VK-канал — нет VK_TOKEN
- **Вывод:** Writing = 92–98% на всех каналах → гипотеза подтверждена, Writing Optimization Sprint обоснован (параллельная генерация / model routing)
- Next: Sprint 73.3 (execution_id сквозная трассировка + LLM-метрики) → 73.4 Dashboard

### Sprint 73.3 — Metrics Quality (completed, 2026-09-09)
- ✅ Сквозной `execution_id`: генерируется в `UniversalContentPipeline.run()` (формат `YYYYMMDD-HHMMSS-<channel8>`, совместим с execution_logs), пишется в `pipeline_run_metrics`
- ✅ LLM-метрики: `core/metrics/llm_metrics.py` — `LLMMetricsCollector` через ContextVar (изоляция между параллельными каналами); инструментированы оба вызова Ollama в `llm_post_generator.py` (`prompt_eval_count`/`eval_count` → tokens_in/out, wall-time latency)
- ✅ ORM/БД: колонки `llm_calls`, `llm_errors`, `llm_latency_ms`, `tokens_in`, `tokens_out`, `llm_model` в `pipeline_run_metrics` (миграция `migrations/002_add_llm_metrics.py`, применена к прод-Postgres)
- ✅ API: `GET /metrics/pipeline/*` отдаёт блок `llm` по каждому прогону
- ✅ Тесты: `tests/test_llm_metrics.py` — 5 passed (накопление, ошибки, изоляция контекстов)
- Назначение: данные для выбора Strategy A/B/C в Writing Optimization Sprint (A: параллельность — проверка деградации стоимости поста; B: model routing)

- 📊 Первый вывод: **~92% времени пайплайна — LLM-генерация (writing)**, research ~3%, publishing ~4%

### Sprint 73.4 — Dashboard + Alerts (completed, 2026-09-09)
- ✅ Backend API (backend/app/api/v1/pipeline_metrics.py): `GET /metrics/pipeline/health/overview` (success rate, P50/P95, LLM-агрегаты, статус healthy/warning/critical), `GET /metrics/pipeline/alerts` (run_failure, timeout, llm_degradation, stale_channel), `GET /metrics/pipeline/trends` (hourly buckets); односегментные маршруты объявлены до /{channel_id}
- ✅ Follow-up из 73.3: `/metrics/pipeline/summary/all` теперь агрегирует LLM-метрики (llm_calls/errors/latency/tokens)
- ✅ Frontend: `frontend/src/pages/PipelineDashboard.tsx` — KPI-карточки, health-таблица каналов, панель алертов, график трендов (recharts), история прогонов по execution_id, авто-обновление 15s; маршрут добавлен в App.tsx/Layout.tsx
- ✅ API-клиент: `pipelineMetricsAPI` (frontend/src/api/client.ts)
- ✅ Тесты: `tests/test_pipeline_metrics_api.py` (health/alerts/trends/route-ordering) — 19 passed вместе с test_llm_metrics.py; `tsc -b` exit 0
- ⏭️ Осталось: валидационный прогон всех каналов (заполнение llm_* на проде), Prometheus/Grafana-экспорт опционально

- **14 active channels** across Telegram and VK platforms
- **8 archetypes**: news, educational, entertainment, viral, releases, reviews, community, aggregator
- **Universal Pipeline** end-to-end: Research → Decision → Writing → Evaluation → Media → Publication → Rendering → Publishing
- **Publication Contract** with archetype-based policies
- **Real LLM generation** via Ollama (Russian language)
- **Deduplication** working correctly
- **Publication duration**: 280-330 seconds per channel (10 topics × 30s LLM)

### Platform Support
- **Telegram**: 13 channels with bot tokens
- **VK**: 1 channel (AI Media Factory)

### Recent Test Results (Sprint 72.4)
- **Channel**: Новости 📰 (24df0f84-46c2-4df4-ab39-d76881b35438)
- **Posts published**: 6 posts
- **Status**: All posts marked as published in database
- **Telegram message IDs**: 504, 505, 506, 507, 508, 509
- **HTML source links**: <a href> tags present in all posts
- **Pipeline duration**: ~173 seconds

---

## Completed Sprints

### Sprint 67-68: Core Infrastructure
- ✅ Universal Pipeline architecture
- ✅ 8 archetypes with specialized strategies
- ✅ Channel Profile system
- ✅ Content deduplication

### Sprint 69: Pilot Infrastructure
- ✅ Telegram publishing integration
- ✅ Database persistence (status, telegram_message_id)
- ✅ Error handling and recovery
- ✅ Scheduler with cron jobs

### Sprint 70: Generic LLM Generation
- ✅ LLM-based text generation for all 8 archetypes
- ✅ Russian language output via Ollama
- ✅ Natural text formatting (no template headers)
- ✅ Source attribution handling

### Sprint 71: VK + Universal Publishing
- ✅ VK API integration (AI Media Factory channel)
- ✅ VK wall.post publishing
- ✅ Multi-platform support (Telegram + VK)
- ✅ Correct publication status tracking

### Sprint 72: Editorial / Publication Layer
- ✅ **72.1** Publication Contract (core/models/publication.py)
  - MediaAsset, FormattingOptions, Publication dataclasses
  - Platform-independent contract
- ✅ **72.2** PublicationBuilder (core/models/publication_builder.py)
  - Archetype-based defaults for 8 archetypes
  - Smart policy resolution (profile > archetype > defaults)
  - Source/article/media policies
- ✅ **72.3** Platform Renderers (core/models/renderers/)
  - TelegramRenderer: HTML source links, InlineKeyboardMarkup
  - VKRenderer: Plain text, URL attachments
  - Platform-specific rendering from Publication
- ✅ **72.4** NewsPublishingStrategy Integration
  - Builder + Renderer pipeline
  - DB updates after publication (status=published)
  - telegram_message_id persisted
  - Rendered Publication text sent to Telegram
  - Fixed: DetachedInstanceError, return value issues

---

## Architecture Overview
Channel Profile
↓
Research (RSS + Topic Extraction)
↓
Decision (Content Selection)
↓
Writing (LLM Generation)
↓
Evaluation (Quality Check)
↓
Media (Image/Video Selection)
↓
PublicationBuilder
↓
Publication Contract
↓
Platform Renderer (Telegram/VK)
↓
Publishing (API Call)
↓
Database Update (status, message_id)

### Key Principle
> **Publication describes what should be published. Renderer describes how it is represented on a platform.**

---

## Current Limitations

### Not Yet Implemented
- ❌ GenericPublishingStrategy not yet migrated to Publication Layer
- ❌ Other archetype strategies still use old text formatting
- ❌ No observability/metrics collection
- ❌ No retry logic for transient errors
- ❌ No health checks for Telegram/VK APIs

### Technical Debt
- Legacy engines/research/engine.py (unused)
- Old channel.sources field (use content_profile["sources"])
- Synchronous VK publishing (should be async)
- Scheduler get_next_run() complexity

---

## Next Steps

### Immediate (Sprint 72.5)
- Migrate GenericPublishingStrategy to Publication Layer
- Apply PublicationBuilder + Renderer to all archetypes
- Test all 14 channels with new Publication flow

### Short-term (Sprint 73-74)
- **73**: Observability — metrics, monitoring, alerting
- **74**: Reliability — retries, timeouts, health checks, dead-letter queue

### Long-term (Sprint 75+)
- Discovery Engine (Subscribe.ru integration)
- Learning Loop (analytics-driven content optimization)
- Smart Scaling (10 → 25 → 50 → 100 channels)

---

## File Structure
AI-MEDIA-FACTORY/
├── core/models/
│ ├── publication.py # Publication Contract
│ ├── publication_builder.py # PublicationBuilder
│ └── renderers/
│ ├── telegram_renderer.py # TelegramRenderer
│ └── vk_renderer.py # VKRenderer
├── backend/engines/
│ ├── news_strategies.py # NewsPublishingStrategy (integrated)
│ ├── generic_strategies.py # GenericPublishingStrategy (TODO)
│ ├── universal_pipeline.py # Universal Pipeline
│ ├── telegram_publisher.py # Telegram API client
│ └── vk_publisher.py # VK API client
├── backend/automation/
│ └── automation_manager_v2.py # Pipeline orchestration
└── docs/
├── STATUS.md # This file
├── ROADMAP.md # Development roadmap
├── ARCHITECTURE.md # System architecture
└── TASK.md # Current backlog

---

## Source of Truth

For current development context:
1. **STATUS.md** — project state (this file)
2. **PROJECT_CONTEXT.md** — architectural context
3. **ARCHITECTURE.md** — system design
4. **TASK.md** — current backlog
5. **AI_CONTEXT.md** — AI-assisted development rules