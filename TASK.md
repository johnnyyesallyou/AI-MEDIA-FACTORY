# AI Media Factory — Current Tasks

**Last Updated:** 2026-09-08
**Current Sprint:** 72.4 (completed)
**Next Sprint:** 72.5

---

## Current Focus

### ✅ Sprint 72.4: NewsPublishingStrategy Integration (COMPLETED)
- [x] PublicationBuilder integrated into NewsPublishingStrategy
- [x] TelegramRenderer applied to news posts
- [x] DB updates after publication (status=published, telegram_message_id)
- [x] Rendered Publication text sent to Telegram
- [x] Fixed: DetachedInstanceError
- [x] Fixed: publish() return value
- [x] **Test Result:** 6 posts published, msg_id 504-509

---

## Next Sprint

### 🔄 Sprint 72.5: GenericPublishingStrategy Integration (NEXT)

**Goal:** Migrate GenericPublishingStrategy to Publication Layer

**Tasks:**
- [ ] Integrate PublicationBuilder into GenericPublishingStrategy
- [ ] Apply TelegramRenderer for Telegram channels
- [ ] Apply VKRenderer for VK channels
- [ ] Test with different archetypes (educational, entertainment, viral)
- [ ] Verify DB updates (status=published, telegram_message_id/vk_post_id)
- [ ] Test 3-5 channels with new Publication flow

**Success Criteria:**
- GenericPublishingStrategy uses PublicationBuilder
- All archetypes render through platform-specific Renderer
- DB correctly updated after publication
- No regressions in existing channels

**Estimated Time:** 2-3 hours

---

## Short-term Backlog

### Sprint 72.6: 14-Channel Regression
- [ ] Run all 14 channels with Publication Layer
- [ ] Verify consistent formatting across archetypes
- [ ] Fix any archetype-specific issues
- [ ] Document archetype-specific behavior

### Sprint 72.7: Naturalness / Formatting QA
- [ ] Review published content quality
- [ ] Adjust archetype defaults based on feedback
- [ ] Fine-tune source/article link policies
- [ ] Create regression test suite (50-100 examples)

### Sprint 73: Observability
- [ ] Stage-by-stage timing instrumentation
- [ ] Metrics collection (posts/hour, success rate, latency)
- [ ] Dashboard implementation
- [ ] Alert system for failures

### Sprint 74: Reliability
- [ ] Retry logic with exponential backoff
- [ ] Circuit breakers for Telegram/VK APIs
- [ ] Dead-letter queue for failed posts
- [ ] Health checks and self-healing

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
- [ ] **No retry logic** — transient failures cause permanent failures

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
- ⚠️ No retry logic for transient errors
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