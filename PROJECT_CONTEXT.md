# AI Media Factory — Project Context

**Last Updated:** 2026-09-08
**Current Sprint:** 72.4 (completed)
**Next Sprint:** 72.5 — GenericPublishingStrategy Integration

---

## What is this project?

AI Media Factory is an automated content generation and publishing system that manages **14 digital media channels** across **Telegram** (13) and **VK** (1) platforms. It uses LLM-based content generation, intelligent topic selection, and multi-platform publishing to run professional media channels with minimal human intervention.

---

## Current State (Post Sprint 72.4)

### Production Numbers
- **14 active channels** across 2 platforms
- **8 content archetypes** with specialized strategies
- **Universal Pipeline** end-to-end automation operational
- **Publication Layer** implemented (Sprint 72)
- **Real LLM generation** via Ollama (Russian language)
- **Telegram publishing** with HTML source links validated
- **VK publishing** operational

### Last Validated Test (Sprint 72.4)
- **Channel:** Новости 📰
- **Result:** 6 posts published successfully
- **Telegram message IDs:** 504, 505, 506, 507, 508, 509
- **HTML source links:** Present in all posts (<a href="...">)
- **Pipeline duration:** ~173 seconds for 6 topics
- **DB status:** All posts marked published

---

## Architecture Overview

### High-Level Flow
Channel Profile
↓
Universal Pipeline
Research → Decision → Writing → Evaluation → Media
↓
PublicationBuilder (applies archetype policies)
↓
Publication Contract (platform-independent)
↓
┌───────┴───────┐
↓ ↓
TelegramRenderer VKRenderer
↓ ↓
Telegram Publisher VK Publisher
↓ ↓
Database Update (status=published, message_id)

### Key Architectural Principle (Sprint 72)

> **Publication describes WHAT should be published. Renderer describes HOW it is represented on a platform.**

This separation allows:
- Same content rendered differently per platform
- Easy addition of new platforms
- Archetype-specific formatting without code duplication
- Natural editorial style (no rigid AI templates)

---

## Content Archetypes

Eight supported archetypes, each with specialized policies:

| Archetype | Source Link | Article Link | Media | Typical Use |
|-----------|-------------|--------------|-------|-------------|
| **news** | always | conditional | preferred | Breaking news, current events |
| **educational** | optional | never | preferred | Tutorials, explainers |
| **entertainment** | never | never | required | Memes, fun content |
| **viral** | never | never | required | Shareable content |
| **releases** | always | never | required | Product launches |
| **reviews** | always | always | required | Product reviews |
| **community** | never | never | optional | Discussions |
| **aggregator** | always | always | preferred | Curated content |

**Policy Resolution:** Profile settings → Archetype defaults → Global defaults

---

## Platform Support

### Telegram (13 channels)
- Bot API integration
- HTML parse mode with proper escaping
- InlineKeyboardMarkup for "Читать полностью" button
- Photo/video support
- Rate limiting (1s between messages)
- Clickable source links: <a href="url">Источник</a>

### VK (1 channel — AI Media Factory)
- wall.post API
- Plain text messages (no HTML)
- URL attachments
- Media attachments
- Source as text line: "Источник: TheVerge"

---

## Production Path

### Successful Publication Flow
automation_manager_v2.run_channel_now(channel_id)
Load channel + profile from database
Universal Pipeline executes stages:
Research: fetch RSS topics
Decision: select topics
Writing: generate text via LLM
Evaluation: score quality
Media: select images (placeholder)
Publishing Strategy:
Create ContentORM (status=pending)
Build Publication via PublicationBuilder
Render via TelegramRenderer/VKRenderer
Send to platform API
Update ContentORM (status=published, message_id)
Return success

---

## File Structure

AI-MEDIA-FACTORY/
├── core/models/
│ ├── publication.py # Publication Contract (Sprint 72.1)
│ ├── publication_builder.py # PublicationBuilder (Sprint 72.2)
│ ├── renderers/
│ │ ├── telegram_renderer.py # TelegramRenderer (Sprint 72.3)
│ │ └── vk_renderer.py # VKRenderer (Sprint 72.3)
│ ├── channel_profile_orm.py
│ ├── channel_orm.py
│ └── content_orm.py
├── backend/engines/
│ ├── news_strategies.py # NewsPublishingStrategy ✅ integrated
│ ├── generic_strategies.py # GenericPublishingStrategy ⚠️ TODO 72.5
│ ├── telegram_publisher.py
│ ├── vk_publisher.py
│ ├── rss_fetcher.py
│ ├── llm_post_generator.py
│ └── deduplicator.py
├── backend/automation/
│ ├── automation_manager_v2.py
│ ├── universal_pipeline.py
│ └── scheduler.py
└── docs/
├── STATUS.md
├── ROADMAP.md
├── ARCHITECTURE.md
├── TASK.md
└── PROJECT_CONTEXT.md # This file

