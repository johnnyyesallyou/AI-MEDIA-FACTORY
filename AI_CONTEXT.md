# AI Media Factory - AI-Assisted Development Context

**Last Updated:** 2026-09-09
**Current Sprint:** 74.2 (completed)
**Next Sprint:** 74.3 - Channel Pause (channel-wide pause on 429 + self-healing integration + frontend status)

---

## Quick Reference

### Current State
- **Sprint:** 74.2 completed
- **Next:** 74.3 - Channel Pause (channel-wide pause on 429 + self-healing integration)
- **Status:** 14 channels active, Reliability Layer (retry + circuit breaker + DLQ + self-healing) implemented
- **Last Test:** reliability regression 40 passed (18 Sprint 74.1 + 22 Sprint 74.2)

### Source of Truth (read these first)
1. **STATUS.md** - project state and completed sprints
2. **ROADMAP.md** - development phases and milestones
3. **TASK.md** - current backlog and next sprint
4. **ARCHITECTURE.md** - system design (detailed)
5. **PROJECT_CONTEXT.md** - project overview and quick start

---

## Key Architectural Concepts

### Publication Layer (Sprint 72) - MOST IMPORTANT

**The core principle:**
> Publication describes WHAT should be published. Renderer describes HOW it is represented on a platform.

**Components:**
- Publication (core/models/publication.py) - platform-independent content contract
- PublicationBuilder (core/models/publication_builder.py) - builds Publication from content dict
- TelegramRenderer (core/models/renderers/telegram_renderer.py) - renders for Telegram
- VKRenderer (core/models/renderers/vk_renderer.py) - renders for VK

**Why this matters:**
- One Publication can be rendered differently per platform
- Archetype-specific formatting without code duplication
- Easy to add new platforms (just add a renderer)
- Natural editorial style (no rigid AI templates)

### Archetype-Based Policies

**8 archetypes:** news, educational, entertainment, viral, releases, reviews, community, aggregator

**Policies:**
- source_link: always | optional | never
- article_link: always | conditional | never
- media_policy: required | preferred | optional | none
- max_length, max_paragraphs, emojis, allow_bullets

**Policy Resolution:** Profile settings > Archetype defaults > Global defaults

### Universal Pipeline

**Stages:**
1. Research (RSS fetching)
2. Decision (topic selection)
3. Writing (LLM generation via Ollama, llama3.1:8b)
4. Evaluation (quality scoring)
5. Media (image/video selection - currently placeholder)
6. Publication (PublicationBuilder)
7. Publishing (platform API)

---

## Development Rules

### When Working on Publication Layer

**DO THIS:**
- Use PublicationBuilder to create platform-independent Publication
- Use Renderer to transform Publication for specific platform
- Publisher sends rendered result to platform API

**DON'T DO THIS:**
- Don't put platform-specific logic in PublicationBuilder
- Don't add platform-specific fields to Publication dataclass
- Use platform_metadata dict for platform-specific data instead

### When Working on Publishing Strategies

