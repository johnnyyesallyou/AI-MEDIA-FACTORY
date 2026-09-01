# 🗺 AI MEDIA FACTORY — PRODUCT ROADMAP

> Последний обновлён: 2026-09-01
> Текущий статус: **PHASE 1 — Production Hardening**
> Следующий шаг: **Sprint 69.6 — Monitoring & Guardrails**

---

## Текущая точка

Проект прошёл важный этап. Реализовано:

- ✅ Channel Management → Research → Generation → Media → Draft → Publish → Metrics → Learning Loop
- ✅ Research Engine, Writing Engine, PromptBuilder, LLMGenerator
- ✅ PostGenerationService, Media Policy, Telegram + VK Publishers
- ✅ Channel Wizard, Post Generator UI, Analytics Dashboard, Review Queue
- ✅ publishing_mode (auto/approval_required/manual)
- ✅ ChannelContext + Learning Loop
- ✅ Structured Logging (JSON), PortableJSONB, Pydantic V2
- ✅ Connection Pool monitoring (size 20, max_overflow 30)
- ✅ Task timeout (300s) + asyncio.wait_for wrapper
- ✅ Unit/CI test separation (63/63 unit + 39/39 CI)
- ✅ Rate Limiting (8 критических POST endpoints)
- ✅ Channel Archetypes (8 universal types)
- ✅ ChannelProfile ORM + CRUD + Assign
- ✅ Universal Content Pipeline + Strategy Registry
- ✅ Channel Templates (6 YAML) + from-template API

Сейчас проект находится на переходе:
WORKING PRODUCT
↓
SCALABLE PLATFORM

---

# 🧱 PHASE 1 — PRODUCTION HARDENING

## Sprint 66 — Production Hardening ✅ CLOSED

### Цель
Закрыть технические риски до масштабирования.

### 66.5 — Pipeline Failure Tracking ✅ CLOSED

Создаём единый журнал ошибок pipeline.

