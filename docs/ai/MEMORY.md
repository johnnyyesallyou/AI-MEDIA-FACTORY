# AI Media Factory

# AI Memory Architecture

Version: 1.0

Status: Active Development


---

# 1. Overview


AI Media Factory requires persistent project memory.


The AI assistant must understand:


- current project state
- completed features
- active tasks
- architectural decisions
- known problems



Memory prevents repeated work and incorrect architectural changes.



---

# 2. Memory Sources


The AI must read information in the following priority order:



1.

AI_CONTEXT.md


↓

2.

STATUS.md


↓

3.

TASK.md


↓

4.

PROJECT_CONTEXT.md


↓

5.

docs/



These files represent the current project knowledge.



---

# 3. AI_CONTEXT.md


Purpose:


Defines how AI should work with the project.



Contains:


- AI role
- development rules
- current objective
- workflow instructions



AI_CONTEXT.md has the highest priority during development sessions.



---

# 4. STATUS.md


Purpose:


Shows the actual implementation state.



Must contain:


- current phase
- completed tasks
- active tasks
- blocked tasks
- known issues
- next steps



STATUS.md must always reflect the real state of the project.



---

# 5. TASK.md


Purpose:


Contains the current development task.



Example:


Implement Writing Engine skeleton.



Before starting work AI must read TASK.md.



---

# 6. PROJECT_CONTEXT.md


Purpose:


Contains complete project knowledge.



Includes:


- architecture
- technology stack
- business rules
- workflows
- API contracts
- database design



This file changes rarely.



---

# 7. Documentation Memory


The docs folder contains detailed knowledge:



docs/

architecture/

backend/

ai/

business/

development/

deployment/

history/



Each technical area has its own documentation.



---

# 8. STATUS.md Update Rule


IMPORTANT:


After every completed development task AI MUST update STATUS.md.



Required updates:


Add completed feature:


Example:


[+] Writing Engine skeleton created



Update current phase:


Example:


Phase 3: Intelligence Layer



Update next steps:



Example:


Next:


- implement prompt builder
- add tests



---

# 9. Documentation Update Rule


Any significant code change requires documentation update.



Examples:



New API endpoint:


Update:

docs/backend/API_CONTRACT.md



New database table:


Update:

docs/backend/DATABASE.md



New AI agent:


Update:

docs/ai/AGENTS.md



Architecture change:


Update:

PROJECT_CONTEXT.md



---

# 10. Decision Memory


Important architectural decisions must be stored.



Location:



docs/history/DECISIONS.md



Example:


Decision:


Use PostgreSQL as primary database.



Reason:


Reliable relational storage and ecosystem.



---

# 11. Development Session Protocol


At the beginning of every AI session:



Step 1:


Read AI_CONTEXT.md



Step 2:


Read STATUS.md



Step 3:


Read TASK.md



Step 4:


Read PROJECT_CONTEXT.md



Step 5:


Inspect required documentation



Only after this AI may modify code.



---

# 12. Before Making Changes


AI must:


- understand existing architecture
- check current implementation
- avoid duplicate functionality
- avoid unnecessary refactoring
- preserve compatibility



---

# 13. After Making Changes


AI must:


1. Test changes

2. Report results

3. Update STATUS.md

4. Update documentation

5. Describe next step



---

# 14. Memory Rules


AI must remember:


- completed work
- failed attempts
- important decisions
- known limitations



AI must not:


- invent completed features
- ignore STATUS.md
- overwrite architecture without reason



---

# 15. Long Term Memory System


Future:


AI Memory Engine



Possible technologies:


- vector database
- embeddings
- semantic search



Purpose:


Allow AI agents to retrieve previous project knowledge automatically.



---

# End of AI Memory Architecture


==========================================================
SESSION MEMORY - appended 2026-08-12 (after Sprint 11)
==========================================================

HARD TECHNICAL CONSTRAINTS (violations caused real incidents):
1. Pollinations AI returns 0 bytes when URL > 200 chars.
   Always generate short EN prompts < 100 chars via ImagePromptEngine (Ollama mistral-nemo:12b).
   Fallback prompt: "anime scene, high quality".
2. Telegram sendPhoto requires requests.post(url, data=payload). json=payload gives 400 Bad Request.
3. Telegram caption max 1024 chars - truncate with "...".
4. SQLAlchemy reserves attribute "metadata". AssetORM uses extra_data = Column("metadata", JSON).
5. Ollama from container: http://host.docker.internal:11434 (extra_hosts host-gateway in docker-compose).
6. AssetManager: retry 3, backoff 2.0, timeout 120s; delete empty files; warn if < 1KB.
7. jobs/__init__.py must export all 8 jobs; runner.py imports them. Never delete job classes via patches.
8. Patch code only via Python scripts with py_compile validation; keep .backup files; show diff.
9. Assets not persistent - TODO add volume ./assets:/app/assets (Sprint 13).
10. Host is Windows PowerShell: no grep/xargs/head/tail (use Select-String/Select-Object),
    Invoke-WebRequest needs -UseBasicParsing, write files via single-quoted here-strings.

PRODUCTION FACTS:
- DB stats: 4 channels, 1345 content, 486 published, 673 approved, 2 assets, 2905 execution_logs.
- AI Anime News: telegram, chat_id=-1003901198631, workflow wf-simple, active.
- AI News RU (Test): chat_id=-1004324099845, inactive. AИ Новости: no creds, inactive.
- Test VK Channel: vk_group_id 240792540 (owner_id -240792540), 19 posts published.
- First Telegram photo post: message_id=191. VK 100% success; avg quality 84.1.

ARCHITECTURE DECISIONS (Sprint 11):
- PublishJob reuses draft_text (no LLM regen), dispatches by channel.platform.
- Publishers implement PublisherInterface in backend/automation/publishers/.
- Image pipeline: ImageJob -> ImagePromptEngine -> ImageEngine -> content.image_url -> sendPhoto.
- StaticFiles mounted at /assets in backend/main.py.

CURRENT TASK: Sprint 12 - Monitoring and Alerting (see TASK.md).


==========================================================
SPRINT 12 PROGRESS - 2026-08-12
==========================================================

MONITORING IMPLEMENTATION:
1. HealthCheckEngine (engines/monitoring/engine.py):
   - check_ollama(): GET /api/tags, returns models count
   - check_pollinations(): tiny URL test (64x64), validates size>0
   - check_telegram(): getMe with bot_token, returns username
   - check_vk(): status.get, validates HTTP 200
   - run_all(): returns {overall: ok/down, down_services: [], checks: []}

2. NotificationEngine (engines/notifications/engine.py):
   - send(text): uses TelegramPublisher.publish()
   - Returns message_id or None on failure

3. MonitoringJob (backend/automation/jobs/monitoring_job.py):
   - Reads ALERT_BOT_TOKEN, ALERT_CHAT_ID from env (security rule)
   - Runs HealthCheckEngine.run_all()
   - Queries execution_logs for SLA metrics (last 24h)
   - Sends alerts for down_services and success_rate<0.70
   - Redis dedup: key=alert:monitoring:{service}:{status}:{detail}, TTL=3600s
   - _should_alert(): compares stable dedup_value (without timestamp)
   - Returns: {health, sla, alerts_sent, alerts_suppressed, runtime_ms}

TESTING RESULTS:
- All 4 services healthy (ollama 8 models, pollinations 2KB, vk 200, telegram ok)
- Forced Ollama down (localhost:9999) -> alert sent to Telegram
- Second run -> alert suppressed (Redis dedup working)
- SLA: 27/27 success (100%) last 24h

NEXT: API endpoints + scheduler cron

==========================================================
SPRINT 12 STEP 3 COMPLETED - 2026-08-12
==========================================================

API ENDPOINTS CREATED:

1. GET /api/v1/monitoring/status
   - Returns JSON: {status, health, sla, runtime_ms}
   - health: {overall, down_services, checks[]}
   - sla: {window_hours, total, success, failed, success_rate}
   - Test result: 200 OK, overall=ok, success_rate=1.0, runtime=405ms

2. GET /api/v1/monitoring/metrics
   - Returns Prometheus-compatible plain text metrics
   - Format: metric_name{labels} value
   - Metrics: amf_health_status, amf_health_latency_ms, amf_sla_*, amf_alerts_*
   - Test result: 200 OK, all services healthy

3. POST /api/v1/monitoring/test-alert
   - Sends test alert to verify notification system
   - Requires ALERT_BOT_TOKEN and ALERT_CHAT_ID in env
   - Returns: {status: "sent", message_id: ...}

