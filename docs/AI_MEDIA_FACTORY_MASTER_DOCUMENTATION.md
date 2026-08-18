# AI MEDIA FACTORY - Master Documentation

Version: 1.12.0 | Last Update: 2026-08-11 | Status: Sprint 11 Complete

---

## 1. Vision

AI Media Factory - автономная платформа производства контента.
Канал создаётся за минуты и далее работает без участия человека:
Research -> Decision -> Writing -> Evaluation -> Image -> Publishing -> Analytics -> Experience

Платформы: Telegram (done), VK (done), YouTube/Dzen/TikTok/Instagram/X (roadmap).
Принципы: Platform First, AI First, Workflow Driven, Quality First (score >= 80), Everything Is Configurable.

---

## 2. Current Status

| Компонент | Статус |
|-----------|--------|
| Platform Core (FastAPI+PG+Redis+Docker) | done |
| Research (RSS/Google News/Reddit) | done |
| Writing (Ollama + style profiles) | done |
| Fact Checking | done |
| Evaluation (LLM-as-a-Judge, порог 80) | done |
| Workflow (DAG + APScheduler) | done |
| Automation Manager | done |
| Image Domain (Pollinations + AssetManager) | done |
| Telegram Publisher (sendMessage + sendPhoto) | done |
| VK Publisher (wall.post) | done |
| React Dashboard | done |
| Monitoring | Sprint 12 |
| ComfyUI | Sprint 13 |

Статистика: 4 канала, 366+ постов, avg quality 84.1, VK 19 постов (100%), Telegram пост с картинкой (message_id=191).

---

## 3. Architecture

React Dashboard -> FastAPI (app/api/v1) -> AutomationManager (scheduler+manager+runner)
-> WorkflowRuntime (WorkflowEngineV2, DAG) -> Jobs -> Engines -> Publishers -> БД.

Слои: Presentation (React) | API (FastAPI) | Automation (cron) | Workflow (DAG) |
Jobs (этапы) | Engines (алгоритмы+LLM) | Publishers (API соцсетей) | Data (ORM+PG) | Cache (Redis).

---

## 4. Repository Structure

