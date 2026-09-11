# AI Media Factory — Development Roadmap

**Last Updated:** 2026-09-11
**Current Phase:** Editorial Standardization (см. STATUS — серия Sprint 75.x = Channel Profile runtime config)

---

## Phase Overview
Phase 1: Core Infrastructure ✅ Complete (Sprints 53-66)
Phase 2: Universal Pipeline ✅ Complete (Sprint 67)
Phase 3: Intelligence ✅ Complete (Sprint 68)
Phase 4: Pilot Infrastructure ✅ Complete (Sprint 69)
Phase 5: Generic LLM Generation ✅ Complete (Sprint 70)
Phase 6: VK + Universal Publishing ✅ Complete (Sprint 71)
Phase 7: Editorial / Publication 🔄 In Progress (Sprint 72)
Phase 8: Observability → Next (Sprint 73)
Phase 9: Reliability → Next (Sprint 74)
Phase 10: Discovery Engine → Future (Sprint 76+, ранее 75+)
Phase 11: Learning Loop → Future (Sprint 77+)
Phase 12: Smart Scaling → Future (Sprint 78+)

---

## Detailed Sprint Breakdown

### Phase 1: Core Infrastructure ✅ (Sprints 53-66)
- Event Bus architecture
- Engine SDK
- Context Manager
- Repository Layer
- Dependency Injection
- Health checks
- Metrics collection
- Capability Registry

**Result:** Stable foundation for independent engines

---

### Phase 2: Universal Pipeline ✅ (Sprint 67)
- Channel Config system
- Source Registry
- Content Formatter
- Channel Wizard
- One-click START
- History tracking
- Analytics foundation
- Learning Loop design

**Result:** Unified pipeline for all channel types

---

### Phase 3: Intelligence / Classification ✅ (Sprint 68)
- 8 archetypes defined:
  - news, educational, entertainment, viral
  - releases, reviews, community, aggregator
- Archetype-specific strategies
- Content classification
- Quality evaluation
- Media policy framework

**Result:** Intelligent content processing by archetype

---

### Phase 4: Pilot Infrastructure ✅ (Sprint 69)
- Telegram publishing integration
- Database persistence (status, telegram_message_id)
- Error handling and recovery
- Scheduler with cron jobs
- Approval workflow
- Failed/rejected recovery

**Result:** Production-ready publishing infrastructure

---

### Phase 5: Generic LLM Generation ✅ (Sprint 70)
- LLM-based text generation for all 8 archetypes
- Russian language output via Ollama
- Natural text formatting (no template headers)
- Source attribution handling
- Deduplication working correctly
- Source normalization (deep copy for SQLAlchemy)

**Result:** Real LLM generation, not templates

---

### Phase 6: VK + Universal Publishing ✅ (Sprint 71)
- VK API integration (vk_publisher.py)
- VkPublishingStrategy
- VK wall.post publishing
- Multi-platform support (Telegram + VK)
- Correct publication status tracking
- Fixed: VK post status updates

**Result:** 14 channels across 2 platforms

---

### Phase 7: Editorial / Publication Layer 🔄 (Sprint 72)

#### 72.1 Publication Contract ✅
- core/models/publication.py
- MediaAsset, FormattingOptions, Publication dataclasses
- Platform-independent contract

#### 72.2 PublicationBuilder ✅
- core/models/publication_builder.py
- Archetype-based defaults for 8 archetypes
- Smart policy resolution (profile > archetype > defaults)
- Source/article/media policies

#### 72.3 Platform Renderers ✅
- core/models/renderers/telegram_renderer.py
- core/models/renderers/vk_renderer.py
- HTML source links, InlineKeyboardMarkup (Telegram)
- Plain text, URL attachments (VK)

#### 72.4 NewsPublishingStrategy Integration ✅
- Builder + Renderer pipeline
- DB updates after publication (status=published)
- telegram_message_id persisted
- Rendered Publication text sent to Telegram
- Fixed: DetachedInstanceError, return value issues
- **Test Result:** 6 posts published, msg_id 504-509

#### 72.5 GenericPublishingStrategy Integration → NEXT
- Migrate GenericPublishingStrategy to Publication Layer
- Apply PublicationBuilder + Renderer to all archetypes
- Test all 14 channels with new Publication flow

#### 72.6 14-Channel Regression
- Run all 14 channels with Publication Layer
- Verify consistent formatting across archetypes
- Fix any archetype-specific issues

#### 72.7 Naturalness / Formatting QA
- Review published content quality
- Adjust archetype defaults based on feedback
- Fine-tune source/article link policies