FILES:
- backend/app/api/v1/monitoring.py (created)
- backend/app/api/v1/router.py (updated - monitoring_router registered)

NEXT: Add MonitoringJob to scheduler (cron every 10 min)

==========================================================
SPRINT 12 COMPLETED - 2026-08-12
==========================================================

MONITORING SYSTEM FULLY IMPLEMENTED:

1. HealthCheckEngine (engines/monitoring/engine.py)
   - check_ollama(): GET /api/tags, returns models count
   - check_pollinations(): tiny URL test (64x64), validates size>0
   - check_telegram(): getMe with bot_token, returns username
   - check_vk(): status.get, validates HTTP 200
   - run_all(): returns {overall: ok/down, down_services: [], checks: []}
   - Architecture: NO database access (pure HTTP)

2. NotificationEngine (engines/notifications/engine.py)
   - send(text): uses TelegramPublisher.publish()
   - Returns message_id or None on failure
   - Credentials: ALERT_BOT_TOKEN, ALERT_CHAT_ID from env (security rule)

3. MonitoringJob (backend/automation/jobs/monitoring_job.py)
   - Runs HealthCheckEngine.run_all()
   - Queries execution_logs for SLA metrics (last 24h)
   - Sends alerts for down_services and success_rate<0.70
   - Redis dedup: key=alert:monitoring:{service}:{status}:{detail}, TTL=3600s
   - _should_alert(): compares stable dedup_value (without timestamp)
   - Returns: {health, sla, alerts_sent, alerts_suppressed, runtime_ms}

4. API Endpoints (backend/app/api/v1/monitoring.py)
   - GET /api/v1/monitoring/status - JSON with health + SLA
   - GET /api/v1/monitoring/metrics - Prometheus format
   - POST /api/v1/monitoring/test-alert - send test alert
   - Router registered in backend/app/api/v1/router.py

5. Scheduler Integration (backend/automation/scheduler.py)
   - MonitoringJob registered in APScheduler (cron every 10 min)
   - 4 jobs total: monitoring_job + 3 channel automations
   - Manual test confirms: monitoring_job: Monitoring (health + SLA)
   - asyncio.create_task() in main.py lifespan

CRITICAL FIXES (do not repeat):
1. Dedup logic: compare stable dedup_value (service:status:detail), NOT full message with timestamp
2. File creation: use Python inside container to avoid CRLF/indentation issues
3. Secrets: ALERT_BOT_TOKEN, ALERT_CHAT_ID from env ONLY (never in code)
4. Redis dedup: TTL 1 hour, key format alert:monitoring:{key}

TESTING RESULTS:
- All 4 services healthy (ollama 8 models, pollinations 2KB, vk 200, telegram ok)
- Manual scheduler test: 4 jobs registered successfully
- MonitoringJob execution: health ok, SLA 100%, alerts_sent=0
- API endpoints: /status returns JSON, /metrics returns Prometheus format

NEXT: Sprint 13 - ComfyUI Integration (local Flux/SDXL, ImageValidator, volume for assets)

==========================================================
SPRINT 12 COMPLETED - 2026-08-12
==========================================================

MONITORING SYSTEM FULLY IMPLEMENTED:

1. HealthCheckEngine (engines/monitoring/engine.py)
   - check_ollama(): GET /api/tags, returns models count
   - check_pollinations(): tiny URL test, validates size>0
   - check_telegram(): getMe with bot_token
   - check_vk(): status.get, validates HTTP 200
   - run_all(): returns {overall, down_services, checks}
   - Architecture: NO database access (pure HTTP)

2. NotificationEngine (engines/notifications/engine.py)
   - send(text): uses TelegramPublisher.publish()
   - Returns message_id or None on failure
   - Credentials: ALERT_BOT_TOKEN, ALERT_CHAT_ID from env

3. MonitoringJob (backend/automation/jobs/monitoring_job.py)
   - Runs HealthCheckEngine.run_all()
   - Queries execution_logs for SLA metrics (last 24h)
   - Sends alerts for down_services and success_rate<0.70
   - Redis dedup: key=alert:monitoring:{service}:{status}, TTL=3600s
   - _should_alert(): compares stable dedup_value (without timestamp)

4. API Endpoints (backend/app/api/v1/monitoring.py)
   - GET /api/v1/monitoring/status - JSON with health + SLA
   - GET /api/v1/monitoring/metrics - Prometheus format
   - POST /api/v1/monitoring/test-alert - send test alert

5. Scheduler Integration (backend/automation/scheduler.py)
   - MonitoringJob registered in APScheduler (cron every 10 min)
   - 4 jobs total: monitoring + 3 channel automations

CRITICAL FIXES (do not repeat):
1. Dedup logic: compare stable dedup_value, NOT full message with timestamp
2. File creation: use Python inside container to avoid CRLF/indentation issues
3. Secrets: ALERT_BOT_TOKEN, ALERT_CHAT_ID from env ONLY
4. Redis dedup: TTL 1 hour, key format alert:monitoring:{key}

NEXT: Sprint 13 - ComfyUI Integration (local Flux/SDXL, ImageValidator, A/B testing)

==========================================================
SPRINT 13 COMPLETED - 2026-08-12
==========================================================

COMFYUI INTEGRATION FULLY IMPLEMENTED:

1. Volume Persistence (./assets:/app/assets)
   - Docker volume для сгенерированных изображений
   - Assets переживают 'docker compose down -v'
   - Проверено: папка /app/assets видна в контейнере

2. ComfyUI Infrastructure (docker-compose.comfyui.yml)
   - GPU support (NVIDIA)
   - Volumes: comfyui_data, models, output, input
   - Network: amf_network (shared with backend)
   - Requires manual model download (Flux ~12GB)

3. ComfyUIEngine (engines/comfyui/engine.py)
   - base_url: http://comfyui:8188
   - Methods: _check_health(), _queue_prompt(), _wait_for_completion(), _get_output_image()
   - generate(): полный workflow txt2img (KSampler, CLIPTextEncode, VAEDecode, SaveImage)
   - **FALLBACK**: если ComfyUI недоступен → автоматически использует Pollinations AI
   - Тест: fallback работает корректно (Pollinations URL возвращается)

4. ImageValidatorEngine (engines/image_validator/engine.py)
   - Uses Ollama Vision model (llava:7b)
   - Evaluates: quality_score, prompt_match, aesthetic_score (0-100 each)
   - overall_score = quality*0.4 + prompt_match*0.3 + aesthetic*0.3
   - QUALITY_THRESHOLD = 70 (passed/failed)
   - Accepts: image_path OR image_url
   - Returns: {quality_score, prompt_match, aesthetic_score, overall_score, passed, feedback}

5. ABTestEngine (engines/ab_test/engine.py)
   - Generates N variants (different seeds)
   - Validates each via ImageValidator
   - Selects best by overall_score
   - generate_and_select(): полный цикл генерация + выбор
   - Returns: {best_variant, all_variants, num_generated, num_passed, selection_reason}

CRITICAL DECISIONS:
1. ComfyUI fallback: если контейнер не запущен → Pollinations (graceful degradation)
2. Vision model: llava:7b для оценки качества (lightweight, fast)
3. A/B testing: разные seeds для вариативности, выбор по overall_score
4. Quality threshold: 70/100 (balance между качеством и количеством)

FILES CREATED:
- docker-compose.comfyui.yml
- comfyui/models/{checkpoints,loras}
- comfyui/{output,input}
- engines/comfyui/engine.py
- engines/image_validator/engine.py
- engines/ab_test/engine.py
- Volume: ./assets:/app/assets in docker-compose.yml

TESTING RESULTS:
- ComfyUI Engine: fallback работает (Pollinations URL)
- ImageValidator: не тестировался (требует llava:7b модель в Ollama)
- ABTestEngine: создан, готов к использованию

NEXT: Sprint 14 - YouTube Shorts Publisher (Data API v3, OAuth2, vertical 9:16)

==========================================================
SPRINT 13 COMPLETED - 2026-08-13
==========================================================

INTEGRATION TEST RESULTS:
✅ Image generation: Pollinations fallback (18.10s)
✅ ImageValidator llava:7b: score=85/100 (25.84s)
  - Quality: 85, Prompt Match: 90, Aesthetic: 80
  - Feedback: "The image displays a high level of technical quality..."
✅ VK publication: text-only (post_id=35)
  - URL: https://vk.com/wall-240792540_35
⚠️ Telegram: skipped (no credentials for channel)

KNOWN LIMITATIONS:
1. VK error 27: community tokens cannot upload photos
   - Workaround: text-only fallback
   - Full solution: use user token (OAuth2 flow, not community token)

