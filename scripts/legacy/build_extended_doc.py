# -*- coding: utf-8 -*-
from pathlib import Path
from string import Template

def read_file(path, default="(file not found)"):
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except Exception as e:
        return f"{default} # error: {e}"

# Читаем все собранные файлы
telegram_publisher = read_file("docs/raw/telegram_publisher.txt")
image_prompt_engine = read_file("docs/raw/image_prompt_engine.txt")
image_engine = read_file("docs/raw/image_engine.txt")
asset_manager = read_file("docs/raw/asset_manager.txt")
telegram_engine = read_file("docs/raw/telegram_engine.txt")
auto_telegram_pub = read_file("docs/raw/auto_telegram_publisher.txt")
vk_publisher = read_file("docs/raw/vk_publisher.txt")
runner = read_file("docs/raw/runner.txt")
image_job = read_file("docs/raw/image_job.txt")
jobs_init = read_file("docs/raw/jobs_init.txt")
asset_orm = read_file("docs/raw/asset_orm.txt")
content_orm = read_file("docs/raw/content_orm.txt")
channel_orm = read_file("docs/raw/channel_orm.txt")
main_py = read_file("docs/raw/main_py.txt")
docker_compose = read_file("docs/raw/docker-compose.txt")
db_stats = read_file("docs/raw/db_stats.txt")
workflows = read_file("docs/raw/workflows.txt")
file_list_raw = read_file("docs/raw/file_list.txt")

# Сокращаем file_list
file_list_lines = file_list_raw.split("\\n")
if len(file_list_lines) > 150:
    file_list = "\\n".join(file_list_lines[:150]) + f"\\n\\n... and {len(file_list_lines) - 150} more files"
else:
    file_list = file_list_raw

# Экранируем обратные слэши и фигурные скобки в реальном коде
# чтобы они не ломали Template substitution
def safe_code(s):
    return s.replace("\\\\", "\\\\\\\\").replace("$", "Cyan")

# Применяем safe_code ко всем реальным файлам
code_vars = {
    "telegram_publisher": safe_code(telegram_publisher),
    "image_prompt_engine": safe_code(image_prompt_engine),
    "image_engine": safe_code(image_engine),
    "asset_manager": safe_code(asset_manager),
    "telegram_engine": safe_code(telegram_engine),
    "auto_telegram_pub": safe_code(auto_telegram_pub),
    "vk_publisher": safe_code(vk_publisher),
    "runner": safe_code(runner),
    "image_job": safe_code(image_job),
    "jobs_init": safe_code(jobs_init),
    "asset_orm": safe_code(asset_orm),
    "content_orm": safe_code(content_orm),
    "channel_orm": safe_code(channel_orm),
    "main_py": safe_code(main_py),
    "docker_compose": safe_code(docker_compose),
    "db_stats": db_stats,  # не эскейпим - это текст БД
    "workflows": safe_code(workflows),
    "file_list": file_list,
}

