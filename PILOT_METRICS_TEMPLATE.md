# Pilot Metrics Collection Template

**Observation Period:** 2026-09-02 → 2026-09-16 (14 days)

## Channel Metrics

### 1. Anime News Daily (Telegram, auto)
- **Generated:** 0 posts
- **Published:** 0 posts
- **Failed:** 0 posts
- **Rejected:** N/A (auto mode)
- **Edited:** 0 posts
- **Approval Rate:** N/A
- **Publish Success Rate:** 0%
- **Source → Topic Conversion:** 0%
- **Duplicate Rate:** 0%
- **Average Text Length:** 0 chars
- **Media Distribution:** image: 0, video: 0, none: 0
- **Errors:** []

### 2. Manga Releases Tracker (Telegram, approval_required)
- **Generated:** 0 posts
- **Published:** 0 posts
- **Failed:** 0 posts
- **Rejected:** 0 posts
- **Edited:** 0 posts
- **Approval Rate:** 0%
- **Publish Success Rate:** 0%
- **Source → Topic Conversion:** 0%
- **Duplicate Rate:** 0%
- **Average Text Length:** 0 chars
- **Media Distribution:** image: 0, video: 0, none: 0
- **Errors:** []

### 3. Gaming News Hub (Telegram, approval_required)
[... аналогично для всех 14 каналов ...]

---

## Source Quality Analysis

### MyAnimeList News (Anime News Daily)
Fetched: 0 topics
↓
Unique: 0 topics
↓
Accepted: 0 topics
↓
Generated: 0 posts
↓
Published: 0 posts
Conversion Rate: 0%

### Anime News Network (Anime News Daily, Manga Releases Tracker)
Fetched: 0 topics
↓
Unique: 0 topics
↓
Accepted: 0 topics
↓
Generated: 0 posts
↓
Published: 0 posts
Conversion Rate: 0%

[... аналогично для всех 22 RSS источников ...]

---

## LLM Quality Assessment

### Anime News Daily
- **A. Фактические ошибки:** 0 posts (0%)
- **B. Галлюцинации:** 0 posts (0%)
- **C. Плохой русский:** 0 posts (0%)
- **D. Слабый заголовок:** 0 posts (0%)
- **E. Повторяемость:** 0 posts (0%)
- **F. Непопадание в стиль:** 0 posts (0%)
- **G. Хороший пост:** 0 posts (0%)

[... аналогично для всех 14 каналов ...]

---

## Channel Rating (Go/Fix/Stop)

| # | Channel | Pipeline | Quality | Sources | Errors | Decision |
|---|---------|----------|---------|---------|--------|----------|
| 1 | Anime News Daily | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 2 | Manga Releases Tracker | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 3 | Gaming News Hub | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 4 | Movie & Series News | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 5 | AI News Daily | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 6 | Tech News Today | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 7 | Space & Science Daily | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 8 | Science Facts | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 9 | Auto News Daily | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 10 | Entertainment Memes | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 11 | Манга — новые главы | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 12 | Anime news | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 13 | Новости 📰 | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |
| 14 | AI Media Factory (VK) | 🟢/🟡/🔴 | высокое/среднее/низкое | хорошие/часть слабая/плохие | мало/много | GO/FIX/STOP |

**Decision Criteria:**
- **GO:** publish_success > 95%, approval_rate > 70%, errors < 5%
- **FIX:** publish_success 80-95%, approval_rate 50-70%, errors 5-15%
- **STOP:** publish_success < 80%, approval_rate < 50%, errors > 15%

---

## Stabilization Actions

### Sources to Remove (< 5% conversion)
- [ ] Source X: 2% conversion, 0 published
- [ ] Source Y: 0% conversion, constant errors

### Prompts to Improve (categories A-F > 30%)
- [ ] Channel Z: 40% weak headlines (category D)
- [ ] Channel W: 35% bad Russian (category C)

### Channels to Stop
- [ ] Channel X: publish_success 60%, too many errors

### Channels Ready for Scale (GO)
- [ ] Anime News Daily: publish_success 98%, high quality
- [ ] AI News Daily: publish_success 97%, high quality