**Таблица `pipeline_failures`:**
```sql
id, channel_id, task_id, pipeline, job, 
error_type, error_message, attempt, created_at
Типы ошибок: timeout, exception, rate_limit, network, validation, llm_error, media_error, publish_error, unknown
Архитектура:
Pipeline → Job → Exception/Timeout → PipelineFailure → Database → API → Monitoring
Зачем: При 50 каналах невозможно читать Docker logs. Нужно видеть какие каналы падают, какие jobs, как часто и почему.
66.6 — Async Tests Stabilization
Разделить тесты: unit / integration / requires_llm / slow
Убрать зависания в Automation Manager, Worker lifecycle, Task cancellation
CI: pytest -m "not integration"
Локально: pytest -m integration
66.7 — GitHub Actions CI
Минимальный pipeline:
git push → Install dependencies → Ruff → Pytest (unit) → CI tests → Result
Позже: security scan, docker build, deployment
Результат Sprint 66
✅ Errors tracked
✅ Async tests stable
✅ CI on every push
✅ Unit tests without Docker
✅ Integration tests isolated
✅ Structured logs
✅ Timeout protection
🚀 PHASE 2 — CHANNEL SCALING ARCHITECTURE
Sprint 67 — Channel Profiles & Universal Pipeline
Цель: Перестать строить отдельную систему под каждую тему.
67.1 — Channel Archetypes
Ограниченный набор: news, releases, educational, entertainment, viral, reviews, community, aggregator
67.2 — Channel Profile
YAML-конфигурация: theme, niche, archetype, audience, language, tone, content, research, media, publishing, learning
67.3 — Universal Pipeline
UniversalContentPipeline вместо AnimePipeline/MangaPipeline/NewsPipeline
67.4 — Strategy Registry
CONTENT_STRATEGIES = {
    "news": NewsStrategy,
    "educational": EducationalStrategy,
    "viral": ViralStrategy,
    "reviews": ReviewStrategy,
}
67.5 — Channel Templates
Библиотека: channel_templates/news.yaml, releases.yaml, educational.yaml, viral.yaml, reviews.yaml, community.yaml
🧠 PHASE 3 — SMART CHANNEL CREATION
Sprint 68 — Smart Wizard
Цель: Пользователь описывает канал обычным языком.
68.1 — Theme Classification
LLM определяет: theme, niche, archetype, risk_level
68.2 — Strategy Suggestion
AI предлагает: content strategy, tone, frequency, media, publishing mode
68.3 — Source Recommendation
AI предлагает источники по теме (RSS, web, Reddit, publishers)
68.4 — Risk Classification
Low Risk (Anime, Gaming, Movies, Memes) → auto
Medium Risk (Business, Tech, Science, History) → approval_required
High Risk (Finance, Crypto, Medicine, Nutrition) → manual
🌐 PHASE 4 — PILOT NETWORK
Sprint 69 — 10 Channel Pilot
Pilot Network (10 каналов):
Entertainment: Anime News, Manga Releases, Gaming News, Movie News
Technology: AI News, Tech News, Space News
Knowledge: Science Facts
Industry: Auto News
Viral: Entertainment
Режим публикации:
30% auto (Anime, Manga)
50% approval_required (AI, Science, Auto)
20% manual (experimental)
Длительность: 14–30 дней
Метрики:
Generation: posts_generated, generation_time, llm_errors
Research: topics_found, duplicates_removed, source_errors
Media: image_success_rate, video_success_rate, fallback_rate
Publishing: publish_success_rate, telegram/vk_errors
Infrastructure: queue_size, worker_utilization, db_pool, memory, cpu
Content: approval_rate, rejection_rate, edit_rate
📈 PHASE 5 — SCALE TEST
Sprint 70 — 10 → 25 → 50 Channels
Этап 1: 10 channels (7–14 дней)
Этап 2: 25 channels (проверка workers, queue, DB, LLM, Telegram limits)
Этап 3: 50 channels (система становится похожей на платформу)
Ожидаемые проблемы: queue congestion, slow LLM, source rate limits, Telegram rate limits, memory, DB connections, retry storms, duplicate content
🔥 PHASE 6 — MEDIA NETWORK MANAGEMENT
Sprint 71 — Network Dashboard
Channels: Active 43, Paused 5, Errors 2
Posts Today: Generated 186, Published 173, Failed 3
Review Queue: Pending 17
System: Workers 12, Queue 8, DB Pool 24%
Channel Groups + Bulk operations (Start/Pause/Publishing Mode/Template Update)
🧠 PHASE 7 — NETWORK INTELLIGENCE
Sprint 72 — Cross-Channel Intelligence
Learning Loop расширяется до Network Intelligence.
Принцип: Insight → Recommendation → Human Approval → Strategy Update
💰 PHASE 8 — COST & RESOURCE MANAGEMENT
Sprint 73 — Cost Control
Аналитика: Cost per channel, Cost per post, LLM tokens, Media requests, API requests, Compute time
🏗 PHASE 9 — PRODUCTION INFRASTRUCTURE
Sprint 74 — Production Deployment
Переход от Docker Compose к production-архитектуре:
Frontend → API → PostgreSQL + Redis + Worker Pool + LLM Service + Media Service + Object Storage
🌍 PHASE 10 — LARGE SCALE NETWORK
Sprint 75+ — 100 → 300 Channels
Этапы: 50 stable → 100 → 150 → 300
Каждый этап: load test + monitoring + failure analysis + cost analysis + content quality analysis
🎯 Стратегия масштабирования
PHASE 1  Finish Production Hardening (Sprint 66)
        ↓
PHASE 2  Channel Profiles + Universal Pipeline (Sprint 67)
        ↓
PHASE 3  Smart Wizard (Sprint 68)
        ↓
PHASE 4  10 Channel Pilot (Sprint 69)
        ↓
PHASE 5  25 → 50 Channel Scale (Sprint 70)
        ↓
PHASE 6  Network Management (Sprint 71)
        ↓
PHASE 7  Cross-Channel Intelligence (Sprint 72)
        ↓
PHASE 8  Cost Control (Sprint 73)
        ↓
PHASE 9  Production Infrastructure (Sprint 74)
        ↓
PHASE 10 100–300 Channel Network (Sprint 75+)
Ключевой принцип
AI Media Factory не должна превратиться в "систему с 300 отдельными пайплайнами".
Она должна стать универсальным движком, который получает Channel Profile и автоматически выбирает стратегии research, generation, media и publishing.---

# 🧪 PHASE 4 — REAL WORLD VALIDATION

## Sprint 69 — 10 Channel Pilot ✅ IN PROGRESS (Days 2-3)

### 69.1 — Telegram Channel Creation ✅ CLOSED
10 channels created via Telethon, @openclavv_ai_bot added as admin to all.

### 69.2 — RSS Sources Configuration ✅ CLOSED
2-3 real RSS sources per channel (22 URLs total from source_recommendations.py).

### 69.3 — Real RSS Fetch Fix ✅ CLOSED
NewsResearchStrategy now reads from channel.content_profile.sources (real URLs).

### 69.4 — LLM Generation (Ollama) ✅ CLOSED
llama3.1:8b generates Russian news posts (345-800 chars per post).

### 69.5 — Real Telegram Publishing ✅ CLOSED
18 posts published to Anime News Daily (message_ids 11-31).

### 69.6 — Monitoring & Guardrails ⏳ **NEXT**
Deduplication, rate limits, scheduler safety, error tracking.

### 69.7 — Controlled Launch ⏳
1-3 posts/day/channel for Days 4-10 (conservative mode).

### 69.8 — Approval Queue UI ⏳
UI for approval_required channels (Manga, Gaming, Movies, AI, Space, Science, Auto).

### Результат Sprint 69
Real-world validation: 10 channels × different archetypes × different publishing modes.



**Цель:** Проверить систему на 10 реальных каналах с разными archetypes в течение 7-14 дней.

### Матрица каналов

| # | Channel | Archetype | Mode | Posts/day |
|---|---------|-----------|------|-----------|
| 1 | Anime News | news | auto | 4-6 |
| 2 | Manga Releases | releases | approval | 2-3 |
| 3 | Gaming News | news | approval | 4-6 |
| 4 | Movie & Series News | news | approval | 4-6 |
| 5 | AI News | news | approval | 4-6 |
| 6 | Tech News | news | auto | 4-6 |
| 7 | Space & Science | news | approval | 2-3 |
| 8 | Science Facts | knowledge | approval | 1-2 |
| 9 | Auto News | news | approval | 3-4 |
| 10 | Entertainment Memes | viral | manual | manual |

### Publishing Modes
- **Auto (20%)**: Anime, Tech
- **Approval Required (70%)**: Manga, Gaming, Movies, AI, Space, Science, Auto
- **Manual (10%)**: Memes

### Ключевые метрики
- Approval rate > 70%
- Publish success rate > 95%
- Pipeline failures < 5%
- Media success rate > 90%

### Timeline
- **Day 1**: Setup (10 channels, sources, modes)
- **Days 2-3**: Controlled launch (1-3 posts/day)
- **Days 4-10**: Normal operation (full frequency)
- **Days 11-14**: Observation + data collection

**Result:** PILOT_REPORT.md with real-world validation data

---

## Sprint 70 — Pilot Analysis & Stabilization

**Цель:** Проанализировать данные пилота, улучшить pipeline на основе реальных проблем.

### 70.1 Source Quality Analysis
Для каждого источника:
topics_found → topics_selected → posts_published
Удалить источники с < 5% conversion rate.

### 70.2 Archetype Performance
Сравнить archetypes по метрикам:
- approval_rate
- edit_rate  
- generation_failures
- engagement

### 70.3 Prompt Improvement
На основе реальных bad posts / edited posts / rejected posts:
Bad Post → Analyze → Prompt Fix → Regenerate → Validate

**Result:** Stabilized pipeline ready for 25-channel scale test

---

# 📈 PHASE 5 — MULTI-CHANNEL OPERATIONS

## Sprint 71 — Channel Operations Layer

### Channel Groups
Technology Group
├── AI News
├── Tech News
└── Space News
Entertainment Group
├── Anime
├── Manga
├── Gaming
└── Movies

### Bulk Operations
- Start/Pause group
- Change publishing mode for group
- Bulk review (approve selected drafts)

### Global Dashboard
Channels: 10 | Active: 8 | Paused: 2
Posts today: 27 | Published: 24 | Failed: 1 | Drafts: 2
Average approval rate: 87%

**Result:** Efficient management of 10+ channels

---

## Sprint 72 — Scale Test: 25 Channels

**Цель:** Проверить систему на 25 concurrent channels (~75 posts/day).

### Load
- 25 channels × 3 posts/day = 75 posts/day
- 75 research cycles + 75 generations + 75 media searches + 75 publishes

### Expected Issues
- Database bottleneck
- Redis queue overload
- Ollama concurrency
- Telegram rate limits
- RSS fetch duplication

**Result:** Identified scaling bottlenecks + fixes

---

## Sprint 73 — Scale Test: 50 Channels

**Цель:** Production-scale тест на 50 каналах (~150 posts/day).

### Metrics
- posts/hour
- jobs/hour
- LLM tokens/day
- database writes/day
- queue depth
- memory/CPU/GPU usage

**Result:** Validated 50-channel stability

---

# 🧠 PHASE 6 — NETWORK INTELLIGENCE

## Sprint 74 — Cross-Channel Intelligence

**Цель:** One event → multiple unique posts for different channels.

### Example
Event: OpenAI releases new model
↓
Topic Intelligence
↓
Channel Matching
↓
AI News → technical details
Tech News → market impact
Business → company analysis
Programming → developer use cases

**Result:** Intelligent content distribution

---

## Sprint 75 — Content Reuse Engine

**Цель:** One research event → multiple content variations.

### Example
NASA launch
↓
Space News → breaking news
Science Facts → technology explanation
Tech News → engineering breakdown
Short Facts → quick fact

**Result:** Reduced cost per post via content reuse

---

# 💼 PHASE 7 — BUSINESS & SCALE

## Sprint 76 — 100+ Channel Infrastructure

**Цель:** Horizontal scaling для 100+ каналов.

### Architecture
- Queue system (Celery/Dramatiq/custom)
- Horizontal workers:
  - Research Workers × N
  - Generation Workers × N
  - Media Workers × N
  - Publish Workers × N

**Result:** Infrastructure ready for mass scale

---

## Sprint 77 — Autonomous Media Network

**Цель:** Финальная архитектурная цель.
Topic Network
↓
Research Layer
↓
Canonical Topics
↓
Intelligence Layer
↓
Technology / Entertainment / Finance
↓
Channels[] → Generate → Review → Publish
↓
Analytics → Learning Loop ↺

**Result:** Fully autonomous AI media network

---

# 📊 Scaling Strategy

## Current: Sprint 69
**10 channels** (pilot validation)

## Next: Sprint 72
**25 channels** (after 14 days stable operation of 10)

**Requirements:**
- Publish success rate > 95%
- Pipeline failures < 5%
- Approval rate > 70%
- Media success rate > 90%

## Later: Sprint 73
**50 channels** (after 14 days stable operation of 25)

## Future: Sprint 76
**100+ channels** (after proven 50-channel stability)

---

# 🎯 Key Principle

**Не масштабировать преждевременно.**

Каждый этап должен доказать стабильность перед переходом к следующему:
10 stable → 25 → 50 → 100+

Реальные данные пилота покажут, какие части требуют улучшения, а какие являются преждевременным усложнением.