2. ComfyUI not deployed yet
   - docker-compose.comfyui.yml ready
   - Requires manual model download (Flux ~12GB)
   - Fallback to Pollinations works perfectly

3. Telegram channel search
   - Test used channel_id from post, but channel has no credentials
   - Need to verify is_connected=True filter logic

NEXT: Sprint 14 - YouTube Shorts (Data API v3, OAuth2, 9:16 video)

==========================================================
SPRINT 13.1 COMPLETED - 2026-08-13
==========================================================

IMAGE DOMAIN STABILIZATION:

1. AssetManager Integration ✅
   - ImageJob теперь использует AssetManager для всех картинок
   - Fallback: если AssetManager упал → внешний URL
   - 57 assets в БД (было 2)

2. File Format Detection ✅
   - Определение формата по Content-Type (PNG/JPEG/WebP)
   - Правильное расширение в filename
   - Маппинг: image/jpeg→jpg, image/png→png, image/webp→webp

3. DB-Level Filtering ✅
   - SQL WHERE вместо Python filter
   - ImageJob обрабатывает ВСЕ posts без image_url
   - Idempotency подтверждена (3 runs → 1 asset)

4. Channel Parameters ✅
   - style_profile и platform из ChannelORM
   - Маппинг: minimal→minimal, anime→anime, realistic→realistic
   - Убран хардкод

CRITICAL FIXES:
1. AssetManager bypass: добавлен в ImageJob pipeline
2. .png для JPEG: определение формата по Content-Type
3. Pagination: SQL WHERE вместо Python filter
4. Hardcoded params: чтение из ChannelORM

NEXT: Sprint 14 - Image Acquisition Pipeline
- Source-first подход (source image → search → AI fallback)
- Image Profile (News/Anime Episodes/Anime General)
- Relevance Validator (entity matching)
- Image Resolver chain

==========================================================
SPRINT 14 STARTED - 2026-08-13
==========================================================

IMAGE ACQUISITION PIPELINE:

Step 1: image_profile в ChannelORM ✅
- Добавлено поле image_profile (JSON) в ChannelORM
- SQL миграция через psql (обход SQLAlchemy FK issues)
- 3 канала настроены с правильными profiles:
  * АИ Новости: source_first, news
  * AI Anime News: source_first, anime
  * Test VK Channel: source_first, anime

CRITICAL FIX:
- IndentationError: создан файл через Python внутри контейнера
  (избегаем проблем с PowerShell encoding + BOM)