---

## Source of Truth

### For Current Development
1. **STATUS.md** — project state, completed sprints, current limitations
2. **ROADMAP.md** — development phases and milestones
3. **TASK.md** — current backlog and next sprint
4. **ARCHITECTURE.md** — system design and components (detailed)
5. **AI_CONTEXT.md** — AI-assisted development rules

### For Code
- **Local repository** — source of truth
- **Docker containers** — running environment
- **PostgreSQL database** — content and channel data

### For Configuration
- **channel.content_profile["sources"]** — production sources
- ⚠️ channel.sources — legacy, NOT production source of truth

---

## Development Workflow

### Sprint Cycle
1. **Plan** — review TASK.md, define sprint goals
2. **Implement** — write code, test locally
3. **Test** — run on actual channels (not mocks)
4. **Fix** — resolve issues found in testing
5. **Commit** — push to git with descriptive message
6. **Document** — update STATUS.md, ROADMAP.md, TASK.md

### Testing Strategy
- Manual testing for each sprint on real channels
- Verify database updates (status=published, message_id set)
- Check published content quality
- Document test results in STATUS.md

---

## Technical Debt

### High Priority
- ⚠️ **GenericPublishingStrategy** not using Publication Layer (Sprint 72.5)
- ⚠️ **No observability** — no metrics, monitoring, alerting (Sprint 73)
- ⚠️ **No retry logic** — transient failures cause permanent failures (Sprint 74)

### Medium Priority
- ⚠️ Legacy engines/research/engine.py — unused, should be removed
- ⚠️ Old channel.sources field — use content_profile["sources"]
- ⚠️ Synchronous VK publishing — should be async
- ⚠️ Scheduler get_next_run() complexity

### Low Priority
- ⚠️ Image generation (currently placeholders)
- ⚠️ Video support (not implemented)
- ⚠️ Multi-language (Russian only currently)
- ⚠️ Advanced deduplication (semantic similarity)

---

## Key Decisions

### Publication Layer (Sprint 72)
**Decision:** Separate content contract from platform rendering

**Rationale:**
- One Publication, multiple platform renderings
- Archetype-specific formatting without code duplication
- Easy to add new platforms (just add a renderer)

### Archetype-Based Defaults
**Decision:** Use archetype to determine default policies

**Rationale:**
- Different content types have different formatting needs
- Avoid hardcoding in engines
- Profile can override archetype defaults

### Russian Language Generation
**Decision:** Use Ollama (llama3.1:8b) for Russian text

**Rationale:**
- Target audience is Russian-speaking
- Natural text without translation artifacts
- Local execution (no API costs)

### Natural Editorial Style
**Decision:** Avoid rigid AI-looking templates

**Rationale:**
- User should see "normal media channel post"
- Not "AI wrote a post using a template"
- Platform-specific rendering handles formatting

---

## Known Limitations

### Current
- Image generation uses placeholders (not real generation)
- Video support not implemented
- Single language (Russian)
- No retry logic for transient failures
- No metrics or observability
- GenericPublishingStrategy not on Publication Layer yet

### Planned
- Image generation (future sprint)
- Observability (Sprint 73)
- Reliability improvements (Sprint 74)
- Discovery Engine (Sprint 75+)

---

## Changelog

### Sprint 72.4 (Current) ✅
- NewsPublishingStrategy integrated with Publication Layer
- DB updates working (status=published, telegram_message_id)
- 6 posts published with message IDs 504-509
- HTML source links in all posts

### Sprint 72.1-72.3 ✅
- Publication Contract defined
- PublicationBuilder created with archetype defaults
- TelegramRenderer + VKRenderer created
- HTML escaping bug fixed

### Sprint 71 ✅
- VK integration complete
- 14 channels active across 2 platforms
- VK post status updates working

### Sprint 70 ✅
- Generic LLM generation for all 8 archetypes
- Russian language output via Ollama
- Natural text formatting
- Source normalization

### Sprint 69 ✅
- Telegram publishing integration
- DB persistence (status, telegram_message_id)
- Scheduler with cron jobs
- Error handling and recovery