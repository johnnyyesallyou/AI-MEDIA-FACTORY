# 🗺 AI MEDIA FACTORY — PRODUCT ROADMAP

> Последний обновлён: 2026-09-01
> Текущий статус: **PHASE 1 — Production Hardening**
> Следующий шаг: **Sprint 66.5 — Pipeline Failure Tracking**

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

Сейчас проект находится на переходе:
WORKING PRODUCT
↓
SCALABLE PLATFORM

---

# 🧱 PHASE 1 — PRODUCTION HARDENING

## Sprint 66 — Production Hardening

### Цель
Закрыть технические риски до масштабирования.

### 66.5 — Pipeline Failure Tracking ⏳ **СЛЕДУЮЩИЙ ШАГ**

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
Она должна стать универсальным движком, который получает Channel Profile и автоматически выбирает стратегии research, generation, media и publishing.