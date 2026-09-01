# 🧪 Sprint 69 — 10 Channel Pilot Plan

**Start Date:** 2026-09-XX
**Duration:** 14 days
**Goal:** Validate system stability with 10 real channels across different archetypes

---

## Channel Matrix

### Group 1 — Entertainment (4 channels)

#### Channel 1: Anime News
- **Archetype:** news
- **Theme:** entertainment
- **Niche:** anime
- **Mode:** auto
- **Frequency:** 4-6 posts/day
- **Sources:** 
  - MyAnimeList News RSS
  - Anime News Network
  - Crunchyroll News
- **Media:** image (anime posters/screenshots)
- **Risk:** low

#### Channel 2: Manga Releases
- **Archetype:** releases
- **Theme:** entertainment
- **Niche:** manga
- **Mode:** approval_required
- **Frequency:** 2-3 posts/day
- **Sources:**
  - MangaDex RSS
  - MangaUpdates
  - Viz Media
- **Media:** image (cover art)
- **Risk:** low

#### Channel 3: Gaming News
- **Archetype:** news
- **Theme:** entertainment
- **Niche:** gaming
- **Mode:** approval_required
- **Frequency:** 4-6 posts/day
- **Sources:**
  - IGN RSS
  - GameSpot
  - PC Gamer
  - Kotaku
- **Media:** image+video (screenshots/trailers)
- **Risk:** medium

#### Channel 4: Movie & Series News
- **Archetype:** news
- **Theme:** entertainment
- **Niche:** movies
- **Mode:** approval_required
- **Frequency:** 4-6 posts/day
- **Sources:**
  - IMDb News RSS
  - Rotten Tomatoes
  - Deadline
  - Variety
- **Media:** image+video (posters/trailers)
- **Risk:** medium

---

### Group 2 — Technology (3 channels)

#### Channel 5: AI News
- **Archetype:** news
- **Theme:** technology
- **Niche:** ai
- **Mode:** approval_required
- **Frequency:** 4-6 posts/day
- **Sources:**
  - MIT Technology Review AI
  - OpenAI Blog
  - Hugging Face Blog
  - ArXiv CS.AI
- **Media:** image (diagrams/charts)
- **Risk:** medium
- **Note:** Critical test for hallucination detection + source filtering

#### Channel 6: Tech News
- **Archetype:** news
- **Theme:** technology
- **Niche:** tech
- **Mode:** auto
- **Frequency:** 4-6 posts/day
- **Sources:**
  - TechCrunch
  - Ars Technica
  - The Verge
  - Wired
- **Media:** image (product photos)
- **Risk:** low

#### Channel 7: Space & Science
- **Archetype:** news
- **Theme:** science
- **Niche:** space
- **Mode:** approval_required
- **Frequency:** 2-3 posts/day
- **Sources:**
  - NASA Breaking News
  - Space.com
  - Nature Astronomy
- **Media:** image (space photos)
- **Risk:** medium

---

### Group 3 — Knowledge (1 channel)

#### Channel 8: Science Facts
- **Archetype:** knowledge
- **Theme:** science
- **Niche:** general
- **Mode:** approval_required
- **Frequency:** 1-2 posts/day
- **Sources:**
  - Science Daily
  - Nature News
  - Smithsonian Magazine
- **Media:** image (infographics)
- **Risk:** medium
- **Note:** Tests Universal Pipeline on non-news archetype (Fact → Explanation → Visual → Question)

---

### Group 4 — Industry (1 channel)

#### Channel 9: Auto News
- **Archetype:** news
- **Theme:** industry
- **Niche:** automotive
- **Mode:** approval_required
- **Frequency:** 3-4 posts/day
- **Sources:**
  - Automotive News RSS
  - Car and Driver
  - Motor Trend
  - Electrek (EV)
- **Media:** image (car photos)
- **Risk:** medium

---

### Group 5 — Viral (1 channel)

#### Channel 10: Entertainment Memes
- **Archetype:** viral
- **Theme:** entertainment
- **Niche:** memes
- **Mode:** manual
- **Frequency:** manual
- **Sources:**
  - Reddit r/memes
  - Reddit r/funny
  - Imgur trending
- **Media:** image-first
- **Risk:** low
- **Note:** Tests viral archetype + image-first content + engagement optimization

---