# RAW шаблон (r-префикс отключает unicode escape)
#  будет заменён на содержимое переменной
template_raw = r"""# AI MEDIA FACTORY - Extended Master Documentation

Version: 1.12.0 | Last Update: 2026-08-11 | Status: Sprint 11 Complete
Document Size: ~80 KB with real production code

> Этот документ содержит РЕАЛЬНЫЙ КОД всех критических компонентов проекта.
> Любой новый чат/разработчик сможет продолжить работу без повторения ошибок.

---

## Table of Contents

1. Vision & Philosophy
2. Current Status & Statistics
3. Architecture Overview
4. Repository Structure
5. Sprint History (1-11)
6. Real Code: Engines
7. Real Code: Jobs
8. Real Code: Publishers
9. Real Code: Runner (Workflow)
10. Real Code: ORM Models
11. Image Domain Pipeline
12. Database Schema & Statistics
13. Workflow Templates
14. API Endpoints
15. Configuration (docker-compose)
16. Main Application (FastAPI)
17. Known Issues & Solutions
18. Coding Standards
19. Roadmap (Sprints 12-25)
20. Appendix: Production Credentials

---

## 1. Vision & Philosophy

AI Media Factory - автономная платформа производства контента.
Канал создаётся за минуты и далее работает без участия человека:
Research -> Decision -> Writing -> Evaluation -> Image -> Publishing -> Analytics -> Experience

### Core Principles

- Platform First: единая абстракция Publisher для всех соцсетей
- AI First: LLM на каждом этапе (research, writing, evaluation, image generation)
- Workflow Driven: DAG-based пайплайны через WorkflowEngineV2
- Quality First: LLM-as-a-Judge с порогом 80+ для автопубликации
- Everything Is Configurable: workflows, style profiles, prompts в БД/файлах

### Supported Platforms

| Platform | Status | Publisher | Method |
|----------|--------|-----------|--------|
| Telegram | Production | TelegramPublisher | sendMessage + sendPhoto |
| VK | Production | VkPublisher | wall.post |
| YouTube | Sprint 14 | YouTubePublisher | Data API v3 |
| Dzen | Sprint 15 | DzenPublisher | Yandex API |
| TikTok | Sprint 19+ | TikTokPublisher | Content API |
| Instagram | Sprint 19+ | InstagramPublisher | Graph API |

---

## 2. Current Status & Statistics

### Production Statistics (real data from DB)



### Component Status

- Platform Core (FastAPI + PostgreSQL + Redis + Docker) - DONE
- Research Engine (RSS, Google News, Reddit) - DONE
- Decision Engine (priority scoring) - DONE
- Writing Engine (Ollama + style profiles) - DONE
- Fact Checker (grounding verification) - DONE
- Evaluator Engine (LLM-as-a-Judge) - DONE
- Workflow System (DAG-based, APScheduler) - DONE
- Automation Manager (cron jobs) - DONE
- Image Domain (Pollinations AI + AssetManager) - DONE
- Telegram Publisher (sendMessage + sendPhoto) - DONE
- VK Publisher (wall.post) - DONE
- React Dashboard - DONE
- Monitoring & Alerting - Sprint 12
- ComfyUI Integration - Sprint 13

### Key Metrics (Sprint 11)

- VK posts published: 19 (100% success)
- Telegram posts with images: 1+ (message_id=191, One Piece)
- Avg quality score: 84.1/100
- Avg image prompt length: 62 символа
- Avg image size: 43-66 KB
- Image generation time: < 5 seconds
- Success rate: 100% (для коротких промптов)

---

## 3. Architecture Overview

React Dashboard -> FastAPI (app/api/v1) -> AutomationManager (scheduler+manager+runner)
-> WorkflowRuntime (WorkflowEngineV2, DAG) -> Jobs -> Engines -> Publishers -> DB.

Layers: Presentation (React) | API (FastAPI) | Automation (cron) | Workflow (DAG) |
Jobs (stages) | Engines (algorithms+LLM) | Publishers (platform API) | Data (ORM+PG) | Cache (Redis).

---

## 4. Repository Structure



---

## 5. Sprint History

Sprint 1 Platform Core: Docker, FastAPI, SQLAlchemy, health checks.
Sprint 2 Research: RSS/Google News/Reddit, dedup via nomic-embed-text, relevance scoring.
Sprint 3 Decision: priority scoring, duplicate detection.
Sprint 4 Writing: WritingEngine + Ollama, Prompt Builder, Style Profiles, Model Selector.
  Models: mistral-nemo:12b (main), qwen2.5-coder:7b (tech), llama3.1:8b (backup).
  Prompt structure: SYSTEM + STYLE + RULES + <FACTS> + OUTPUT
Sprint 5 Telegram: TelegramPublisher, sendMessage, retry with backoff, flood control.
Sprint 6 Analytics: ExecutionLogORM, metrics collection.
Sprint 7 Quality: EvaluatorEngine (LLM Judge), 5 criteria, threshold 80, revision max 3.
  Scoring: overall = factual*0.25 + relevance*0.25 + engagement*0.20 + grammar*0.15 + style*0.15
Sprint 8 Workflow: WorkflowEngineV2 (DAG), 4 templates, APScheduler, AutomationManager.
Sprint 9 Dashboard: React + TypeScript, pages, axios client, polling.
Sprint 10 Workflow Designer: React Flow, drag-and-drop, JSON configs.
Sprint 11 Multi-Platform + Image Domain (CURRENT):
  1. VK Integration: vk_group_id/vk_access_token, VkPublisher (wall.post), 19 posts in club240792540.
  2. Image Domain (full pipeline): ImagePromptEngine -> ImageEngine -> AssetManager -> ImageJob -> PublishJob.
  3. Telegram sendPhoto: publish_photo() with data=payload, caption <=1024, fallback to text.
  4. PublishJob refactoring: uses draft_text, multi-platform dispatcher, status approved->published.
  5. Static files: app.mount("/assets", StaticFiles).
  Critical Decisions:
  - Short EN prompts (<100 chars) - otherwise Pollinations returns 0 bytes at URL >200
  - data=payload instead of json=payload for Telegram sendPhoto
  - extra_data = Column("metadata", JSON) - SQLAlchemy reserves metadata
  - host.docker.internal:11434 for Ollama from container
  - Retry 3 attempts backoff 2.0 for AssetManager

---

## 6. Real Code: Engines

### 6.1 TelegramPublisher (LOW-LEVEL - engines/telegram/publisher.py)

`$telegram_publisher
`

Key points:
- publish_photo() uses data=payload, NOT json=payload
- caption truncated to 1024 chars
- Fallback to publish(text) on sendPhoto error
- Detailed logging of HTTP status and response body

---

### 6.2 ImagePromptEngine (engines/image_prompt/engine.py)

`

`

Key points:
- Generates short EN prompts <100 chars via Ollama
- Uses mistral-nemo:12b
- Critical constraint: prompt <100 chars, otherwise Pollinations URL >200 -> 0 bytes
- Fallback: "anime scene, high quality"

---

### 6.3 ImageEngine (engines/image/engine.py)

`

`

Key points:
- Builds URL: https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&model=flux&nologo=true
- Parameters: width=1024, height=576 (16:9 landscape), model=flux, nologo=true
- Avg URL length: 168 chars

---

### 6.4 AssetManager (engines/asset/manager.py)

`

`

Key points:
- _download_with_retry(): 3 attempts, backoff 2.0, timeout 120s
- Validation: file size > 1KB (otherwise deletes empty file)
- Saves to /app/assets/YYYY/MM/uuid.png
- extra_data instead of metadata (SQLAlchemy reserved)
- Creates AssetORM and updates content.asset_id

---

### 6.5 TelegramEngine (wrapper - engines/telegram/engine.py)

`

`

---

## 7. Real Code: Jobs

### 7.1 ImageJob (backend/automation/jobs/image_job.py)

`

`

Key points:
- Takes approved posts without image_url (limit 10)
- Calls ImageEngine.generate(headline, draft_text)
- Saves image_url and image_prompt to ContentORM
- Logs: "Items without images", "Image URL generated for {id}"

---

### 7.2 Jobs Registry (backend/automation/jobs/__init__.py)

`

`

IMPORTANT: all 8 classes exported - do not remove any!

---

## 8. Real Code: Publishers

### 8.1 TelegramPublisher (automation layer - backend/automation/publishers/telegram.py)

`

`

Key points:
- Wrapper over engines.telegram.publisher
- Accepts image_url via kwargs
- Calls self.engine.publish_photo() if image_url exists
- platform_data contains has_image flag

---

### 8.2 VkPublisher (backend/automation/publishers/vk.py)

`

`

Key points:
- Uses VK API wall.post
- credentials: vk_group_id (negative), vk_access_token
- owner_id = f"-{group_id}", from_group=1, v=5.199
- Error handling: parse VK error_code/error_msg

---

## 9. Real Code: Runner (Workflow)

### 9.1 AutomationRunner (backend/automation/runner.py)

`

`

Key points:
- stage_map: mapping stage_name -> Job class
- node_type_to_job: mapping node_type (with aliases) -> Job class
- run_now(): if workflow_id -> WorkflowRuntime, else hardcoded jobs list
- Fallback jobs list: research -> decision -> writing -> evaluation -> publish
- retry_stage(): retry single specific stage

---

## 10. Real Code: ORM Models

### 10.1 AssetORM (core/models/asset_orm.py)

`

`

IMPORTANT: extra_data = Column("metadata", JSON) - SQLAlchemy reserves metadata.

---

### 10.2 ContentORM (core/models/content_orm.py)

`

`

Key fields:
- image_url = Column(String(500)) - URL from Pollinations
- image_prompt = Column(Text) - prompt used for generation
- asset_id = Column(String, ForeignKey("assets.id")) - link to assets table
- status: research -> draft -> needs_revision -> approved -> published -> rejected

---

### 10.3 ChannelORM (core/models/channel_orm.py)

`

`

Key fields:
- Telegram: bot_token, chat_id, is_connected
- VK: vk_group_id, vk_access_token
- YouTube (planned): youtube_channel_id, youtube_api_key
- Dzen (planned): dzen_channel_id, dzen_api_key
- sources: JSON array of KnowledgeSource
- workflow_id: FK to workflows

---

## 11. Image Domain Pipeline

### Full image generation flow

Content (status=approved, image_url=None)
  -> ImageJob.run()
  -> ImagePromptEngine.generate_prompt(headline, draft_text)
     # Ollama translates RU -> EN, short prompts <100 chars
     -> image_prompt (EN, avg 62 chars)
  -> ImageEngine.generate(prompt)
     # URL encoding + Pollinations URL
     -> image_url (avg 168 chars)
  -> AssetManager.save_from_url(image_url)
     # Download + retry (3 attempts) + save to /app/assets/
     -> asset (AssetORM)
  -> Content.image_url = image_url
  -> Content.asset_id = asset.id
  -> PublishJob.run()
  -> TelegramPublisher.publish(text, image_url, credentials)
  -> self.engine.publish_photo(text, image_url, bot_token, chat_id)
  -> POST https://api.telegram.org/bot{token}/sendPhoto
     data={  # IMPORTANT: data=, not json=
       "chat_id": chat_id,
       "photo": image_url,
       "caption": text[:1024]
     }
  -> Post with image in Telegram

### Pollinations URL Format

https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&model=flux&nologo=true

Parameters:
- width: 1024 (landscape for Telegram)
- height: 576 (16:9 aspect ratio)
- model: flux (best quality)
- nologo: true (no watermark)

---

## 12. Database Schema & Statistics

### channels table

| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR PK | UUID |
| name | VARCHAR | Channel name |
| platform | VARCHAR | telegram/vk/youtube/dzen |
| bot_token | VARCHAR | Telegram bot token |
| chat_id | VARCHAR | Telegram chat ID |
| vk_group_id | VARCHAR | VK group ID (negative) |
| vk_access_token | VARCHAR | VK API token |
| is_connected | BOOLEAN | Connected |
| is_active | BOOLEAN | Active |
| style_profile | VARCHAR | Post style |
| language_publish | VARCHAR | Publish language |
| workflow_id | VARCHAR FK | Workflow template |
| sources | JSON | Source array |

### content table

| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR PK | UUID |
| channel_id | VARCHAR FK | Channel link |
| source_url | VARCHAR NOT NULL | Source URL |
| headline | VARCHAR | Headline |
| source_text | TEXT | Original text |
| status | VARCHAR | research/draft/needs_revision/approved/published/rejected |
| draft_text | TEXT | Generated text |
| quality_score | INTEGER | Score 0-100 |
| image_url | VARCHAR(500) | Image URL (Pollinations) |
| image_prompt | TEXT | Image prompt |
| asset_id | VARCHAR FK | Link to assets |
| telegram_message_id | VARCHAR | Message ID in Telegram |
| published_at | TIMESTAMP | Publish time |

### assets table

| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR PK | UUID |
| content_id | VARCHAR FK | Content link |
| type | VARCHAR | image/video/audio |
| storage_path | VARCHAR | assets/2026/08/uuid.png |
| public_url | VARCHAR | /assets/2026/08/uuid.png |
| prompt | TEXT | Prompt used |
| model | VARCHAR | flux/sdxl/comfyui |
| seed | INTEGER | Seed for reproducibility |
| width/height | INTEGER | Dimensions |
| generation_time_ms | INTEGER | Generation time |
| status | VARCHAR | generating/generated/failed |
| extra_data | JSON | Extra data (maps to "metadata" column) |

### Production Statistics (real data)



---

## 13. Workflow Templates



### Available workflow presets

1. Simple: Research -> Writing -> Publish
2. Default Full: Research -> Decision -> Writing -> Evaluator -> Revision -> Image -> Publish
3. Research Only: Research -> Decision
4. Legacy: backward compatibility

---

## 14. API Endpoints

### Channels

- GET /api/v1/channels - list channels
- POST /api/v1/channels - create channel
- GET /api/v1/channels/{id} - details
- PATCH /api/v1/channels/{id} - update
- DELETE /api/v1/channels/{id} - delete
- POST /api/v1/channels/{id}/connect-telegram - save bot_token+chat_id
- POST /api/v1/channels/{id}/connect-vk - save vk_group_id+vk_access_token
- POST /api/v1/channels/{id}/connect-youtube - (planned)
- POST /api/v1/channels/{id}/connect-dzen - (planned)
- PUT /api/v1/channels/{id}/schedule - auto_publish, cron_expression

### Content

- GET /api/v1/content?channel_id=&status= - list posts
- PATCH /api/v1/content/{id} - change status

### Workflows

- GET /api/v1/workflows - templates
- POST /api/v1/workflows/{id}/run - run for channel

### Other

- GET /health - health check
- GET /assets/... - static images (StaticFiles mount)
- GET /api/v1/logs - execution logs

---

## 15. Configuration

### docker-compose.yml

`

`

### Environment Variables

- DATABASE_URL: postgresql://amf_user:amf_password@postgres:5432/ai_media_factory
- REDIS_URL: redis://redis:6379
- OLLAMA_BASE_URL: http://host.docker.internal:11434 (Windows/Mac)
- VK_API_VERSION: 5.199
- TELEGRAM_API_URL: https://api.telegram.org/bot
- POLLINATIONS_BASE_URL: https://image.pollinations.ai

### LLM Models (Ollama)

- mistral-nemo:12b - main writing + image prompts
- llama3.1:8b - fast backup
- gemma2:9b - alternative
- qwen2.5-coder:7b - code/technical content
- nomic-embed-text - embeddings for deduplication

### Commands

docker compose up -d
docker compose logs -f backend
docker compose exec backend bash
docker compose exec postgres psql -U amf_user -d ai_media_factory

---

## 16. Main Application

### FastAPI app (backend/main.py)

`

`

IMPORTANT: app.mount("/assets", StaticFiles(directory="/app/assets")) - for image access.

---

## 17. Known Issues & Solutions

### CRITICAL (do not repeat!)

| # | Problem | Solution |
|---|---------|----------|
| 1 | Pollinations returns 0 bytes at URL >200 chars | Short EN prompts <100 chars via Ollama |
| 2 | Telegram sendPhoto 400 Bad Request | data=payload instead of json=payload (form-data) |
| 3 | SQLAlchemy: "Attribute name 'metadata' is reserved" | extra_data = Column("metadata", JSON) |
| 4 | Ollama unavailable from container | host.docker.internal:11434 instead of localhost:11434 |
| 5 | ContentORM broken by patches (IndentationError, NameError) | Use py_compile.compile() for validation, show diff |
| 6 | RevisionJob/ReEvaluationJob accidentally deleted by patches | Restored, keep imports in jobs/__init__.py and runner.py |
| 7 | Assets not persistent | TODO: add volume ./assets:/app/assets in docker-compose |
| 8 | No image validation | TODO: Sprint 13 - ImageValidator (LLM score) |
| 9 | PowerShell Invoke-WebRequest warning | Always use -UseBasicParsing |
| 10 | xargs/grep unavailable in PowerShell | Use Select-String/Select-Object |
| 11 | Telegram caption > 1024 chars | Auto-truncate with ... |
| 12 | Empty files from Pollinations | Validation: file_size > 1KB in AssetManager |

### Limitations

- Pollinations rate limits: 429 on frequent requests - use backoff
- Telegram flood control: 429 - parse retry_after, sleep, retry
- Long Russian prompts: always translate to short EN via Ollama
- Assets persistence: lost on docker compose down -v (no volume)
- No image quality validation: any artifact gets published

### Coding Standards

- Engines: clean business logic, no FastAPI; async where LLM
- Jobs: thin wrapper over Engines, logging, db.commit after each item
- Publishers: credentials validation, retry, fallback, detailed errors
- ORM: nullable=True except PK/NOT NULL; FK with ondelete
- API: no business logic, only repositories/engines calls
- Code patches: only via Python script with py_compile validation
- PowerShell: single-quoted here-strings @'...'@, C:\Users\Johnn\AI-MEDIA-FACTORY with dollar, -UseBasicParsing

---

## 18. Roadmap (Sprints 12-25)

### Sprint 12: Monitoring & Alerting (NEXT)
- [ ] Telegram bot for notifications
- [ ] Health checks (Ollama, Pollinations, VK API, Telegram API)
- [ ] SLA metrics (uptime, latency, success rate)
- [ ] Grafana dashboards
- [ ] Alerting: 5xx errors, low quality, API failures

### Sprint 13: ComfyUI Integration
- [ ] Local ComfyUI (Docker)
- [ ] Flux/SDXL models
- [ ] ImageValidator (LLM quality scoring)
- [ ] A/B testing images
- [ ] Batch generation
- [ ] Volume ./assets:/app/assets for persistence

### Sprint 14: YouTube Shorts
- [ ] YouTube Data API v3
- [ ] OAuth2 flow
- [ ] Vertical video 9:16
- [ ] Auto-thumbnail
- [ ] Title/description optimization via LLM

### Sprint 15: Dzen Publishing
- [ ] Yandex Dzen API
- [ ] Long-form articles
- [ ] Rich formatting
- [ ] SEO optimization

### Sprint 16: Experience Engine
- [ ] Engagement tracking (likes, shares, comments)
- [ ] Learning loop: top posts -> style profiles
- [ ] Best posting time prediction
- [ ] Content performance scoring

### Sprint 17: Workflow Designer v2
- [ ] Conditional branching (if quality < 80 -> revision)
- [ ] Parallel execution
- [ ] UI-based validation
- [ ] Visual debugging

### Sprint 18: Marketplace
- [ ] Public channel templates
- [ ] Public workflow templates
- [ ] Community sharing

### Sprint 19-25: Expansion
- TikTok, Instagram, X, Threads, Pinterest
- Realtime analytics
- Multi-tenant architecture
- SaaS version
- Mobile dashboard

---

## 19. Appendix

### Production URLs

| Service | URL |
|---------|-----|
| React Dashboard | http://localhost:3000 |
| API docs (Swagger) | http://localhost:8000/docs |
| API v1 | http://localhost:8000/api/v1 |
| Health check | http://localhost:8000/health |
| Assets storage | http://localhost:8000/assets/... |
| PostgreSQL | localhost:5432 (amf_user / ai_media_factory) |
| Redis | localhost:6379 |
| Ollama | http://localhost:11434 |

### Test Channels

- Telegram AI Anime News: chat_id=-1003901198631, workflow=wf-simple
- Telegram AI News: (empty credentials, inactive)
- Telegram AI News RU (Test): chat_id=-1004324099845, is_active=false
- Test VK Channel: vk_group_id=-240792540

### CHANGELOG

- v0.1-v1.10: internal development
- v1.11 (Sprint 11): VK Publisher + Image Domain + Telegram sendPhoto
- v1.12 (planned): Monitoring & Alerting

---

End of Document

Generated: 2026-08-11
Total size: ~80 KB (with real code)
Purpose: Single source of truth for AI Media Factory project
"""

template = Template(template_raw)
doc = template.substitute(**code_vars)

out = Path("docs/MASTER_DOCUMENTATION_EXTENDED.md")
out.write_text(doc, encoding="utf-8")
size_kb = len(doc.encode("utf-8")) / 1024
lines = len(doc.split("\\n"))
print("=" * 60)
print("EXTENDED MASTER DOCUMENTATION CREATED")
print("=" * 60)
print(f"  Path: {out}")
print(f"  Size: {size_kb:.1f} KB")
print(f"  Lines: {lines}")
print("=" * 60)
print("Open: code docs/MASTER_DOCUMENTATION_EXTENDED.md")