- Код:
  ```python
  content = """..."""  # без кириллицы в комментариях
  f = pathlib.Path('/app/core/models/channel_orm.py')
  f.write_text(content, encoding='utf-8', newline='\n')
NEXT: Step 2 - SourceImageResolver (og:image extraction)

==========================================================
SPRINT 15 STEP 4 COMPLETED - 2026-08-13
==========================================================

MANGA CHAPTER RELEASE PIPELINE:

1. Source Adapter Framework ✅
   - BaseSourceAdapter + SourceItem (dataclass)
   - ReMangaAdapter (API endpoint /api/titles/last-chapters/)
   - Stateless adapters, no DB access

2. ChapterDetector ✅
   - Группировка по (source, title_id)
   - MAX chapter для определения новизны
   - manga_source_states таблица
   - Idempotent: 2-й запуск = 0 новых

3. MangaResearchJob ✅
   - Оркестратор: adapters → detector → ContentORM
   - Канал создаётся через SQL (обход SQLAlchemy FK на channel_profiles)
   - Метаданные в source_text как JSON

KNOWN ISSUES:
- URL artifact "<29.04.2026>" в некоторых dir (Shark/Акула)
- Channel creation через ORM вызывает FK errors из-за channel_profiles
- Решение: SQL для создания каналов, ORM только для чтения

NEXT: Step 5 - ImageResolver (source-first для обложек через AssetManager)

==========================================================
SPRINT 15 COMPLETED - 2026-08-13
==========================================================

MANGA CHAPTER RELEASE PIPELINE - FULLY WORKING:

Architecture:
  Scheduler (every 30 min)
       ↓
  MangaPipelineJob
       ↓
  ├── MangaResearchJob (ReManga API, /api/titles/last-chapters/)
  ├── MangaImageResolver (source-first cover download via AssetManager)
  └── MangaPublishJob (description + genres + short URL + hashtags)
       ↓
  Telegram @manga_new_chapters

Channel:
  Name: Манга — новые главы
  ID: manga-channel-001
  Chat ID: -1004327209979
  Bot: @openclavv_ai_bot

Database:
  manga_source_states - deduplication (source + title_id unique)
  content.source_text - JSON с metadata (description, genres, cover_url)
  assets - локальные обложки (/assets/2026/08/*.webp)

Post format:
  📚 {title_name}
  🌐 {title_name_en}

  {description (smart truncate под 1024 caption limit)}

  📖 Глава {number}

  🔗 Читать: https://tinyurl.com/{hash}

  #Манга #Жанр1 #Жанр2 ...

Key learnings:
- SQLAlchemy FK issues: обходим через SQL для создания каналов
- PowerShell encoding: Set-Content -Encoding ASCII (не UTF8) для Python файлов
- Telegram multipart: для локальных файлов используется files= вместо data=
- ReManga API: last-chapters работает без auth, search требует auth
- TinyURL: работает без ключа (81→28 chars)
- Telegram caption limit: 1024 символов (smart truncate по словам)
- BOM: PowerShell -Encoding UTF8 добавляет BOM, используйте ASCII или Python

NEXT SPRINTS (идеи):
- Sprint 16: MangaDex API как backup для enrichment
- Sprint 17: ZazaZa через Playwright
- Sprint 18: Image Acquisition Pipeline (source-first для обычных новостей)
- Sprint 19: Rate limiting для Telegram (flood control)
- Sprint 20: Альтернативные источники (MangaLib, Shikimori, MyAnimeList)

==========================================================
SPRINT 17 COMPLETED - 2026-08-13
==========================================================

IMAGE ACQUISITION PIPELINE (SOURCE-FIRST FOR NEWS):

Architecture:
  SourceImageResolver
       ↓
  Extract og:image from source_url (BeautifulSoup)
       ↓
  AssetManager.save_from_url()
       ↓
  Update content.image_url
       ↓
  Telegram publish with image

Results:
  - 587/604 news items with covers (97% success)
  - 17 failed (403 Forbidden: habr.com anti-bot, openai.com)
  - Priority: og:image > twitter:image > article_img > favicon

Key learnings:
- BeautifulSoup отлично парсит og:image из HTML
- habr.com иногда возвращает 403 (anti-bot) — нужно fallback
- openai.com полностью блокирует ботов
- Relative URLs нужно резолвить через urljoin
- Tracker pixels (1x1, beacon) нужно фильтровать

NEXT: Sprint 18 (Telegram + Telegraph pages)

==========================================================
SPRINT 18 COMPLETED - 2026-08-13
==========================================================

TELEGRAPH INTEGRATION + CHAPTER PREVIEW:

Architecture:
  MangaPublishJob
       ↓
  ReMangaAdapter.fetch_first_chapter_preview(slug, 5)
       ↓ (first_chapter → /api/titles/chapters/{id}/ → pages[0..4][0].link)
  TelegraphPublisher.publish_manga_page(preview_pages)
       ↓
  Telegraph page: cover + description + preview + links
       ↓
  Telegram post with Telegraph URL

Key learnings:
- ReManga API: /api/titles/{slug}/ → content.first_chapter.id
- Pages structure: [[{id, link, height, width}], ...] (list of lists)
- ReManga CDN: страницы доступны БЕЗ Referer в Telegraph (img тег)
- Telegraph upload заблокирован (400) → используем внешние URL
- manga_title_slug сохраняется в metadata для preview
- Preview = легально (как "Look Inside" в книжных)

Files:
- engines/telegraph/publisher.py (TelegraphPublisher)
- engines/source_adapters/remanga_adapter.py (fetch_first_chapter_preview)
- backend/automation/jobs/manga_publish_job.py (v3 с preview)

NEXT: Sprint 19 (Хентай-канал / MangaDex enrichment / Telegram improvements)

==========================================================
SPRINT 19 COMPLETED - 2026-08-13
==========================================================

TELEGRAM IMPROVEMENTS + RU-ONLY:

Results:
- 107 RU posts published (101 ReManga + 6 MangaDex)
- 145 EN posts marked as skipped_en
- Inline buttons in all posts
- Rate limiter: 24 posts/min (no flood bans)
- Full descriptions + hashtags from API

Key learnings:
- All free image hosting blocks container IP (catbox, 0x0, Telegraph upload)
- Preview pages require self-hosted proxy server
- RU-only filter: re.search(r"[а-яА-ЯёЁ]", title)
- MangaDex batch API returns partial results → use individual requests

Files:
- engines/telegram/rate_limiter.py
- engines/telegram/publisher.py (v2 with inline buttons)
- backend/automation/jobs/manga_publish_job.py (RU filter)

NEXT: Sprint 20 (Proxy server for preview pages / HentaiChan / ZazaZa)

==========================================================
SPRINT 20 COMPLETED - 2026-08-13
==========================================================

CHANNEL CONTENT PROFILES:

Architecture:
  ChannelORM.content_profile (JSONB)
       ↓
  resolve_channel_profile(channel)
       ↓
  {theme, content_type, image_policy, publishing_policy, ...}
       ↓
  Pipeline reads profile → behaves differently per channel

Profiles:
  - ai_news: og:image → AI fallback, no RU filter
  - anime_news: anime_visual, anime style
  - manga_releases: manga_cover, RU-only, Telegraph, inline buttons

Key learnings:
- Deep-merge: stored config overrides defaults
- guess_profile_key() by channel name (fallback)
- JSONB column for flexible config storage
- One Research layer → different Publishing rules

Files:
- engines/channel_profiles.py (profile resolver)
- core/models/channel_orm.py (content_profile JSONB)

NEXT: Sprint 21 (Smart Image Acquisition - source first, AI fallback)

==========================================================
SPRINT 21 COMPLETED - 2026-08-13
==========================================================

SMART IMAGE ACQUISITION:

Architecture:
  Content → SmartImageResolver → найдена?
                                    │
              ┌─────────────────────┴─────────────────────┐
              ↓ YES                                       ↓ NO
        AssetManager                              AI Generation
              ↓                                         ↓
        SmartImageResult                        ImageValidator
              ↓                                         ↓
        {url, source, confidence, type}          AssetManager

Key learnings:
- Приоритеты зависят от channel_profile.content_type
- News: og_image → twitter:image → article_img → AI fallback
- Manga: manga_cover → chapter_preview → NO AI fallback
- Anime: anime_visual → source_img → AI fallback
- Structured return: {asset_id, url, source, confidence, type}

Files:
- engines/smart_image_resolver.py (SmartImageResolver)
- engines/image_validator.py (ImageValidator)
- backend/automation/jobs/smart_image_acquisition_job.py

Results:
- News test: og_image, confidence=0.85
- Manga test: manga_cover, confidence=0.95
- Success rate: 100% for items with available sources

NEXT: Sprint 22 (Manga Sources Expansion - ZazaZa/ReadManga adapters)

==========================================================
SPRINT 22 COMPLETED - 2026-08-17
==========================================================

MANGA SOURCES EXPANSION:

Architecture:
  MangaRegistry (единая точка доступа)
       ↓
  ┌────┴────┐
  ↓         ↓
ReManga   MangaDex
  ↓         ↓
BaseMangaAdapter (единый интерфейс)
       ↓
  MangaItem (единая структура)

Key learnings:
- BaseMangaAdapter: абстрактный класс для всех manga sources
- MangaItem: dataclass с общими полями (title, chapter, url, source, ...)
- MangaRegistry: fetch_from(), fetch_all(), fetch_with_dedup()
- Дедупликация по (source, external_id) предотвращает повторы
- Каждый адаптер реализует fetch_latest_chapters_manga() -> List[MangaItem]

Files:
- engines/source_adapters/base_manga_adapter.py (BaseMangaAdapter, MangaItem)
- engines/source_adapters/manga_registry.py (MangaRegistry)
- engines/source_adapters/remanga_adapter.py (рефакторинг)
- engines/source_adapters/mangadex_adapter.py (рефакторинг)
- backend/automation/jobs/manga_research_job.py (использует registry)

Results:
- 2 sources: remanga + mangadex
- Unified interface for all manga adapters
- Deduplication works (5+5=10 unique items)
- MangaResearchJob uses MangaRegistry.fetch_with_dedup()

NEXT: Sprint 23 (Manga Knowledge Layer - deduplication по названию манги)

==========================================================
SPRINT 22 COMPLETED - 2026-08-17
==========================================================

MANGA SOURCES EXPANSION:

Results:
- 40 new chapters loaded via MangaRegistry
- 2 sources: remanga + mangadex
- Automatic deduplication by (source, external_id)
- Channel profile defines which sources to use
- BaseMangaAdapter + MangaItem unified interface

Architecture:
  MangaRegistry.fetch_with_dedup(limit, sources)
       ↓
  ┌────┴────┐
  ↓         ↓
ReManga   MangaDex  (оба наследуют BaseMangaAdapter)
       ↓
  MangaItem → SourceItem → ChapterDetector → ContentORM

Files:
- engines/source_adapters/base_manga_adapter.py (BaseMangaAdapter, MangaItem)
- engines/source_adapters/manga_registry.py (MangaRegistry)
- engines/source_adapters/remanga_adapter.py (рефакторинг)
- engines/source_adapters/mangadex_adapter.py (рефакторинг)
- backend/automation/jobs/manga_research_job.py (использует registry)
- core/models/channel_orm.py (content_profile JSONB)

NEXT: Sprint 23 (Manga Knowledge Layer - deduplication по названию манги)

==========================================================
SPRINT 23 COMPLETED - 2026-08-17
==========================================================

MANGA KNOWLEDGE LAYER:

Architecture:
  MangaItem → TitleNormalizer.normalize() → canonical_title
                         ↓
              find_or_create_title(cache) → MangaTitle
                         ↓
              find_or_create_chapter → MangaChapter

Key learnings:
- TitleNormalizer: lowercase + remove punctuation + RU->EN mapping
- "Ван Пис" = "ONE PIECE" = "Ван-Пис!" = "one piece"
- In-memory seen_chapters Set предотвращает дубликаты в батче
- SELECT → INSERT + try/except IntegrityError для атомарной защиты
- db.flush() без commit сохраняет сессию активной
- Передача title_id вместо title избегает DetachedInstanceError

Files:
- core/models/manga_knowledge.py (MangaTitle, MangaChapter)
- engines/title_normalizer.py
- engines/manga_knowledge_engine.py

Results:
- 20 items → 14 unique titles, 19 unique chapters
- Deduplication works (second run: 0 new, 20 existing)
- In-memory tracking: 1 duplicate caught in batch
- Protection against race conditions via IntegrityError

NEXT: Integrate MangaKnowledgeEngine into MangaResearchJob

==========================================================
SPRINT 24.1 + 24.2 COMPLETED - 2026-08-17
==========================================================

KNOWLEDGE INTEGRATION + E2E VALIDATION:

Architecture:
  MangaRegistry.fetch_all() → [MangaItem list]
                    ↓
  MangaKnowledgeEngine.process_items(db, items)
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
  MangaTitle              MangaChapter
  (find_or_create)        (find_or_create + IntegrityError)
                    ↓
  MangaResearchJob (единая сессия)
                    ↓
  ContentORM (manga_chapter_id → MangaChapter)

Key learnings:
- Единая сессия для Knowledge Layer + ContentORM (избегаем DetachedInstanceError)
- Knowledge Engine принимает db параметр, не создаёт свою сессию
- Возвращаем List[str] ID вместо List[MangaChapter] объектов
- db.query().filter(MangaChapter.id.in_(ids)) загружает объекты в текущей сессии
- Commit делается один раз в конце, в MangaResearchJob

Results:
- Run #1: 19 new chapters, 18 new titles, 0 existing
- Run #2: 0 new chapters, 0 new titles, 20 existing (дедупликация!)
- DB: 18 manga_titles, 19 manga_chapters, 19 content with manga_chapter_id
- Knowledge Layer = единый источник истины

Files:
- engines/manga_knowledge_engine.py (process_items(db, items))
- backend/automation/jobs/manga_research_job.py (единая сессия)
- core/models/content_orm.py (manga_chapter_id)

NEXT: Sprint 25 (Multi-Channel Publishing with different profiles)

==========================================================
SPRINT 25.1 COMPLETED - 2026-08-17
==========================================================

KNOWLEDGE-AWARE PUBLISHING:

Architecture:
  ContentORM (manga_chapter_id)
         ↓
  MangaChapter → MangaTitle (enrichment)
         ↓
  Telegraph → Telegram (inline buttons)

Key learnings:
- Publishing через Knowledge Layer (manga_chapter_id)
- Grouping по manga_title_id через MangaChapter (не metadata)
- Enrichment из MangaTitle (description, genres, cover_url)
- catbox.moe блокирует контейнерный IP → убран retry
- MangaDex UUID не имеют slug в ReManga → обогащение только для ReManga slug

Results:
- 3 posts published via Knowledge Layer
- Enriched: 10/18 titles (MangaDex UUID skipped)
- DB: 3 content with manga_chapter_id (Knowledge-aware)
- RU-only filter works via channel_profile

Files:
- backend/automation/jobs/manga_publish_job.py (v4)
- engines/preview_resolver.py (без catbox)

NEXT: Sprint 25.2 (Multi-Channel Publishing with different profiles)

==========================================================
SPRINT 25.2 COMPLETED - 2026-08-17
==========================================================

MULTI-CHANNEL PUBLISHING:

Architecture:
  Research → Knowledge Layer → Enrichment
                    ↓
            PublicationImageResolver (policy-driven)
                    ↓
              Publication (text + image + buttons)
                    ↓
        PlatformPublisher.publish(publication)
                    ↓
              Telegram / VK / ...

Key learnings:
- Publishing Layer отделяет "ЧТО публиковать" от "КАК доставить"
- Publication — нормализованный объект для любой платформы
- BasePublisher — контракт платформы
- PublicationImageResolver использует channel_profile для выбора изображения
- html.unescape() исправляет &quot; в заголовках
- Job — оркестратор, не носитель логики

Files:
- engines/publishing/publication.py
- engines/publishing/base_publisher.py
- engines/publishing/telegram_publisher_adapter.py
- engines/publishing/image_resolver.py
- engines/channel_profiles.py (source_policy, enrichment_policy, formatting)
- backend/automation/jobs/manga_publish_job.py (v5)

Results:
- 3 test publications via Publishing Layer
- RU-only filter works
- &quot; fixed via unescape
- Image policy: manga cover from Knowledge Layer
- Job is pure orchestrator

NEXT: Sprint 26 (Cross-source Enrichment)

==========================================================
SPRINT 26 COMPLETED - 2026-08-18
==========================================================

CROSS-SOURCE ENRICHMENT:

Architecture:
  MangaItem (title_external_id)
       ↓
  MangaKnowledgeEngine
       ↓
  MangaTitle (title_slug = slug для ReManga, UUID для MangaDex)
       ↓
  CrossSourceEnricher.fetch_source_data()
       ↓
  sources_data = {remanga: {...}, mangadex: {...}}
       ↓
  merge() → description (RU priority) + genres (union) + cover

Key learnings:
- title_external_id отделяет ID тайтла от ID главы
- title_slug содержит: slug для ReManga, UUID для MangaDex
- Формат UUID (36 символов, 4 дефиса) определяет MangaDex
- Description merge: приоритет RU, затем самая длинная
- Genres merge: union уникальных
- Auto-enrichment в ResearchJob для новых тайтлов

Files:
- engines/source_adapters/base_manga_adapter.py (title_external_id)
- engines/cross_source_enricher.py
- engines/manga_knowledge_engine.py (использует title_external_id)
- engines/source_adapters/remanga_adapter.py (title_external_id)
- engines/source_adapters/mangadex_adapter.py (title_external_id)
- backend/automation/jobs/manga_enrichment_job.py
- backend/automation/jobs/manga_research_job.py (auto-enrichment)

Results:
- 8 MangaDex titles enriched via MangaDex API
- 10 ReManga titles already had descriptions
- All 18 titles now have description + genres
- Source detection by slug format (UUID = MangaDex, string = ReManga)
- Auto-enrichment works in ResearchJob

NEXT: Sprint 27 (Image Intelligence - AI fallback for news, validation)

==========================================================
SPRINT 26 COMPLETED - 2026-08-18
==========================================================

CROSS-SOURCE ENRICHMENT:

Architecture:
  MangaItem (title_external_id)
       ↓
  MangaKnowledgeEngine
       ↓
  MangaTitle (title_slug = slug для ReManga, UUID для MangaDex)
       ↓
  CrossSourceEnricher.fetch_source_data()
       ↓
  sources_data = {remanga: {...}, mangadex: {...}}
       ↓
  merge() → description (RU priority) + genres (union) + cover

Key learnings:
- title_external_id отделяет ID тайтла от ID главы
- title_slug содержит: slug для ReManga, UUID для MangaDex
- Формат UUID (36 символов, 4 дефиса) определяет MangaDex
- Description merge: приоритет RU, затем самая длинная
- Genres merge: union уникальных
- Auto-enrichment в ResearchJob для новых тайтлов

Files:
- engines/source_adapters/base_manga_adapter.py (title_external_id)
- engines/cross_source_enricher.py
- engines/manga_knowledge_engine.py (использует title_external_id)
- engines/source_adapters/remanga_adapter.py (title_external_id)
- engines/source_adapters/mangadex_adapter.py (title_external_id)
- backend/automation/jobs/manga_enrichment_job.py
- backend/automation/jobs/manga_research_job.py (auto-enrichment)

Results:
- 14 new titles created in Knowledge Layer
- All 14 automatically enriched via API
- ReManga titles: slug → description + genres
- MangaDex titles: UUID → description + genres + cover
- Auto-enrichment works in ResearchJob
- Source detection by slug format (UUID = MangaDex, string = ReManga)

NEXT: Sprint 27 (Image Intelligence - AI fallback for news, validation)

==========================================================
SPRINT 27 COMPLETED - 2026-08-18
==========================================================

IMAGE INTELLIGENCE:

Architecture:
  PublicationImageResolver.resolve(content, channel)
       ↓
  content_type → candidates chain
       ↓
  is_valid_image_url() (status 200 + content-type image)
       ↓
  Referer fallback (MangaDex strict CDN)
       ↓
  first valid URL

Key learnings:
- MangaDex covers требуют Referer header (без него 404)
- ReManga covers работают без Referer
- Валидация: status 200 + content-type image
- Битые URL (404) отклоняются
- HTML-entities в description фиксированы через unescape()
- Валидация не блокирует реальные публикации

Files:
- backend/automation/jobs/manga_publish_job.py (unescape)
- engines/publishing/image_resolver.py (v3)

Results:
- Validation rejects broken URLs
- Validation accepts real covers from DB
- MangaDex Referer fallback works
- Publishing with validation: 3 posts, 0 failed

NEXT: Sprint 28 (VK Publishing + Unified Publisher)

==========================================================
SPRINT 28 COMPLETED - 2026-08-18
==========================================================

VK PUBLISHING + UNIFIED PUBLISHER:

Architecture:
  MangaPublishJob
       ↓
  get_publisher_for_channel(channel)
       ↓
  ┌──────────────┬──────────────┐
  ↓              ↓              ↓
Telegram      VK          (future platforms)
Publisher   Publisher
       ↓              ↓
  Publication (единый объект)

Key learnings:
- VK не имеет inline-кнопок → конвертируем в ссылки в тексте
- VK фото загрузка: getWallUploadServer → upload → saveWallPhoto
- MangaDex covers требуют Referer (используем тот же UA как для валидации)
- Factory выбирает publisher по channel.platform
- Research/Knowledge Layer НЕ знает о платформах
- Один Publication работает для обеих платформ

Files:
- engines/publishing/vk_publisher.py
- engines/publishing/factory.py
- engines/publishing/__init__.py
- backend/automation/jobs/manga_publish_job.py (использует factory)

Results:
- VK post created: https://vk.com/wall-240792540_46
- Publisher platform: vk
- Unified Publisher works
- Factory selects publisher automatically

NEXT: Sprint 29 (Bulk Publishing - production validation)

==========================================================
SPRINT 29 COMPLETED - 2026-08-18
==========================================================

BULK PUBLISHING + PRODUCTION VALIDATION:

Results:
- 14 posts published (все с manga_chapter_id)
- 5 posts skipped_en (правильный RU-only фильтр)
- 3 posts failed (SSL ошибка сети, не архитектура)
- 2 posts research (ORPHAN без manga_chapter_id)
- 10/10 posts без issues (все поля заполнены)
- Идемпотентность: Run #2 = 0 published ✅

Quality (10 checked):
- title_name: 10/10 ✅
- chapter_number: 10/10 ✅
- description: 10/10 ✅
- genres: 10/10 (1-12 жанров) ✅
- cover: 10/10 ✅
- source_url: 10/10 ✅

Known issues (network):
- SSL errors accessing api.telegra.ph and tinyurl.com
- 3 failed "No image resolved" (image exists, Telegraph failed)
- Fix: configure proxy or update SSL certs

Idempotency confirmed:
  Run #1: published=3, failed=0
  Run #2: published=0, message='No items'

NEXT: Sprint 30 (New manga sources - ZazaZa / ReadManga / MangaLib)

==========================================================
SPRINT 30 COMPLETED - 2026-08-18
==========================================================

MANGA SOURCES EXPANSION (ReadManga):

Architecture:
  MangaRegistry (3 sources)
       ↓
  ┌──────────────┬──────────────┬──────────────┐
  ↓              ↓              ↓              ↓
ReManga    MangaDex      ReadManga     (future)
       ↓              ↓              ↓
  MangaKnowledgeEngine (cross-source dedup)
       ↓
  MangaTitle + MangaChapter
       ↓
  CrossSourceEnricher
       ↓
  MangaPublishJob → Publication → Telegram/VK

Key learnings:
- ReadManga HTML parsing через BeautifulSoup
- Селектор: div.feed-latest-updates > a.chapter-link
- URL паттерн: /{slug}/vol{N}/{chapter}
- Lazy-loaded images: data-src attribute
- Parent card: feed-latest-updates-item (не footer)
- BaseMangaAdapter нуждается в self.logger и fetch_latest_chapters_manga()
- ReadManga slug ≠ ReManga slug (разные форматы)

Files:
- engines/source_adapters/base_manga_adapter.py (logger + fetch_latest_chapters_manga)
- engines/source_adapters/readmanga_adapter.py (новый)
- engines/source_adapters/manga_registry.py (readmanga зарегистрирован)

Results:
- 3 sources: remanga + mangadex + readmanga
- ResearchJob: 30 chapters, 26 titles
- Breakdown: mangadex: 10, readmanga: 10, remanga: 10
- Bulk publish: all published
- Idempotency: 0 on second run ✅

Known issues:
- CrossSourceEnricher tries to enrich ReadManga via ReManga API (404)
- Different slug formats: ReadManga uses IDs, ReManga uses URL-safe slugs

NEXT: Sprint 31 (Anime Channel Profile + publishing)

==========================================================
SPRINT 30.5 COMPLETED - 2026-08-18
==========================================================

ENRICHMENT CONSISTENCY:

Problem:
  CrossSourceEnricher tried to enrich ReadManga titles via ReManga API
  ReadManga slug (34223) → ReManga API → 404

Solution:
  Made CrossSourceEnricher source-aware:
  - Determines source by slug format
  - ReadManga slug: numeric ID or underscore translit
  - ReManga slug: URL-safe without underscore
  - Enriches each title only from its source

Architecture:
  MangaTitle
       ↓
  _get_available_sources()
       ↓
  ┌──────────────┬──────────────┬──────────────┐
  ↓              ↓              ↓              ↓
ReManga    MangaDex      ReadManga     (skip)
       ↓              ↓              ↓
  _enrich_from_source()
       ↓
  sources_data = {remanga: {...}, readmanga: {...}}
       ↓
  _merge_sources_data() (priority: ReManga > MangaDex > ReadManga)
       ↓
  description / genres / cover

Files:
- engines/cross_source_enricher.py (source-aware)
- engines/source_adapters/readmanga_adapter.py (+ get_title_info)

Results:
- Before: 404 errors when enriching ReadManga titles
- After: 0 errors, all titles enriched correctly

NEXT: Sprint 31 (Anime Channel Profile)

==========================================================
SPRINT 30.5 FIX - 2026-08-18
==========================================================

TITLE REGEX FIX:

Problem:
  Title: "Сильнейшая служанка культа Небесного Демонаонлайн\n   - RM.me"
  Regex не убирал "онлайн\n   - RM.me" из-за newline

Solution:
  Добавлен re.DOTALL флаг для \s:
  - re.sub(r'\s*—\s*RM\.me.*$', '', title_text, flags=re.DOTALL)
  - re.sub(r'\s*онлайн.*$', '', title, flags=re.IGNORECASE | re.DOTALL)

Result:
  Title: "Сильнейшая служанка культа Небесного Демона"
  Clean, без суффиксов и newline

Files:
- engines/source_adapters/readmanga_adapter.py (re.DOTALL added)

==========================================================
SPRINT 30.5 COMPLETED (FINAL) - 2026-08-18
==========================================================

ENRICHMENT CONSISTENCY - ALL ISSUES FIXED:

Problems solved:
1. ✅ CrossSourceEnricher source-aware (определяет источник по slug формату)
2. ✅ ReadMangaAdapter.get_title_info() правильные селекторы
3. ✅ Title regex очищает префиксы "Манга/Манхва" и суффиксы "онлайн/RM.me"
4. ✅ MangaEnrichmentJob использует новый API enrich()
5. ✅ 26/26 тайтлов обогащены (100% coverage)
6. ✅ 0 ошибок 404

Title regex (final):
  re.sub(r'\s*—\s*RM\.me.*$', '', title_text, flags=re.DOTALL)
  re.sub(r'^(Манга|Манхва|Маньхуа|Комикс)\s+', '', title, flags=re.IGNORECASE)
  re.sub(r'\s*онлайн.*$', '', title, flags=re.IGNORECASE | re.DOTALL)
  re.sub(r'\s*\([^)]*\)\s*', '', title)

Results:
  Title: "Сильнейшая служанка культа Небесного Демона" (clean)
  Title: "Прогулка в другом мире" (clean, без "Манга")
  26/26 titles enriched with description + genres + cover

Architecture:
  MangaTitle (slug format determines source)
       ↓
  CrossSourceEnricher._get_available_sources()
       ↓
  ┌──────────────┬──────────────┬──────────────┐
  ↓              ↓              ↓              ↓
ReManga    MangaDex      ReadManga     (skip)
       ↓              ↓              ↓
  _enrich_from_source() (source-specific)
       ↓
  sources_data = {source: {description, genres, cover}}
       ↓
  _merge_sources_data() (priority: ReManga > MangaDex > ReadManga)
       ↓
  MangaTitle.description / genres / cover_url

Files:
- engines/cross_source_enricher.py (source-aware)
- engines/source_adapters/readmanga_adapter.py (correct selectors + clean titles)
- engines/source_adapters/base_manga_adapter.py (logger + fetch_latest_chapters_manga)
- backend/automation/jobs/manga_enrichment_job.py (новый API)
- backend/automation/jobs/manga_research_job.py (auto-enrichment)

NEXT: Sprint 31 (Anime Channel Profile)

==========================================================
SPRINT 31.1-31.4 COMPLETED - 2026-08-18
==========================================================

ANIME KNOWLEDGE LAYER:

Architecture:
  AniListAdapter (GraphQL API)
           ↓
  AnimeRegistry (единая точка доступа)
           ↓
  AnimeKnowledgeEngine.process_items(db, items)
           ↓
    ┌──────────────────────┬──────────────────────┐
    ↓                      ↓                      ↓
  AnimeTitle          AnimeEpisode          (deduplication)
           ↓
  AnimeResearchJob (единая сессия)
           ↓
  ContentORM (anime_episode_id → AnimeEpisode)

Key learnings:
- AniList GraphQL API работает без OAuth
- Единая сессия для Knowledge Layer + ContentORM
- AnimeKnowledgeEngine принимает db параметр
- Возвращаем List[str] ID вместо объектов
- db.query().filter(AnimeEpisode.id.in_(ids)) загружает объекты
- anime_episode_id связывает ContentORM с Knowledge Layer
- Идемпотентность работает (повторный запуск = 0 новых)

Files:
- engines/source_adapters/anilist_adapter.py
- engines/source_adapters/anime_registry.py
- core/models/anime_knowledge.py
- engines/anime_knowledge_engine.py
- backend/automation/jobs/anime_research_job.py
- core/models/content_orm.py (anime_episode_id)

Results:
- Run #1: 7 new episodes, 7 new titles
- Run #2: 0 new episodes, 10 existing (идемпотентность!)
- DB: 7 anime_titles, 7 anime_episodes, 8 content with anime_episode_id
- Связь ContentORM ↔ AnimeEpisode ↔ AnimeTitle: все OK

NEXT: Sprint 31.5 (Anime Channel Profile + Publishing)

==========================================================
SPRINT 31 COMPLETED (FINAL) - 2026-08-18
==========================================================

ANIME CHANNEL PROFILE + PUBLISHING:

Architecture (full pipeline):
  AniList GraphQL API
           ↓
  AnimeRegistry
           ↓
  AnimeKnowledgeEngine (creates AnimeTitle + AnimeEpisode)
           ↓
  AnimeResearchJob (ContentORM with anime_episode_id)
           ↓
  AnimePublishJob → PublicationImageResolver (anime cover)
           ↓
  Publication (text + image + buttons)
           ↓
  PlatformPublisher (Telegram/VK)

Key learnings:
- AniList GraphQL API работает без OAuth
- Единая сессия для Knowledge Layer + ContentORM
- anime_episode_id связывает ContentORM с Knowledge Layer
- anime_release profile добавлен в channel_profiles.py
- PublicationImageResolver поддерживает anime_release
- AnimePublishJob использует тот же Publishing Layer что и MangaPublishJob
- Идемпотентность работает

Files:
- engines/source_adapters/anilist_adapter.py
- engines/source_adapters/anime_registry.py
- core/models/anime_knowledge.py
- engines/anime_knowledge_engine.py
- backend/automation/jobs/anime_research_job.py
- backend/automation/jobs/anime_publish_job.py
- engines/channel_profiles.py (anime_release profile)
- engines/publishing/image_resolver.py (anime candidates)

Results:
- Research: 7 new episodes, 7 new titles (идемпотентность подтверждена)
- Publishing: 3 published, 1 failed (network), 0 skipped
- DB: 7 anime_titles, 7 anime_episodes, 8 content with anime_episode_id

Known issues (network):
- TinyURL timeout
- Telegram API timeout → fallback to text
- Fix: configure proxy or update network settings

NEXT: Sprint 32 (News Channel Profile + Publishing)

==========================================================
SPRINT 32 COMPLETED - 2026-08-18
==========================================================

NEWS CHANNEL PROFILE - TRIAD COMPLETE (manga/anime/news):

Architecture:
  Habr RSS → NewsResearchJob
       ↓
  NewsKnowledgeEngine (dedup by canonical_url)
       ↓
  NewsArticle + ContentORM (news_article_id)
       ↓
  NewsPublishJob → PublicationImageResolver (og:image + validation)
       ↓
  download image as bytes → _publish_photo_bytes()
       ↓
  Telegram post + Telegraph page

Key learnings:
- Habr og:image URL без расширения → Telegram sendPhoto 400
  "wrong type of the web page content"
  Fix: download + multipart upload as bytes
- News dedup: normalize URL (strip utm_ params) + unique index
- TelegramPublisher.publish() returns status='success' (unified)
- RSS sources: habr, vc, techcrunch, theverge
- og:image extraction: meta[property=og:image] / twitter:image

Files:
- engines/research/models/news_article.py
- engines/news_knowledge_engine.py
- backend/automation/jobs/news_research_job.py
- backend/automation/jobs/news_publish_job.py
- engines/telegram/publisher.py
- engines/publishing/telegram_publisher_adapter.py

Results:
- Research: 5 new articles, 5 images extracted, idempotent
- Publishing: 3 published (msg 350-352), 0 failed
- Verified: og:image + description + Telegraph + inline buttons

TRIAD COMPLETE:
  MANGA: cover from Knowledge Layer (3 sources)
  ANIME: key visual from AniList
  NEWS:  og:image (real photo, bytes upload)

NEXT: Sprint 33 (Image Acquisition Policy)

==========================================================
SPRINT 33 COMPLETED - 2026-08-18
==========================================================

IMAGE ACQUISITION POLICY - CONTROLLED AI FALLBACK:

Problem:
  ImageEngine (Pollinations AI) used as MANDATORY generator for all posts
  without images. This violated: "news → real photo; manga → cover; anime → key visual"

Solution:
  Created ImageAcquisitionPolicy — policy-driven layer that decides:
  - Use real image (priority)
  - Apply AI fallback (only if allowed by profile)

Architecture:
  PublicationImageResolver.resolve(content, channel)
       ↓
  candidates: [cover_url, og:image, content.image_url]
       ↓
  for url in candidates:
      if is_valid_image_url(url):
          real_url = url; break
       ↓
  ImageAcquisitionPolicy.acquire(content, real_url, profile)
       ↓
  if real_url:
      return AcquisitionResult(source="real")
       ↓
  if content_type == "news" && fallback == "ai_generated":
      return ImageEngine.generate(headline, text, style)
             → AcquisitionResult(source="ai", prompt=...)
       ↓
  return AcquisitionResult(source="none")

Rules:
  MANGA  → real cover only → fallback: none (NEVER AI!)
  ANIME  → real key visual only → fallback: none (NEVER AI!)
  NEWS   → og:image (real) → if none:
             ├── fallback: "ai_generated" → ImageEngine (Pollinations)
             └── fallback: "none" → text post (no image)

Test results:
  [1] MANGA без cover: source=none        ✅ AI запрещён
  [2] ANIME без cover: source=none        ✅ AI запрещён
  [3] NEWS с og:image: source=real        ✅ реальная приоритет
  [4] NEWS без og:image: source=ai        ✅ controlled AI fallback
  [5] NEWS fallback=none: source=none     ✅ policy уважается
  
  ALL POLICY TESTS PASSED ✅

Key learnings:
- Policy-driven: channel profile defines behavior
- AI fallback is CONTROLLED mechanism, not default
- Manga/Anime NEVER use AI (only real covers)
- Lazy init for expensive services (ImageEngine, ImageValidator)

Files:
- engines/publishing/image_acquisition.py (new)
- engines/publishing/image_resolver.py (integration)

NEXT: Sprint 34 (Production Hardening)

==========================================================
SPRINT 34 COMPLETED - 2026-08-18
==========================================================

PRODUCTION HARDENING:

Architecture:
  Production Hardening Stack:
    ├── NetworkConfig (SSL, timeouts, pooling, retry)
    │     ↓
    │   get_http_session() (singleton)
    │
    ├── Retry decorators (@retry_external_api, @retry_network)
    │     ↓
    │   Exponential backoff (2^attempt)
    │
    ├── Monitoring (StructuredFormatter + JobMetrics)
    │     ↓
    │   @monitor_job() → JSON logs
    │
    └── Health checks (database, APIs, components)
          ↓
        /health endpoint

Key learnings:
- SQLAlchemy 2.x requires text('SELECT 1') not string
- Retry decorator with exponential backoff is must-have
- Structured logging (JSON) easier to parse and analyze
- Health checks provide quick system verification
- Connection pooling reduces overhead for repeated requests
- SSL_VERIFY=false for container with self-signed certs

Files:
- core/network_config.py (new)
- core/retry.py (new)
- core/monitoring.py (new)
- core/health.py (new)
- engines/source_adapters/*.py (retry decorators)
- engines/cross_source_enricher.py (_build_sources_data)

E2E test results:
- Health: database ✅, APIs ✅, components ✅
- Manga research: 6 new chapters, 6 new titles
- Anime research: 0 new, 2 existing (idempotent!)
- News research: 3 new articles, 3 images extracted

NEXT: Sprint 35 (Multi-channel Automation)

==========================================================
SPRINT 35 COMPLETED - 2026-08-18
==========================================================

MULTI-CHANNEL AUTOMATION:

Architecture:
  ChannelManager
       ↓
  list_channels() → [channel1, channel2, ...]
       ↓
  enable_automation(channel_id, interval=30m)
       ↓
  ChannelScheduler.add_channel(schedule)
       ↓
  scheduler.start() → background thread
       ↓
  Main loop (every 10s):
    for channel in schedules:
      if enabled && time_to_run:
        research_runner(channel_id)
        publish_runner(channel_id)
        schedule.last_run = now
        schedule.error_count = 0 (or +1 on error)
       ↓
  After 5 errors → auto-pause

Key learnings:
- Scheduler with background thread is simple and effective
- Error tracking with auto-pause prevents cascade failures
- CLI tools make it easy to manage automation
- Daemon with signal handling enables graceful shutdown
- Concurrent execution allows multiple channels in parallel
- Configurable interval per channel (30m, 1h, etc.)

Files:
- core/channel_scheduler.py (new)
- core/channel_manager.py (new)
- core/cli.py (new)
- backend/automation/automation_service.py (new)

Test results:
- Scheduler: 2 channels, jobs run, status tracking ✅
- Channel Manager: list_channels, get_status ✅
- CLI: list-channels, status ✅
- Daemon: start, load channels, graceful shutdown ✅

NEXT: Sprint 36 (Advanced Analytics)

==========================================================
SPRINT 36.1 COMPLETED - 2026-08-18
==========================================================

ANALYTICS STORAGE:

Tables created:
  - post_metrics (views, likes, shares, comments, CTR)
  - ab_tests (variants, traffic_split, winner)
  - ab_test_results (impressions, clicks, conversions)

Key fixes:
- content.id is VARCHAR not UUID → FK must be VARCHAR
- 'metadata' reserved in SQLAlchemy → renamed to 'extra_metadata'
- db.expunge() before return → prevents DetachedInstanceError

Files:
- core/models/analytics.py (PostMetric, ABTest, ABTestResult)
- engines/analytics_engine.py (record/get/channel analytics/top posts)

NEXT: Sprint 36.2 (Engagement Tracker - collect from Telegram/VK API)

==========================================================
SPRINT 36.2 COMPLETED - 2026-08-18
==========================================================

ENGAGEMENT TRACKER:

Created:
- TelegramEngagementTracker (telegram_tracker.py)
- VKEngagementTracker (vk_tracker.py)

API capabilities:
  Telegram:
    ✅ getChat (type, title, username)
    ✅ getChatMemberCount (subscribers)
    ⚠️ views: only via t.me embed parsing (public channels)
    ❌ forwards/reactions: not available

  VK (group token):
    ✅ groups.getById (name, members_count)
    ✅ wall.get (latest posts with metrics)
    ❌ wall.getById: not available with group token
    ✅ metrics: likes, reposts, comments, views

Test results:
  Telegram: subscribers=2, channel_type=channel ✅
  VK: get_group_stats + get_latest_posts work ✅

Known limitations:
1. Telegram views: Bot API doesn't provide direct access
2. VK wall.getById: not available with group token
3. Use collect_metrics() without post_id for VK auto mode

Files:
- engines/analytics/telegram_tracker.py
- engines/analytics/vk_tracker.py
- engines/analytics/__init__.py

NEXT: Sprint 36.3 (EngagementCollectionJob - periodic collection)

==========================================================
SPRINT 36.3 COMPLETED - 2026-08-18
==========================================================

ENGAGEMENT COLLECTION JOB:

Created:
- backend/automation/jobs/engagement_collection_job.py

Pipeline:
  EngagementCollectionJob.run()
       ↓
  _find_published_posts()
       ↓
  _group_by_channel()
       ↓
  for each channel:
    _create_tracker() (Telegram/VK)
       ↓
    _process_post() for each post:
      → collect_metrics()
      → AnalyticsEngine.record_post_metric()
       ↓
  PostMetric table

API:
  job.run(channel_id=None, limit=100, hours_back=72)

Key points:
- Telegram: views via t.me embed parsing
- VK with group token: only group stats (wall.get unavailable)
- Idempotent: multiple runs add new metrics with new measured_at
- Per-post error handling: one failure doesn't break entire job

NEXT: Sprint 36.4 (Performance Dashboard)

==========================================================
SPRINT 36.4 COMPLETED - 2026-08-18
==========================================================

PERFORMANCE DASHBOARD:

Created:
- engines/performance_dashboard.py

Methods:
- overview(days) → total stats
- channel_details(name, days) → detailed stats
- top_posts(channel, days, limit, metric) → top posts
- compare_channels(days) → channel comparison
- generate_report(days) → formatted text report

CLI:
- python -m core.cli performance-report --days 7
- python -m core.cli performance-report --channel "Name" --days 7

Example output:
  📊 OVERVIEW: 45 posts, 12,450 views, 890 likes
  📱 BY PLATFORM: telegram: 45 metrics
  📈 CHANNEL COMPARISON: AI News RU: 8,900 views
  🏆 TOP 5 POSTS: sorted by views

NEXT: Sprint 36.5 (Automated Insights)

==========================================================
SPRINT 36 COMPLETED (FINAL) - 2026-08-18
==========================================================

ADVANCED ANALYTICS - FULL STACK:

36.1 Analytics Storage:
- Tables: post_metrics, ab_tests, ab_test_results
- Models: PostMetric, ABTest, ABTestResult
- AnalyticsEngine: record/get/channel/top_posts

36.2 Engagement Tracker:
- TelegramEngagementTracker (views, subscribers)
- VKEngagementTracker (group stats)
- Limitations: TG views only for public, VK wall.get unavailable

36.3 Engagement Collection Job:
- EngagementCollectionJob (automatic collection)
- Groups by channel, creates trackers
- Idempotent, per-post error handling

36.4 Performance Dashboard:
- PerformanceDashboard (overview, details, top, compare)
- CLI: performance-report (full + per channel)
- Text format with emoji

36.5 Automated Insights:
- AutomatedInsights (analysis + recommendations)
- CLI: insights (text + JSON)
- Categories: reach, engagement, frequency, channels, content
- Priorities: high/medium/low

Architecture:
  Analytics Layer:
    ├── Storage (PostMetric, ABTest)
    ├── Collection (EngagementCollectionJob)
    ├── Analysis (PerformanceDashboard)
    └── Intelligence (AutomatedInsights)

CLI:
  python -m core.cli performance-report --days 7
  python -m core.cli performance-report --channel "Name" --days 7
  python -m core.cli insights --days 7
  python -m core.cli insights --days 7 --json

Test results:
  Performance: 59 posts, 400 views, 60 likes
  Insights: low reach (9.8 avg), low engagement, recommendations generated

Files:
- core/models/analytics.py
- engines/analytics_engine.py
- engines/analytics/{telegram,vk}_tracker.py
- backend/automation/jobs/engagement_collection_job.py
- engines/performance_dashboard.py
- engines/automated_insights.py
- core/cli.py

Known limitations:
- Telegram views: only public channels via t.me embed
- VK API: wall.get unavailable with group token
- Test data: most views=0 due to private channels

NEXT: Sprint 37 (A/B Testing Framework - if needed)

==========================================================
SPRINT 37 COMPLETED - 2026-08-19
==========================================================

A/B TESTING FRAMEWORK:

Created:
- engines/ab_test_framework.py

Methods:
- create_test(name, variants, traffic_split, scope) → test_id
- start_test(test_id) / complete_test(test_id)
- assign_variant(test, content_id) → variant (hash-based)
- record_exposure(test_id, content_id, variant_id)
- update_results(test_id) → aggregate PostMetric
- analyze(test_id) → Welch t-test + winner
- list_tests() → all tests

Architecture:
  create_test() → draft
       ↓
  start_test() → running
       ↓
  NewsPublishJob:
    get_active_test() → find running test for channel
         ↓
    assign_variant() → deterministic hash
         ↓
    record_exposure() → track in ab_test_results
         ↓
    _publish_one(variant) → apply config overrides
         ↓
  EngagementCollectionJob (periodic)
       ↓
  PostMetric records
       ↓
  update_results() → aggregate
       ↓
  analyze() → Welch t-test
       ↓
  complete_test() → winner fixed

Statistics:
- Welch t-test (two-tailed, normal approx)
- significant: p < 0.05 && n >= 2
- winner: variant with higher mean
- improvement_pct: (winner - loser) / loser * 100

CLI:
  python -m core.cli ab-test create --name "Test" --variants [...] --split {...}
  python -m core.cli ab-test list
  python -m core.cli ab-test start --id <id>
  python -m core.cli ab-test analyze --id <id>
  python -m core.cli ab-test complete --id <id>

Variant config keys:
- emoji_header, include_description, max_hashtags
- unescape_html, include_image (bool)

Files:
- engines/ab_test_framework.py (new)
- core/cli.py (ab-test commands)
- backend/automation/jobs/news_publish_job.py (integration)
- core/models/analytics.py (scope field)

NEXT: Sprint 38 (Advanced Image Intelligence)

==========================================================
SPRINT 38 COMPLETED - 2026-08-19
==========================================================

ADVANCED IMAGE INTELLIGENCE:

Created:
- engines/image/unsplash_adapter.py
- engines/image/dalle_adapter.py

Fallback chain in ImageAcquisitionPolicy:
  og:image (real) → validate
       ↓
  Unsplash (stock, if UNSPLASH_ACCESS_KEY)
       ↓
  DALL-E (AI, if OPENAI_API_KEY)
       ↓
  Pollinations (free AI)
       ↓
  text post

Rules preserved:
- Manga/Anime: real covers only (fallback: none)
- News: fallback chain only if fallback: "ai_generated"
- Configurable: image_policy.fallback_chain

Test results:
[1] Unsplash available: False (no key) ✅
[2] Search without key: None (graceful) ✅
[3] Chain falls through to pollinations ✅
[4] Real image priority ✅
[5] Manga unchanged ✅

Files:
- engines/image/unsplash_adapter.py (new)
- engines/image/dalle_adapter.py (new)
- engines/publishing/image_acquisition.py (fallback chain)

NEXT: Sprint 39 (Content Optimization)
