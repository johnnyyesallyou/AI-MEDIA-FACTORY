# AI Media Factory — Project Status

> Last updated: 2026-09-01
> Current Phase: **PHASE 3 — Smart Channel Creation**
> Current Phase: **OBSERVATION PERIOD (7-14 days)**

---

## 🎯 Current Focus

**Sprint 68.1: Theme Classification (LLM)**
- Create `.github/workflows/ci.yml`
- Ruff lint on every push
- Unit tests (without Docker/Ollama)
- CI tests on every push

**Next:** Sprint 66.6 (Async Tests Stabilization) → Sprint 66.7 (GitHub Actions CI)

---

## ✅ Completed Sprints

### Sprint 65 — Smart Channel Intelligence ✅ CLOSED

| Step | Status | Result |
|------|--------|--------|
| 65.1 Foundation | ✅ | ChannelIntent/Strategy/Capability + 11 domains + TopicClassifier |
| 65.2 Wizard API | ✅ | `/wizard/suggest` for any topic (no more 400 errors) |
| 65.3 Profiles Registry | ✅ | 7 new profiles (technology/ai/automotive/science/gaming/business/general) |
| 65.4 StrategyPreview + Persist | ✅ | UI for editing strategy + publishing_mode/frequency persist end-to-end |
| 65.5 Publishing Mode Selector | ✅ | Inline edit in Channels page (auto/approval_required/manual) |

**E2E verified:** Create channel → edit strategy → persist → GET returns correct publishing_mode/frequency

---

### Sprint 66 — Production Hardening (IN PROGRESS)

| Step | Status | Result |
|------|--------|--------|
| 66.1 Connection Pool | ✅ | Pool size 5→20, max_overflow 10→30, timeout 30→60, pool_pre_ping |
| 66.2 Pool Monitoring | ✅ | `GET /api/health/db-pool` + Prometheus gauges (db_pool_size/checkedout/overflow) |
| 66.3 Task Timeout | ✅ | `TASK_TIMEOUT=300s` + `asyncio.wait_for` wrapper (prevents worker hangs) |
| 66.4 Structured Logging | ✅ | JSON logs (logs/app.log, debug.log, errors.log) + StructuredFormatter |
| 66.4 PortableJSONB | ✅ | SQLite + PostgreSQL support (12 models migrated) |
| 66.4 Pydantic V2 | ✅ | `ConfigDict` migration (0 deprecation warnings) |
| 66.4 Test Infrastructure | ✅ | pytest-asyncio + event loop fixtures + conftest.py |
| 66.5 Pipeline Failures | ✅ | pipeline_failures table + ErrorLogger + /failures API (8 endpoints) + worker integration |
| 66.6 Async Tests | ✅ | 63/63 unit passed (1.67s), pytest-asyncio auto mode, integration markers |
| 66.7 GitHub Actions CI | ✅ | .github/workflows/ci.yml + requirements-test.txt |

---

### Sprint 67 — Channel Scaling Architecture ✅ CLOSED

| Step | Status | Result |
|------|--------|--------|
| 67.1 Channel Archetypes | ✅ | 8 archetypes (news/releases/educational/viral/reviews/community/aggregator) + ArchetypeDefaults |
| 67.2 Channel Profile ORM | ✅ | ChannelProfileORM (12 fields) + Pydantic V2 + CRUD + assign endpoint |
| 67.3 Universal Pipeline | ✅ | UniversalContentPipeline (research→generation→media→publish) + Protocol strategies |
| 67.4 Strategy Registry | ✅ | 8 archetypes registered (NEWS specialized + 7 generic) |
| 67.5 Channel Templates | ✅ | 6 YAML templates + from-template + assign (E2E: Gaming News from news template) |

**Note:** Performance framework created but not yet integrated into production engines. Real LLM generation happens in `automation/jobs/`, not `backend/engines/`.

---

## 🧪 Test Results

### Unit Tests
✅ 63/63 passed (APP_ENV=test, SQLite)
✅ 39/39 CI tests passed (tests/ci/)
⏭️ 7 skipped (@pytest.mark.integration)
⏭️ 2 skipped (requires Ollama LLM)

### Integration Tests (require Docker + Ollama)
⏭️ automation_manager (async event loop)
⏭️ post_generation_service (LLM calls)

**Total:** 102 tests green, 0 failures in CI mode

---

## 🏗 Architecture Status

### Production Components
- ✅ FastAPI backend (Uvicorn)
- ✅ PostgreSQL (primary DB)
- ✅ Redis (queue/cache)
- ✅ Qdrant (vector DB)
- ✅ MinIO (object storage)
- ✅ Nginx (reverse proxy)
- ✅ Prometheus + Grafana (monitoring)
- ✅ Open WebUI (LLM interface)

### Performance Infrastructure (Created, Not Fully Integrated)
- ✅ LLM Profiler (decorator ready)
- ✅ Cache Layer (Memory + Redis backends)
- ✅ Rate Limiter (sliding window + circuit breaker)
- ✅ Connection Pool (optimized)
- ✅ Structured Logging (JSON)