## Publishing Mode Distribution

| Mode | Count | Channels | Percentage |
|------|-------|----------|------------|
| Auto | 2 | Anime, Tech | 20% |
| Approval Required | 7 | Manga, Gaming, Movies, AI, Space, Science, Auto | 70% |
| Manual | 1 | Memes | 10% |

**Rationale:** Conservative approach for pilot — prioritize quality validation over automation.

---

## Metrics Dashboard

### Pipeline Metrics
research_runs: total research cycles
topics_found: total topics discovered
topics_selected: topics that passed filters
posts_generated: successful generations
posts_published: successful publishes
posts_failed: failed operations

### Generation Metrics
generation_success_rate: % successful generations
average_generation_time: seconds per post
generation_retry_count: retries per generation
empty_generation_count: LLM returned empty

### Publishing Metrics
publish_success_rate: % successful publishes
telegram_errors: Telegram API failures
media_upload_errors: image/video upload failures
duplicate_posts: duplicate content detected

### Human Review Metrics (CRITICAL)
approval_rate: % approved without edit
rejection_rate: % rejected
edit_rate: % approved after edit
average_edit_distance: chars changed per edit

### Quality Indicators
IF approval_rate > 70% AND edit_rate < 30%:
→ AI quality = HIGH
ELIF approval_rate > 50% AND edit_rate < 50%:
→ AI quality = MEDIUM (needs improvement)
ELSE:
→ AI quality = LOW (critical issues)

---

## Timeline

### Day 1: Setup
- [ ] Create 10 Telegram bots via @BotFather
- [ ] Create 10 ChannelProfiles via `/profiles/from-template`
- [ ] Create 10 channels via `/channels/`
- [ ] Assign profiles to channels
- [ ] Configure sources for each channel
- [ ] Set publishing modes
- [ ] Test `/pipeline/{id}/run-universal` for each channel

### Days 2-3: Controlled Launch
- [ ] Set frequency to 1-3 posts/day per channel
- [ ] Monitor pipeline logs for errors
- [ ] Review first generated posts
- [ ] Fix critical bugs
- [ ] Adjust sources if needed

### Days 4-10: Normal Operation
- [ ] Increase frequency to target levels
- [ ] Daily metrics collection
- [ ] Review approval queue
- [ ] Monitor system health (CPU/memory/queue)
- [ ] Document issues in PILOT_ISSUES.md

### Days 11-14: Observation
- [ ] Collect final metrics
- [ ] Analyze approval/edit/rejection patterns
- [ ] Identify best/worst archetypes
- [ ] Identify best/worst sources
- [ ] Prepare PILOT_REPORT.md

---

## Success Criteria

### Must Have (Go/No-Go for Sprint 70)
- [ ] Publish success rate > 95%
- [ ] Pipeline failures < 5%
- [ ] Approval rate > 70%
- [ ] Media success rate > 90%
- [ ] Zero critical failures (data loss, crashes)

### Nice to Have
- [ ] Average generation time < 30s
- [ ] Duplicate posts < 1%
- [ ] Edit rate < 30%
- [ ] System uptime > 99%

---

## Deliverables

### During Pilot
- **PILOT_DAILY_LOG.md**: Daily metrics + issues
- **PILOT_ISSUES.md**: Tracked bugs + fixes
- **PILOT_SCREENSHOTS/**: Screenshots of good/bad posts

### After Pilot
- **PILOT_REPORT.md**: Comprehensive analysis
  - What worked
  - What failed
  - Top technical problems
  - Best archetypes
  - Worst archetypes
  - Source quality ranking
  - Generation quality analysis
  - Approval metrics breakdown
  - Scaling bottlenecks identified
  - Sprint 70 priorities

---

## Rollback Plan

If critical failures occur:
1. Pause all channels (`/channels/{id}/pause`)
2. Backup database
3. Revert to last stable commit
4. Fix issues in staging
5. Resume pilot

---

## Notes

- **Real channels only**: No test channels, no sandbox
- **Conservative modes**: 70% approval_required to catch quality issues early
- **Daily monitoring**: Check metrics every 24 hours
- **Document everything**: Every issue, every fix, every insight
- **No premature optimization**: Fix real problems, not theoretical ones

---

**Ready to launch?** Execute Sprint 69.1: Create Channel Matrix.