backend/main.py - FastAPI + StaticFiles mount /assets
backend/app/api/v1/ - channels.py, content.py, workflows.py, sources.py, dashboard.py
backend/automation/ - runner.py, manager.py, scheduler.py
backend/automation/jobs/ - automation_jobs.py, image_job.py, revision_job.py, re_evaluation_job.py
backend/automation/publishers/ - telegram.py, vk.py
backend/core/ - database.py, models/*_orm.py, repositories/
engines/research/ - engine.py, sources/, deduplicator/, scorer/
engines/writing/ - engine.py, prompt_builder.py, prompt_manager.py, model_selector.py, styles/, validators.py, fact_guard.py, output_guard.py
engines/evaluator/ - engine.py (LLM Judge)
engines/fact_checker/ - engine.py
engines/image_prompt/ - engine.py (RU->EN, промпт <100 символов)
engines/image/ - engine.py (Pollinations URL)
engines/asset/ - manager.py (download+retry+storage)
engines/telegram/ - engine.py, publisher.py
frontend/ - React+TS (pages, components, api)
prompts/ - writing/, evaluation/

---

## 5. Sprint History

Sprint 1 Platform Core | Sprint 2 Research | Sprint 3 Decision | Sprint 4 Writing |
Sprint 5 Telegram | Sprint 6 Analytics | Sprint 7 Quality (LLM Judge, порог 80, revision loop max 3) |
Sprint 8 Workflow (DAG, APScheduler) | Sprint 9 Dashboard (React) | Sprint 10 Workflow Designer (React Flow) |
Sprint 11 Multi-Platform + Image Domain (VK wall.post, ImagePromptEngine, ImageEngine, AssetManager, sendPhoto, assets таблица).

Ключевые решения Sprint 11: короткие EN промпты (<100 символов, иначе Pollinations возвращает 0 bytes при URL >200);
data=payload вместо json=payload для sendPhoto; extra_data вместо metadata (SQLAlchemy reserved);
retry 3 попытки backoff 2.0; host.docker.internal:11434 для Ollama.

---

## 6. Engines

ResearchEngine: sources -> fetchers (rss/google/reddit) -> dedup (nomic-embed-text, cosine 0.85, окно 7 дней)
-> scorer (relevance*0.4 + freshness*0.3 + source_priority*0.2 + keywords*0.1) -> Content(status=research).

WritingEngine: brief -> PromptBuilder (SYSTEM+STYLE+RULES+FACTS+OUTPUT) -> ModelSelector
(llama3.1:8b simple / mistral-nemo:12b complex / qwen2.5-coder:7b tech) -> LLM -> Grammar -> Style -> FactGuard -> OutputGuard -> draft.

EvaluatorEngine: 5 критериев (factual 0.25, relevance 0.25, engagement 0.20, grammar 0.15, style 0.15),
overall >= 80 -> approved, иначе needs_revision + feedback.

FactChecker: grounding (все факты из источника), hallucination detection, fact_score.

ImagePromptEngine: RU headline -> Ollama -> EN промпт <100 символов (avg 62).

ImageEngine: prompt -> https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&model=flux&nologo=true (avg 168 символов).

AssetManager: download (timeout 120, retry 3, backoff) -> /app/assets/YYYY/MM/uuid.png -> AssetORM -> content.asset_id. Валидация: размер >1KB.

---

## 7. Jobs

ResearchJob: sources канала -> ResearchEngine -> Content(research).
WritingJob: Content(research) -> WritingEngine -> Content(draft, draft_text).
EvaluatorJob: Content(draft) -> EvaluatorEngine -> approved / needs_revision.
RevisionJob: needs_revision + reason -> WritingEngine.revise -> draft, revision_count+1 (max 3).
ReEvaluationJob: draft c revision_count>0 -> повторная оценка.
ImageJob: approved без image_url -> ImagePromptEngine -> ImageEngine -> image_url + image_prompt.
PublishJob: approved -> dispatcher по channel.platform -> Publisher -> published + published_at.

---

## 8. Publishers

TelegramPublisher (engines/telegram/publisher.py):
- publish(text, retries=3): sendMessage, retry backoff, flood control 429 (retry_after).
- publish_photo(text, image_url): sendPhoto, data=payload (НЕ json!), caption <=1024 (обрезка ...),
  fallback на текст при ошибке.

VkPublisher (backend/automation/publishers/vk.py):
- publish(text, credentials): wall.post, owner_id=-group_id, from_group=1, v=5.199.
- credentials: vk_group_id, vk_access_token.

Future: YouTubePublisher (Data API v3), DzenPublisher, TikTok, Instagram, X.

---

## 9. Image Domain

Пайплайн: Content(approved) -> ImageJob -> ImagePromptEngine -> ImageEngine -> AssetManager -> PublishJob -> sendPhoto.

БД: assets(id, content_id FK, type, storage_path, public_url, prompt, model, seed, width, height,
generation_time_ms, status, metadata JSONB, created_at);
content += image_url VARCHAR(500), image_prompt TEXT, asset_id FK.

StaticFiles: app.mount("/assets", StaticFiles(directory="/app/assets")) в main.py.

Проблемы и решения: URL>200 -> 0 bytes (короткие промпты); 400 sendPhoto (data=); timeout (retry);
caption>1024 (обрезка); пустые файлы (валидация >1KB).

Метрики: prompt avg 62 символа, картинка 43-66KB, генерация <5 сек, success 100%.

---

## 10. Database Schema

channels: id, name, platform (telegram/vk), bot_token, chat_id, vk_group_id, vk_access_token,
youtube_channel_id, youtube_api_key, dzen_channel_id, dzen_api_key, is_connected, is_active,
style_profile, language_publish, workflow_id, sources (JSON).

content: id, channel_id FK, source_url (NOT NULL), headline, source_text, status
(research/draft/needs_revision/approved/published/rejected), draft_text, quality_score,
fact_score, fact_check_passed, revision_count, last_revision_reason, validation_issues JSON,
model_used, image_url, image_prompt, asset_id FK, telegram_message_id, published_at,
publish_error, created_at, updated_at.

assets: см. раздел 9.

workflows: id, name, description, definition JSON (nodes+edges), is_active, created_at.
workflow_executions / execution_logs: id, workflow_id, channel_id, node_id, stage, status,
output JSON, error, metrics JSON, started_at, finished_at.
channel_schedules: channel_id FK, auto_publish, max_posts_per_day, cron_expression.
channel_templates / channel_profiles: пресеты оформления.
users, settings: dashboard.

---

## 11. API Endpoints

GET /api/v1/channels - список каналов
POST /api/v1/channels - создать канал
GET /api/v1/channels/{id} - детали
PATCH /api/v1/channels/{id} - обновить
DELETE /api/v1/channels/{id} - удалить
POST /api/v1/channels/{id}/connect-telegram - записать bot_token+chat_id+is_connected
POST /api/v1/channels/{id}/connect-vk - записать vk_group_id+vk_access_token
POST /api/v1/channels/{id}/connect-youtube / connect-dzen (заготовки)
PUT /api/v1/channels/{id}/schedule - auto_publish, max_posts_per_day, cron
GET /api/v1/channels/{id}/sources | POST | PATCH | DELETE - источники
GET /api/v1/content?channel_id=&status= - список постов
PATCH /api/v1/content/{id} - смена статуса (approve/reject)
POST /api/v1/workflows/{id}/run - запуск workflow для канала
GET /api/v1/workflows - шаблоны
GET /api/v1/logs - execution logs
GET /health - health check
GET /assets/... - статика картинок

---

## 12. Dashboard Pages

Dashboard (сводка) | Channels (создание+подключение) | Content (модерация) |
Sources (RSS) | Workflows (шаблоны+запуск) | Workflow Designer (React Flow) |
Analytics (метрики) | Logs (execution) | Images (assets) | Settings | Users.

---

## 13. Workflow System

WorkflowORM.definition JSON: nodes [{id, node_type, config}], edges [{from, to}].
Runner: если channel.workflow_id - WorkflowRuntime.execute (topological sort, parallel levels,
state machine), иначе hardcoded список jobs.
node_type_to_job: research, decision, writing/brief, evaluation/evaluator, revision,
re_evaluation, image, publish/publisher.
Scheduler: APScheduler cron (channel_schedules.cron_expression), rate limit max_posts_per_day.

---

## 14. Prompt System

Шаблоны prompts/writing/*.md: SYSTEM (роль) + STYLE (style_profile) + RULES (length/tone/CTA)
+ <FACTS>source_text</FACTS> + OUTPUT (формат).
Evaluation prompt: rubric 5 критериев, JSON output {scores, overall, feedback_for_regeneration}.
ImagePrompt prompt: перевод RU->EN, max 10 слов, ONLY prompt.

---

## 15. Configuration & Deployment

docker-compose: postgres (5432, amf_user/ai_media_factory), redis (6379), backend (8000), frontend (3001:80).
Volume backend: ./:/app. Ollama: host.docker.internal:11434.
Модели Ollama: mistral-nemo:12b (writing+prompt), llama3.1:8b, gemma2:9b, qwen2.5-coder, nomic-embed-text.
Запуск: docker compose up -d. Логи: docker compose logs -f backend.

---

## 16. Known Issues & Solutions

1. Pollinations: URL>200 символов -> 0 bytes => короткие EN промпты. 429 => backoff.
2. Telegram sendPhoto 400 => data= вместо json=. caption<=1024.
3. SQLAlchemy metadata reserved => extra_data = Column("metadata", JSON).
4. Ollama из контейнера => host.docker.internal:11434.
5. ContentORM ломался патчами => править аккуратно, проверять py_compile, держать бэкапы.
6. RevisionJob/ReEvaluationJob удалялись случайно => восстановлены, импорты в jobs/__init__.py и runner.py.
7. Assets не персистентны => нужен volume ./assets:/app/assets (TODO).
8. Нет image validation => TODO (Sprint 13).
9. Invoke-WebRequest в PowerShell => -UseBasicParsing.
10. xargs/grep недоступны в PowerShell => Select-String/Select-Object.

---

## 17. Coding Standards

- Engines: чистая бизнес-логика, без FastAPI; async где LLM.
- Jobs: тонкая обёртка над Engines, логирование, db.commit после каждого item.
- Publishers: валидация credentials, retry, fallback, подробные ошибки.
- ORM: все поля nullable=True кроме PK/NOT NULL; FK с ondelete.
- API: без бизнес-логики, только вызовы repositories/engines.
- Патчи кода: только через Python-скрипт с py_compile проверкой и показом диффа.
- PowerShell: here-string single-quoted, $PWD с долларом, -UseBasicParsing.

---

## 18. Roadmap

Sprint 12 Monitoring: Telegram-бот алертов, health checks (Ollama/Pollinations/VK), метрики SLA, Grafana.
Sprint 13 ComfyUI: локальный Flux/SDXL, ImageValidator (LLM score картинки), A/B варианты, volume для assets.
Sprint 14 YouTube: Data API v3, OAuth2, Shorts 9:16, авто-thumbnail.
Sprint 15 Dzen: лонгриды, SEO.
Sprint 16 Experience Engine: сбор engagement, learning loop (лучшие посты -> style profiles).
Sprint 17 Workflow Designer v2: conditional branching, parallel, UI-валидация.
Sprint 18 Marketplace: публичные шаблоны каналов и workflows.
Sprint 19-25: TikTok/Instagram/X, realtime analytics, multi-tenant, SaaS.

---

## 19. Appendix

URLs: Dashboard http://localhost:3000 | API http://localhost:8000/docs | PG localhost:5432 |
Redis 6379 | Ollama http://localhost:11434 | Assets http://localhost:8000/assets/...
VK тест-группа: club240792540. Telegram тест-канал: -1003901198631.
Каналы: AI Anime News (telegram, wf-simple), АИ Новости (telegram), Test VK Channel (vk).

CHANGELOG: v0.1-v1.11 внутренние | v1.12 Sprint 11 (VK + Image Domain + sendPhoto).

Конец документа.