### Missing for Scale
- ❌ Universal Pipeline (Sprint 67.3)
- ❌ Channel Profiles/Archetypes (Sprint 67.1-67.2)
- ❌ Strategy Registry (Sprint 67.4)
- ❌ Network Dashboard (Sprint 71)
- ❌ Cross-Channel Intelligence (Sprint 72)

---

## 📊 Key Metrics

| Metric | Current | Target (Sprint 69) |
|--------|---------|-------------------|
| Channels | 16 (test) | 10 (pilot) |
| Test Coverage | 102/102 passed | 150+ tests |
| API Latency (p95) | ~200ms | <100ms |
| LLM Generation | ~300s | <45s (with cache) |
| Publish Success Rate | ~95% | >99% |
| Error Tracking | Docker logs | Pipeline failures table |

---

## 🚧 Known Issues

1. **Async tests hang** in CI (automation_manager, worker lifecycle) — need event loop fix
2. **Performance components not integrated** — LLMProfiler/CacheLayer exist but not used in real engines
3. **No error tracking** — pipeline failures only visible in Docker logs (Sprint 66.5 will fix)
4. **Manual scaling** — each new topic requires manual pipeline configuration (Sprint 67 will fix)

---

## 📅 Recent Commits (Last 10)
d2b5e95 Sprint 66.4 final: mark LLM-dependent tests as @pytest.mark.integration
f5aee4a Sprint 66.1-66.2: Connection pool hardening + monitoring
74e3450 fix(sprint-65.4): persist wizard publishing settings and fix StrategyPreview create flow

---


## 🔍 OBSERVATION PERIOD (7-14 days)

**Статус:** Активное наблюдение за пилотом (начало: 2026-09-02)

**Что делаем:**
- Наблюдаем 14 каналов (13 Telegram + 1 VK)
- Собираем метрики по каждому каналу
- НЕ меняем архитектуру, pipeline, prompts
- Исправляем только критические баги

**Критерии успеха:**
- Publish success rate > 95%
- Approval rate > 70% (для approval_required каналов)
- Pipeline failures < 5%
- Нет критических ошибок в логах

**Что собираем:**
- Количество generated/published/failed/rejected постов
- Conversion rate: sources → topics → posts
- LLM quality (фактические ошибки, галлюцинации, стиль)
- Source quality (какие RSS дают 0 topics)
- Telegram API errors

**Следующий шаг:** Sprint 70 — Pilot Analysis (Go/Fix/Stop decision)

## 🎯 Next Steps

1. **OBSERVATION (7-14 дней)** — собираем метрики, не меняем систему
2. **Sprint 70.1** — Pilot Analysis: метрики по каждому каналу
3. **Sprint 70.2** — Source Quality Analysis: conversion funnels
4. **Sprint 70.3** — LLM Quality Assessment: категории проблем A-G
5. **Sprint 70.4** — Channel Rating: Go/Fix/Stop decision
6. **Sprint 71** — Scale to 25 channels (только если 70.4 = GO)

**PHASE 3 goal:** User writes "Хочу канал про котов" → AI → profile → sources → ready to publish

---

## 📚 Documentation

- `ROADMAP.md` — 10-phase product roadmap (Sprint 66 → Sprint 75+)
- `CHANNEL_CATALOG.md` — Strategic map of future channel network (Tier 1-3)
- `SPRINT_66_4_COMPLETION.md` — Detailed Sprint 66.4 implementation
- `SPRINT_66_4_FINAL.md` — Final test report (63/63 unit + 39/39 CI)

---

## 🔑 Key Decisions

1. **Universal Pipeline over separate pipelines** — один движок для всех каналов через Strategy Registry (вместо anime/manga/news pipelines)
2. **Archetypes as foundation** — 8 архетипов покрывают все типы каналов
3. **YAML Templates** — декларативное описание шаблонов, легко добавлять новые
4. **Profile assignment** — один profile может использоваться многими каналами
5. **PortableJSONB** — SQLite for testing, PostgreSQL for production (single codebase)
2. **Rate Limiting** — Decorator-based, applied to 8 critical POST endpoints
3. **Task Timeout** — 300s hard limit via `asyncio.wait_for`
4. **Connection Pool** — Size 20, max_overflow 30 (supports 16+ active channels)
5. **Test Strategy** — Unit (SQLite) + Integration (PostgreSQL) separation

---

## 🏆 Achievements

- ✅ **Smart Wizard** — AI-powered channel creation for any topic
- ✅ **Publishing Mode Control** — auto/approval_required/manual per channel
- ✅ **Production Hardening** — Connection pool, timeouts, structured logging
- ✅ **102 Tests Passing** — Unit + CI tests green
- ✅ **Rate Limiting** — API protected from DDoS
- ✅ **PortableJSONB** — Cross-database compatibility