**Result:** Unified professional format for all channels

---

### Phase 8: Observability → NEXT (Sprint 73)

#### 73.1 Pipeline Observability
- Stage-by-stage timing (Research, Decision, Writing, etc.)
- Posts/hour per channel
- Success/failure rates
- Average generation time

#### 73.2 LLM Metrics
- LLM latency per request
- Token usage
- Model performance
- Rate limiting

### Sprint 73.3 Metrics Quality ✅ (2026-09-09)
- Сквозной `execution_id` (pipeline → pipeline_run_metrics), совместим с execution_logs
- LLM-метрики: `core/metrics/llm_metrics.py` (LLMMetricsCollector, ContextVar, изоляция между параллельными каналами)
- Инструментирован production writing path (`llm_post_generator.py`): llm_calls, llm_latency_ms, tokens_in/out, llm_model, llm_errors
- Миграция `002_add_llm_metrics.py` (6 колонок), применена к прод-Postgres
- API: блок `llm` в `/metrics/pipeline/*`; тесты `tests/test_llm_metrics.py`

#### 73.4 Dashboard ✅→NEXT (см. TASK.md — перенесён как следующий спринт)
- Real-time metrics dashboard
- Channel health overview
- Alert system
- Historical trends

**Result:** Full system visibility

---

### Phase 9: Reliability → NEXT (Sprint 74)

#### 74.1 Retry Logic
- Exponential backoff for transient errors
- Configurable retry policies per platform
- Dead-letter queue for failed posts

#### 74.2 Timeout Policies
- Per-stage timeouts
- Circuit breaker for Telegram/VK APIs
- Graceful degradation

#### 74.3 Health Checks
- Channel health monitoring
- Source health validation
- Automatic recovery
- Self-healing mechanisms

#### 74.4 Error Handling
- Structured error reporting
- Error categorization
- Automatic retry vs manual intervention

**Result:** Production-ready reliability

---

### Phase 10: Discovery Engine → FUTURE (Sprint 76+, ранее 75+)

> Нумерация 75.x занята реализованной серией «Channel Profile runtime config»
> (см. STATUS.md). Discovery сдвинут на 76+.

#### 76.1 Source Discovery
- Subscribe.ru integration (discovery only)
- RSS feed validation
- Source scoring
- Automatic source recommendations

#### 76.2 Smart Source Selection
- Topic-based source matching
- Source quality metrics
- Diversity optimization
- Source rotation

**Result:** Intelligent source discovery

---

### Phase 11: Learning Loop → FUTURE (Sprint 77+)

#### 77.1 Analytics Collection
- Post engagement metrics
- Click-through rates
- Audience behavior
- Content performance

#### 77.2 Learning Engine
- A/B testing framework
- Performance correlation
- Strategy optimization
- Automatic policy adjustment

**Result:** Self-improving content generation

---

### Phase 12: Smart Scaling → FUTURE (Sprint 78+)

#### 78.1 Gradual Scaling
- 10 → 25 → 50 → 100 channels
- Health gates at each level
- Resource monitoring
- Load balancing

#### 78.2 Distributed Architecture
- Worker pools
- Redis queues
- Distributed locks
- Task prioritization

**Result:** Scalable to 300+ channels

---

## Strategic Sequence
Editorial Standardization (72)
↓
Observability (73)
↓
Reliability (74)
↓
Discovery Engine (75+)
↓
Learning Loop (76+)
↓
Smart Scaling (77+)

**Rationale:**
1. Standardize format first (72) — ensure consistency
2. Add observability (73) — see what's happening
3. Improve reliability (74) — make it robust
4. Discover better sources (75+) — improve quality
5. Learn from performance (76+) — optimize content
6. Scale gradually (77+) — grow safely

---

## Success Metrics

### Current (Sprint 72)
- ✅ 14 channels active
- ✅ 8 archetypes with specialized strategies
- ✅ Telegram + VK support
- ✅ Publication Contract implemented
- ✅ 6 posts published with correct status

### Phase 8 Target (Sprint 73)
- [ ] All stages timed and logged
- [ ] Metrics dashboard operational
- [ ] Alert system active
- [ ] Historical data collection

### Phase 9 Target (Sprint 74)
- [ ] 99%+ success rate
- [ ] Automatic retry for transient errors
- [ ] Circuit breakers in place
- [ ] Self-healing for common failures

### Phase 12 Target (Sprint 77+)
- [ ] 100+ channels active
- [ ] Distributed architecture
- [ ] Load balancing operational
- [ ] Resource quotas enforced