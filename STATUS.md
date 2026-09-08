# AI Media Factory — Status

**Last Updated:** 2026-09-08 (Sprint 72.6 regression completed)
**Current Sprint:** 72.6 (completed)
**Next Sprint:** 73 — Observability

---

## Current State

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
- 📊 Первый вывод: **~92% времени пайплайна — LLM-генерация (writing)**, research ~3%, publishing ~4%

### Production System
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