**DO THIS:**
1. Use PublicationBuilder + Renderer (don't format text manually)
2. Save content_id BEFORE db.close() to avoid DetachedInstanceError
3. Use content_id in all post-close operations
4. Always update database after successful publication (status=published, message_id)

**DON'T DO THIS:**
- Don't format text manually - let Renderer do it
- Don't access content.id after db.close() (DetachedInstanceError!)
- Don't forget to update database after publication

### When Working on Engines

**DO THIS:**
- Engines return structured data (dicts), not formatted strings
- PublicationBuilder handles formatting downstream

**DON'T DO THIS:**
- Don't format output in engines
- Don't add emoji/templates in engine output

### When Working with Sources

**DO THIS:**
- Use channel.content_profile["sources"] for production sources
- Each source is a dict: {name, url, type, source_type}

**DON'T DO THIS:**
- Don't use legacy channel.sources field
- Production source of truth is content_profile["sources"]

---

## Common Tasks

### Adding New Archetype
1. Add to ARCHETYPE_DEFAULTS in publication_builder.py
2. Define policies: source_link, article_link, media_policy, max_length, etc.
3. Test with sample content
4. Document in ARCHITECTURE.md

### Adding New Platform
1. Create renderer in core/models/renderers/
2. Create publisher in backend/engines/
3. Integrate into publishing strategy
4. Test end-to-end

### Debugging Publication Issues
1. Check Publication object (text, source, article_url)
2. Check Renderer output (rendered text, parse_mode)
3. Check database (status, telegram_message_id, draft_text)

---

## Testing Checklist

### Before Committing
- Code compiles without errors (python -m py_compile)
- Manual test on real channel (not mock)
- Database updated correctly (status=published, message_id set)
- Published content looks correct
- No regressions in existing channels
- Documentation updated (STATUS.md, TASK.md)

### Sprint Completion
- All sprint tasks completed
- Tested on multiple channels (3-5 minimum)
- No critical bugs or regressions
- STATUS.md updated with sprint results
- ROADMAP.md updated if phase completed
- TASK.md updated with next sprint
- ARCHITECTURE.md updated if architecture changed
- Commit message describes what was done and why

---

## Known Issues

### Resolved (Historical)
- DetachedInstanceError in NewsPublishingStrategy (Sprint 72.4)
  - Fix: Save content_id = content.id before db.close()
- VK post status not updating (Sprint 71)
  - Fix: Added row.status = "published" in VK publishing path
- Telegram 401 Unauthorized for 3 channels (Sprint 70)
  - Fix: Updated bot tokens and chat_ids
- Pydantic ValidationError for ChannelScheduleResponse (Sprint 70.5)
  - Fix: Changed next_run: datetime to next_run: Optional[Any]
- HTML escaping bug in TelegramRenderer (Sprint 72.3)
  - Fix: Escape main text BEFORE adding source line

### Open (Current)
- GenericPublishingStrategy not using Publication Layer (Sprint 72.5)
- No metrics or observability (Sprint 73)
- Pipeline reports "0 published" even when posts succeed (cosmetic - return value issue)

---

## File Locations Quick Reference

### Publication Layer
- core/models/publication.py - Publication Contract
- core/models/publication_builder.py - PublicationBuilder + ARCHETYPE_DEFAULTS
- core/models/renderers/telegram_renderer.py - TelegramRenderer
- core/models/renderers/vk_renderer.py - VKRenderer

### Publishing Strategies
- backend/engines/news_strategies.py - NewsPublishingStrategy (integrated)
- backend/engines/generic_strategies.py - GenericPublishingStrategy (TODO Sprint 72.5)

### Publishers
- backend/engines/telegram_publisher.py - Telegram API client
- backend/engines/vk_publisher.py - VK API client

### Engines
- backend/engines/rss_fetcher.py - RSS fetching
- backend/engines/llm_post_generator.py - LLM text generation
- backend/engines/deduplicator.py - URL-based deduplication

### Pipeline
- backend/engines/universal_pipeline.py - Universal Pipeline
- backend/automation/automation_manager_v2.py - Orchestration
- backend/automation/scheduler.py - Cron jobs

### Reliability (Sprint 74)
- backend/core/reliability.py - retry engine, CircuitBreaker (CLOSED/OPEN/HALF_OPEN), registry get_breaker(), channel pause, alert-disable
- backend/core/rate_limiter.py - rate limiting / throttle (compatibility proxy → reliability breaker)
- backend/core/dead_letter.py - Dead-Letter Queue (pipeline_failures)
- backend/core/self_healing.py - SelfHealingWorker (re-publish from DLQ)
- backend/app/api/v1/reliability.py - /api/v1/reliability/* endpoints
- backend/core/error_taxonomy.py - error classification

### Database Models
- core/models/content_orm.py - Content
- core/models/channel_orm.py - Channel
- core/models/channel_profile_orm.py - ChannelProfile
- core/models/pipeline_failure_orm.py - PipelineFailure (base for DLQ)

---

## Questions?

If you're unsure about something:
1. Check STATUS.md for current state
2. Check ARCHITECTURE.md for design details
3. Check TASK.md for known issues and next sprint
4. Look at recent commits for examples
5. Test locally before making changes
6. When in doubt, ask for clarification

---

## Changelog

### Sprint 74.2 (Current) ✅
- Unified CircuitBreaker (CLOSED/OPEN/HALF_OPEN) in reliability.py + registry get_breaker()
- Publisher / Self-Healing / Rate limiter use the same breaker (single source of truth)
- Channel-wide pause on 429 (pause_channel / ChannelPausedError)
- Alert-disable on CONFIGURATION errors (401/403 → is_active=False)
- /api/v1/circuit-breakers → unified breaker (primary) + rate_limit_stats (auxiliary)
- Tests 22/22 passed (test_reliability_74_2.py)

### Sprint 74.1 ✅
- Retry engine (with_retry / @retry_async), exponential backoff, Retry-After (429)
- VK error classification (error_code → ErrorType)
- Dead-Letter Queue (dead_letter.py) on pipeline_failures
- Integrated into telegram_publisher.py / vk_publisher.py
- Tests 18 passed (test_reliability.py)

### Sprint 73 ✅
- Pipeline observability (stage timing, posts/hour, success/failure rates)
- LLM metrics (latency, token usage, model performance)
- /metrics/pipeline endpoints + frontend dashboard

### Sprint 72.4
- NewsPublishingStrategy integrated with Publication Layer
- DB updates working correctly (status=published, telegram_message_id)
- 6 posts published successfully (msg_id 504-509)
- HTML source links present in all posts

### Sprint 72.1-72.3
- Publication Contract defined
- PublicationBuilder created with archetype-based defaults
- TelegramRenderer and VKRenderer created
- HTML escaping bug fixed

### Sprint 71
- VK integration complete
- 14 channels active across 2 platforms

### Sprint 70
- Generic LLM generation for all 8 archetypes
- Russian language output via Ollama
- Natural text formatting (no template headers)
