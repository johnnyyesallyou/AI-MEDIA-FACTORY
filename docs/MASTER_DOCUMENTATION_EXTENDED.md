# AI MEDIA FACTORY - Extended Master Documentation

**Version:** 1.12.0
**Last Update:** 2026-08-11
**Status:** Sprint 11 Complete (Multi-Platform Publishers + Image Domain)

> Этот документ содержит РЕАЛЬНЫЙ КОД всех критических компонентов.
> Любой новый чат/разработчик сможет продолжить работу без повторения ошибок.

---

## 1. Vision & Philosophy

AI Media Factory - автономная платформа производства контента.
Канал создаётся за минуты и далее работает без участия человека:
Research -> Decision -> Writing -> Evaluation -> Image -> Publishing -> Analytics -> Experience

### Core Principles
- Platform First: единая абстракция Publisher для всех соцсетей
- AI First: LLM на каждом этапе
- Workflow Driven: DAG-based пайплайны через WorkflowEngineV2
- Quality First: LLM-as-a-Judge с порогом 80+
- Everything Is Configurable: workflows, style profiles, prompts в БД

### Supported Platforms
| Platform | Status | Publisher | Method |
|----------|--------|-----------|--------|
| Telegram | Production | TelegramPublisher | sendMessage + sendPhoto |
| VK | Production | VkPublisher | wall.post |
| YouTube | Sprint 14 | YouTubePublisher | Data API v3 |
| Dzen | Sprint 15 | DzenPublisher | Yandex API |
| TikTok/Instagram/X | Sprint 19+ | | |

---

## 2. Current Status & Statistics

### Production Statistics (реальные данные из БД)
`
﻿        tbl        | count 
-------------------+-------
 channels          |     4
 content           |  1345
 content_published |   486
 content_approved  |   673
 assets            |     2
 workflows         |     4
 channel_schedules |     4
 execution_logs    |  2905
(8 rows)
`

### Component Status
- DONE: Platform Core, Research, Decision, Writing, Fact Checker, Evaluator
- DONE: Workflow System, Automation Manager, Image Domain
- DONE: Telegram Publisher (sendMessage + sendPhoto), VK Publisher
- DONE: React Dashboard
- PENDING: Sprint 12 (Monitoring), Sprint 13 (ComfyUI)

### Key Metrics (Sprint 11)
- VK posts: 19 (100% success)
- Telegram posts with images: 1+ (message_id=191)
- Avg quality score: 84.1/100
- Avg image prompt: 62 chars (EN, via Ollama)
- Avg image size: 43-66 KB
- Image gen time: <5 sec

---

## 3. Architecture Overview
`
React Dashboard -> FastAPI -> AutomationManager -> WorkflowRuntime (DAG)
  -> Jobs -> Engines -> Publishers -> DB

Layers: Presentation | API | Automation | Workflow | Jobs | Engines
        | Publishers | Data (ORM+PG) | Cache (Redis)
`

---

## 4. Repository Structure
`
﻿
Path                                                                 Size
----                                                                 ----
.dockerignore                                                         103
.gitignore                                                            489
.pytest_cache\.gitignore                                               37
.pytest_cache\CACHEDIR.TAG                                            191
.pytest_cache\README.md                                               302
.pytest_cache\v\cache\lastfailed                                      298
.pytest_cache\v\cache\nodeids                                         224
add_buttons_final.py                                                 2294
add_buttons_fixed.py                                                 2496
add_buttons_surgery.py                                               2739
add_connect_methods.py                                                948
add_content_draft.py                                                  971
add_delete_source_endpoint.py                                         790
add_dzen_to_dropdown.py                                              1235
add_get_next_run.py                                                  1003
add_health_checks.py                                                 5128
add_image_fields.sql                                                  209
add_image_job_class.py                                               4195
add_logger.py                                                        1776
add_modal_final.py                                                   6130
add_mount.py                                                         1705
add_photo_method.py                                                  1798
add_platform_buttons.py                                              3002
add_platform_buttons_v2.py                                           5098
add_platform_endpoints.py                                            5036
add_platform_modal.py                                                6299
add_platform_state.py                                                3358
add_remove_source.py                                                 1380
add_retry_endpoint.py                                                3363
add_retry_to_client.py                                                475
add_retry_to_runner.py                                               2328
add_run_channel.py                                                   1683
add_scheduler_status.py                                              1641
add_static_files.py                                                  2222
AI_CONTEXT.md                                                        1231
ai_media_factory.db                                                151552
AI_MEDIA_FACTORY_AUDIT.zip                                         330950
apply_all_fixes.py                                                   2433
apply_publisher_abstraction.py                                       2219
asset_init.py                                                          33
asset_manager.py                                                     5988
asset_manager_fixed.py                                               4927
asset_manager_retry.py                                               5635
asset_orm.py                                                         1552
asset_orm_fixed.py                                                   1889
AUDIT\docker_images.txt                                              3698
AUDIT\docker_status.txt                                               136
AUDIT\git_history.txt                                                1756
AUDIT\git_status.txt                                                 2732
AUDIT\package_report.txt                                           912180
AUDIT\pip_freeze.txt                                                 8408
AUDIT\project_context.txt                                         1388619
AUDIT\project_structure.txt                                       1498876
AUDIT\requirements.txt                                               8408
AUDIT\requirements_report.txt                                        8408
AUDIT\описание и запуск локально.txt                                    0
backend\.gitkeep                                                        0
backend\__init__.py                                                     0
backend\app\__init__.py                                                 0
backend\app\api\__init__.py                                             0
backend\app\api\v1\__init__.py                                          0
backend\app\api\v1\ai.py                                             4727
backend\app\api\v1\analytics.py                                      5976
backend\app\api\v1\assets.py                                         2120
backend\app\api\v1\automation.py                                     5630
backend\app\api\v1\automation.py.backup                              2061
backend\app\api\v1\automation_v2.py                                  7973
backend\app\api\v1\channels.py                                      13627
backend\app\api\v1\content.py                                        5389
backend\app\api\v1\dashboard.py                                      6991
backend\app\api\v1\health.py                                         3746
backend\app\api\v1\integrations.py                                   3028
backend\app\api\v1\knowledge.py                                      2715
backend\app\api\v1\logs.py                                           3940
backend\app\api\v1\research.py                                       6792
backend\app\api\v1\research.py.backup_fact_guard                     6789
backend\app\api\v1\research.py.backup_source_fix                     6790
backend\app\api\v1\router.py                                         1847
backend\app\api\v1\schemas.py                                       10071
backend\app\api\v1\settings.py                                       2390
backend\app\api\v1\templates.py                                      9204
backend\app\api\v1\users.py                                          2451
backend\app\api\v1\workflows.py                                      4686
backend\automation\__init__.py                                          0
backend\automation\api\__init__.py                                      0
backend\automation\automation_manager_v2.py                         13277
backend\automation\automation_models.py                               570
backend\automation\automation_policies.py                             416
backend\automation\config.py                                         1506
backend\automation\jobs\__init__.py                                   400
backend\automation\jobs\automation_jobs.py                          24945
backend\automation\jobs\automation_jobs.py.backup                    4909
backend\automation\jobs\automation_jobs.py.backup_before_research   10595
backend\automation\jobs\image_job.py                                 3258
backend\automation\jobs\re_evaluation_job.py                         3078
backend\automation\jobs\revision_job.py                              3172
backend\automation\manager.py                                        2669
backend\automation\model_router.py                                    638
backend\automation\models\__init__.py                                   0
backend\automation\policies\__init__.py                              7268
backend\automation\publishers\__init__.py                             437
backend\automation\publishers\base.py                                1097
backend\automation\publishers\dzen.py                                 700
backend\automation\publishers\factory.py                             1033
backend\automation\publishers\telegram.py                            2549
backend\automation\publishers\vk.py                                  6049
backend\automation\publishers\youtube.py                              718
backend\automation\runner.py                                         6186
backend\automation\runtime\__init__.py                                416
backend\automation\runtime\contracts.py                              4935
backend\automation\runtime\job_factory.py                            1877
backend\automation\runtime\register_jobs.py                           698
backend\automation\runtime\workflow_runtime.py                      11691
backend\automation\scheduler.py                                      8082
backend\automation\service.py                                         987
backend\automation\services\__init__.py                                 0
backend\automation\triggers.py                                        507
backend\automation\workflow.py                                       7261
backend\automation\workflow_engine_v2.py                             6380
backend\main.py                                                      2329
backend\static\js\dashboard.backup.js                               19703
backend\static\js\dashboard.js                                      23012
backend\templates\dashboard.backup.html                             14921
backend\templates\dashboard.html                                    14970
backend_logs.txt                                                    16980
check_vk_posts.py                                                    1016
check_workflow.py                                                     513
clean_bom.py                                                          758
clean_channel_manager.py                                              835
connectors\.gitkeep                                                     0
core\__init__.py                                                        0
core\database.py                                                     1697
core\models\__init__.py                                               378
core\models\asset_orm.py                                             1889
core\models\channel.py                                               1947
core\models\channel_orm.py                                           2312
core\models\channel_profile_orm.py                                   1620
core\models\channel_schedule_orm.py                                  1329
core\models\channel_template_orm.py                                  2053
core\models\content_orm.py                                           2493
core\models\content_orm.py.backup_source_text                        1747
core\models\execution_log_orm.py                                     1224
core\models\model_routing.py                                         3454
core\models\policy.py                                                1680
core\models\prompt_tracking.py                                       3249
core\models\routing_defaults.py                                      3126
core\models\workflow_orm.py                                           755
core\policies\engine.py                                              2239
core\prompt_lab\engine.py                                            3920
core\prompt_lab\models.py                                            1472
core\prompts\logger.py                                               2102
core\prompts\manager.py                                              1293
core\repositories\__init__.py                                           0
core\repositories\channel_repository.py                              2848
core\repositories\content_repository.py                              3438
core\repositories\templates_repository.py                            4865
core\repositories\workflow_repository.py                             1600
core\workflows\executor.py                                           2650
core\workflows\models.py                                             2180
create_anime_test.py                                                 1762
create_assets_table.sql                                              1446
create_one_post.py                                                   1117
create_prompt_builder.py                                             5670
create_status.py                                                    11282
create_test_final.py                                                 1123
create_test_post.py                                                  1229
docker-compose.backup.yml                                            3500
docker-compose.yml                                                   3578
Dockerfile.backend                                                    724
docs\ai\AGENTS.md                                                    3566
docs\ai\MEMORY.md                                                    3818
docs\ai\MODELS.md                                                    3078
docs\ai\PROMPTS.md                                                   2765
docs\AI_MEDIA_FACTORY_ENGINEERING_BIBLE.md                           3473
docs\AI_MEDIA_FACTORY_MASTER_DOCUMENTATION.md                       13487
docs\architecture\ARCHITECTURE.md                                    4200
docs\architecture\COMPONENTS.md                                      4405
docs\architecture\EVENT_BUS.md                                       3346
docs\architecture\PIPELINES.md                                       3935
docs\architecture\REAL_ARCHITECTURE.md                               1949
docs\backend\API_CONTRACT.md                                         3151
docs\backend\DATABASE.md                                             4056
docs\backend\REPOSITORIES.md                                         3113
docs\backend\SERVICES.md                                             4145
docs\business\BUSINESS_RULES.md                                      4643
docs\business\WORKFLOWS.md                                           4578
docs\DECISIONS\.gitkeep                                                 0
docs\deployment\DEPLOYMENT.md                                        3005
docs\deployment\DOCKER.md                                            3366
docs\deployment\ENVIRONMENT.md                                       3862
docs\development\CODING_STYLE.md                                     3313
docs\development\DEVELOPMENT_RULES.md                                3143
docs\development\TESTING.md                                          3602
docs\history\CHANGELOG.md                                            1856
docs\history\DECISIONS.md                                            4001
docs\raw\asset_manager.txt                                           7790
docs\raw\asset_orm.txt                                               2321
`

---

## 5. Sprint History

**Sprint 1 Platform Core:** Docker, FastAPI, SQLAlchemy, health checks.
**Sprint 2 Research:** RSS/Google News/Reddit, dedup via nomic-embed-text.
**Sprint 3 Decision:** priority scoring, duplicate detection.
**Sprint 4 Writing:** WritingEngine+Ollama, PromptBuilder, StyleProfiles, ModelSelector.
  Models: mistral-nemo:12b (main), qwen2.5-coder:7b (tech), llama3.1:8b (backup).
  Prompt: SYSTEM + STYLE + RULES + <FACTS> + OUTPUT
**Sprint 5 Telegram:** TelegramPublisher, sendMessage, retry, flood control (429).
**Sprint 6 Analytics:** ExecutionLogORM, metrics collection.
**Sprint 7 Quality:** EvaluatorEngine (LLM Judge), 5 criteria, threshold 80, revision max 3.
  Scoring: overall = factual*0.25 + relevance*0.25 + engagement*0.20 + grammar*0.15 + style*0.15
**Sprint 8 Workflow:** WorkflowEngineV2 (DAG), 4 templates, APScheduler.
**Sprint 9 Dashboard:** React+TS, pages, axios.
**Sprint 10 Workflow Designer:** React Flow, drag-and-drop.
**Sprint 11 Multi-Platform + Image Domain (CURRENT):**
  1. VK Integration: vk_group_id/vk_access_token, wall.post, 19 posts in club240792540
  2. Image Domain: ImagePromptEngine -> ImageEngine -> AssetManager -> ImageJob -> PublishJob
  3. Telegram sendPhoto: publish_photo() с data=payload, caption<=1024
  4. PublishJob: uses draft_text, multi-platform dispatcher
  5. StaticFiles: app.mount("/assets", StaticFiles)

### Critical Decisions Sprint 11
- Короткие EN промпты (<100 chars) - иначе Pollinations 0 bytes при URL>200
- data=payload вместо json=payload для Telegram sendPhoto
- extra_data = Column("metadata", JSON) - SQLAlchemy резервирует metadata
- host.docker.internal:11434 для Ollama из контейнера
- Retry 3 попытки backoff 2.0 в AssetManager

---

## 6. Real Code: Engines

### 6.1 TelegramPublisher LOW-LEVEL (engines/telegram/publisher.py)

`python
﻿"""Telegram Publisher тАФ ╨╛╤В╨┐╤А╨░╨▓╨║╨░ ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╨╣ ╤З╨╡╤А╨╡╨╖ Telegram Bot API."""

import re
import time
import logging
from typing import Optional

import requests


logger = logging.getLogger(__name__)


def _strip_markdown(text: str) -> str:
    """╨г╨┤╨░╨╗╤П╨╡╤В markdown, ╤З╤В╨╛╨▒╤Л Telegram ╨╜╨╡ ╨╛╤В╨║╨╗╨╛╨╜╤П╨╗ ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╤П."""
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    return text.strip()


class TelegramPublisher:
    """Telegram Bot API Publisher."""

    API_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def _url(self, method: str) -> str:
        return self.API_URL.format(token=self.bot_token, method=method)

    def get_me(self) -> dict:
        response = requests.get(self._url("getMe"), timeout=10)
        response.raise_for_status()
        return response.json()

    def get_chat(self) -> dict:
        response = requests.get(self._url("getChat"), params={"chat_id": self.chat_id}, timeout=10)
        response.raise_for_status()
        return response.json()

    def publish(self, text: str, retries: int = 3) -> dict:
        clean_text = _strip_markdown(text)
        if not clean_text:
            raise Exception("╨Я╤Г╤Б╤В╨╛╨╣ ╤В╨╡╨║╤Б╤В ╤Б╨╛╨╛╨▒╤Й╨╡╨╜╨╕╤П")

        message_id = self._send_message(clean_text, retries)
        if not message_id:
            raise Exception("Telegram ╨╜╨╡ ╨▓╨╡╤А╨╜╤Г╨╗ message_id")

        logger.info("Telegram published message_id=%s", message_id)
        return {
            "status": "published",
            "message_id": message_id,
            "chat_id": self.chat_id,
            "text_length": len(clean_text)
        }

    def _send_message(self, text: str, retries: int = 3) -> Optional[int]:
        payload = {"chat_id": self.chat_id, "text": text}

        for attempt in range(1, retries + 1):
            try:
                response = requests.post(self._url("sendMessage"), json=payload, timeout=30)
                data = response.json()

                if data.get("ok"):
                    return data["result"]["message_id"]

                error_code = data.get("error_code")
                description = data.get("description")
                logger.error("Telegram API error code=%s description=%s", error_code, description)

                if error_code == 429:
                    retry_after = data.get("parameters", {}).get("retry_after", 10)
                    logger.warning("Telegram flood limit. Waiting %s sec", retry_after)
                    time.sleep(retry_after)
                    continue

                return None

            except requests.exceptions.RequestException as e:
                logger.exception("Telegram network error attempt=%s error=%s", attempt, e)
                time.sleep(5)

        return None

    def publish_photo(self, text: str, image_url: str) -> dict:
        """╨Я╤Г╨▒╨╗╨╕╨║╤Г╨╡╤В ╨┐╨╛╤Б╤В ╤Б ╨║╨░╤А╤В╨╕╨╜╨║╨╛╨╣ ╤З╨╡╤А╨╡╨╖ Telegram sendPhoto API."""
        url = self._url("sendPhoto")

        # Telegram ╨╛╨│╤А╨░╨╜╨╕╤З╨╕╨▓╨░╨╡╤В caption 1024 ╤Б╨╕╨╝╨▓╨╛╨╗╨░╨╝╨╕
        clean_text = _strip_markdown(text)
        if len(clean_text) > 1024:
            clean_text = clean_text[:1021] + "..."

        payload = {
            "chat_id": self.chat_id,
            "photo": image_url,
            "caption": clean_text,
        }

        try:
            logger.info("=" * 60)
            logger.info("ЁЯУ╕ PUBLISH_PHOTO START")
            logger.info(f"   chat_id: {self.chat_id}")
            logger.info(f"   image_url: {image_url[:120]}...")
            logger.info(f"   image_url length: {len(image_url)} chars")
            logger.info(f"   caption length: {len(clean_text)} chars")
            logger.info("=" * 60)

            # ╨Т╨Р╨Ц╨Э╨Ю: data= ╨▓╨╝╨╡╤Б╤В╨╛ json= (Telegram ╨╛╨╢╨╕╨┤╨░╨╡╤В form-data)
            response = requests.post(url, data=payload, timeout=30)

            # ╨Ы╨╛╨│╨╕╤А╤Г╨╡╨╝ ╨╛╤В╨▓╨╡╤В ╨Я╨Х╨а╨Х╨Ф raise_for_status
            logger.info(f"   HTTP Status: {response.status_code}")
            logger.info(f"   Response headers: {dict(response.headers)}")
            logger.info(f"   Response body: {response.text[:500]}")

            data = response.json()

            if data.get("ok"):
                message_id = data["result"]["message_id"]
                logger.info(f"тЬЕ Photo sent successfully! message_id={message_id}")
                return {
                    "status": "success",
                    "message_id": message_id,
                    "chat_id": self.chat_id,
                    "text_length": len(clean_text)
                }
            else:
                error_code = data.get("error_code")
                description = data.get("description")
                logger.error(f"тЭМ Telegram API error: code={error_code}, desc={description}")

                # Flood control
                if error_code == 429:
                    retry_after = data.get("parameters", {}).get("retry_after", 10)
                    logger.warning(f"Flood control: waiting {retry_after} sec")
                    time.sleep(retry_after)
                    return self.publish_photo(text, image_url)

                # Fallback ╨║ ╤В╨╡╨║╤Б╤В╤Г
                logger.info("Falling back to text-only publish")
                return self.publish(text)

        except Exception as e:
            logger.error(f"тЭМ sendPhoto exception: {type(e).__name__}: {e}")
            logger.info("Falling back to text-only publish")
            return self.publish(text)
`

**Key:** publish_photo() uses data=payload (NOT json!), caption<=1024, fallback to text.

### 6.2 ImagePromptEngine (engines/image_prompt/engine.py)

`python
﻿"""Image Prompt Generator Engine - ╤Б╨╛╨╖╨┤╨░╨╡╤В ╨Ъ╨Ю╨а╨Ю╨в╨Ъ╨Ш╨Х ╨░╨╜╨│╨╗╨╕╨╣╤Б╨║╨╕╨╡ ╨┐╤А╨╛╨╝╨┐╤В╤Л."""
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ImagePromptEngine:
    """
    Sprint 11: ╨У╨╡╨╜╨╡╤А╨╕╤А╤Г╨╡╤В ╨Ъ╨Ю╨а╨Ю╨в╨Ъ╨Ш╨Х ╨░╨╜╨│╨╗╨╕╨╣╤Б╨║╨╕╨╡ ╨┐╤А╨╛╨╝╨┐╤В╤Л ╨┤╨╗╤П Image Generator.
    
    ╨Т╨Р╨Ц╨Э╨Ю: ╨Я╤А╨╛╨╝╨┐╤В╤Л ╨┤╨╛╨╗╨╢╨╜╤Л ╨▒╤Л╤В╤М ╨║╨╛╤А╨╛╤В╨║╨╕╨╝╨╕ (< 100 ╤Б╨╕╨╝╨▓╨╛╨╗╨╛╨▓) ╨╕ ╨╜╨░ ╨░╨╜╨│╨╗╨╕╨╣╤Б╨║╨╛╨╝,
    ╤З╤В╨╛╨▒╤Л URL ╨╜╨╡ ╨▒╤Л╨╗ ╤Б╨╗╨╕╤И╨║╨╛╨╝ ╨┤╨╗╨╕╨╜╨╜╤Л╨╝ ╨┤╨╗╤П Pollinations AI.
    """
    
    OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
    
    def __init__(self, model: str = "mistral-nemo:12b"):
        self.model = model
    
    def _call_ollama(self, prompt: str) -> str:
        """╨Я╤А╤П╨╝╨╛╨╣ ╨▓╤Л╨╖╨╛╨▓ Ollama API."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 50
                }
            }
            
            response = requests.post(self.OLLAMA_URL, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            return data.get("response", "").strip()
        
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            raise
    
    def generate_prompt(
        self,
        headline: str,
        text: str,
        platform: str = "telegram",
        language: str = "en",
        style: str = "anime"
    ) -> Dict[str, Any]:
        """
        ╨У╨╡╨╜╨╡╤А╨╕╤А╤Г╨╡╤В ╨Ъ╨Ю╨а╨Ю╨в╨Ъ╨Ш╨Щ ╨░╨╜╨│╨╗╨╕╨╣╤Б╨║╨╕╨╣ ╨┐╤А╨╛╨╝╨┐╤В (< 100 ╤Б╨╕╨╝╨▓╨╛╨╗╨╛╨▓).
        """
        try:
            # ╨Я╨╡╤А╨╡╨▓╨╛╨┤╨╕╨╝ headline ╨╜╨░ ╨░╨╜╨│╨╗╨╕╨╣╤Б╨║╨╕╨╣ ╨╕ ╤Б╨╛╨║╤А╨░╤Й╨░╨╡╨╝
            translation_prompt = f"""Translate this Russian anime news headline to English and create a SHORT image prompt (max 10 words). Output ONLY the prompt, no explanations.

Headline: {headline}

Short English image prompt:"""
            
            prompt = self._call_ollama(translation_prompt)
            
            # ╨Ю╤З╨╕╤Й╨░╨╡╨╝ ╨╕ ╨╛╨│╤А╨░╨╜╨╕╤З╨╕╨▓╨░╨╡╨╝ ╨┤╨╗╨╕╨╜╤Г
            prompt = prompt.strip().strip('"').strip("'")
            if len(prompt) > 100:
                prompt = prompt[:100]
            
            # ╨Ф╨╛╨▒╨░╨▓╨╗╤П╨╡╨╝ ╤Б╤В╨╕╨╗╤М
            prompt = f"{prompt}, anime style, high quality"
            
            logger.info(f"Generated SHORT prompt: {prompt}")
            
            return {
                "prompt": prompt,
                "negative_prompt": "text, letters, watermark, blurry",
                "style": style,
                "platform": platform,
                "language": "en"
            }
        
        except Exception as e:
            logger.exception(f"ImagePromptEngine failed: {e}")
            # Fallback: ╨╛╤З╨╡╨╜╤М ╨║╨╛╤А╨╛╤В╨║╨╕╨╣ ╨┐╤А╨╛╨╝╨┐╤В
            return {
                "prompt": "anime scene, high quality",
                "negative_prompt": "text, letters, watermark",
                "style": style,
                "platform": platform,
                "language": "en"
            }
    
    def generate_anime_prompt(self, anime_title: str, context: str = "") -> Dict[str, Any]:
        """╨б╨┐╨╡╤Ж╨╕╨░╨╗╨╕╨╖╨╕╤А╨╛╨▓╨░╨╜╨╜╤Л╨╣ ╨┐╤А╨╛╨╝╨┐╤В ╨┤╨╗╤П ╨░╨╜╨╕╨╝╨╡."""
        return {
            "prompt": f"{anime_title}, anime poster, high quality",
            "negative_prompt": "text, letters, watermark",
            "style": "anime",
            "platform": "telegram",
            "language": "en"
        }
`

**Key:** короткие EN промпты <100 chars через Ollama mistral-nemo:12b.
Критично: иначе Pollinations URL>200 -> 0 bytes. Fallback: 'anime scene, high quality'

### 6.3 ImageEngine (engines/image/engine.py)

`python
﻿"""Image Engine - ╨│╨╡╨╜╨╡╤А╨░╤Ж╨╕╤П ╨║╨░╤А╤В╨╕╨╜╨╛╨║ ╤З╨╡╤А╨╡╨╖ Pollinations AI."""
import logging
import urllib.parse
from typing import Dict, Any
from engines.image_prompt.engine import ImagePromptEngine

logger = logging.getLogger(__name__)


class ImageEngine:
    """
    Sprint 11: ╨У╨╡╨╜╨╡╤А╨╕╤А╤Г╨╡╤В ╨║╨░╤А╤В╨╕╨╜╨║╨╕ ╤З╨╡╤А╨╡╨╖ Pollinations AI.
    
    ╨Ш╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╤В ImagePromptEngine ╨┤╨╗╤П ╤Б╨╛╨╖╨┤╨░╨╜╨╕╤П ╨Ъ╨Ю╨а╨Ю╨в╨Ъ╨Ш╨е ╨░╨╜╨│╨╗╨╕╨╣╤Б╨║╨╕╤Е ╨┐╤А╨╛╨╝╨┐╤В╨╛╨▓,
    ╤З╤В╨╛╨▒╤Л URL ╨╜╨╡ ╨▒╤Л╨╗ ╤Б╨╗╨╕╤И╨║╨╛╨╝ ╨┤╨╗╨╕╨╜╨╜╤Л╨╝.
    """
    
    BASE_URL = "https://image.pollinations.ai/prompt/"
    
    def __init__(self):
        self.prompt_engine = ImagePromptEngine()
    
    def generate(
        self,
        headline: str,
        text: str,
        platform: str = "telegram",
        style: str = "anime",
        width: int = 1024,
        height: int = 576,
        model: str = "flux"
    ) -> Dict[str, Any]:
        """
        ╨У╨╡╨╜╨╡╤А╨╕╤А╤Г╨╡╤В URL ╨┤╨╗╤П Pollinations AI.
        
        Args:
            headline: ╨Ч╨░╨│╨╛╨╗╨╛╨▓╨╛╨║ ╨┐╨╛╤Б╤В╨░
            text: ╨в╨╡╨║╤Б╤В ╨┐╨╛╤Б╤В╨░
            platform: ╨Я╨╗╨░╤В╤Д╨╛╤А╨╝╨░
            style: ╨б╤В╨╕╨╗╤М
            width: ╨и╨╕╤А╨╕╨╜╨░
            height: ╨Т╤Л╤Б╨╛╤В╨░
            model: ╨Ь╨╛╨┤╨╡╨╗╤М
        
        Returns:
            {"image_url": str, "prompt": str, "style": str}
        """
        try:
            # ╨У╨╡╨╜╨╡╤А╨╕╤А╤Г╨╡╨╝ ╨║╨╛╤А╨╛╤В╨║╨╕╨╣ ╨┐╤А╨╛╨╝╨┐╤В ╤З╨╡╤А╨╡╨╖ ImagePromptEngine
            prompt_result = self.prompt_engine.generate_prompt(
                headline=headline,
                text=text,
                platform=platform,
                language="en",
                style=style
            )
            
            prompt = prompt_result["prompt"]
            
            # URL-encode ╨┐╤А╨╛╨╝╨┐╤В╨░
            encoded_prompt = urllib.parse.quote(prompt, safe='')
            
            # ╨Я╨░╤А╨░╨╝╨╡╤В╤А╤Л
            params = {
                "width": width,
                "height": height,
                "model": model,
                "nologo": "true"
            }
            
            query_string = urllib.parse.urlencode(params)
            image_url = f"{self.BASE_URL}{encoded_prompt}?{query_string}"
            
            logger.info(f"ImageEngine: Generated URL (prompt: {len(prompt)} chars, URL: {len(image_url)} chars)")
            logger.info(f"   Prompt: {prompt}")
            logger.info(f"   URL: {image_url[:100]}...")
            
            return {
                "image_url": image_url,
                "prompt": prompt,
                "style": style,
                "platform": platform
            }
        
        except Exception as e:
            logger.exception(f"ImageEngine generation failed: {e}")
            # Fallback: ╨╛╤З╨╡╨╜╤М ╨║╨╛╤А╨╛╤В╨║╨╕╨╣ ╨┐╤А╨╛╨╝╨┐╤В
            fallback_prompt = "anime scene, high quality"
            encoded = urllib.parse.quote(fallback_prompt, safe='')
            fallback_url = f"{self.BASE_URL}{encoded}?width={width}&height={height}&model={model}&nologo=true"
            
            return {
                "image_url": fallback_url,
                "prompt": fallback_prompt,
                "style": style,
                "platform": platform
            }
`

**Key:** URL = https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&model=flux&nologo=true

### 6.4 AssetManager (engines/asset/manager.py)

`python
﻿"""Asset Manager - ╤Б╨╛╤Е╤А╨░╨╜╤П╨╡╤В ╤Б╨│╨╡╨╜╨╡╤А╨╕╤А╨╛╨▓╨░╨╜╨╜╤Л╨╡ ╨╝╨╡╨┤╨╕╨░╤Д╨░╨╣╨╗╤Л."""
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional
import uuid
import time

from core.database import SessionLocal
from core.models.asset_orm import AssetORM

logger = logging.getLogger(__name__)


class AssetManager:
    """
    Sprint 11: ╨Ь╨╡╨╜╨╡╨┤╨╢╨╡╤А ╨┤╨╗╤П ╤Б╨╛╤Е╤А╨░╨╜╨╡╨╜╨╕╤П ╨╕ ╤Г╨┐╤А╨░╨▓╨╗╨╡╨╜╨╕╤П ╨╝╨╡╨┤╨╕╨░╤Д╨░╨╣╨╗╨░╨╝╨╕.
    
    ╨б╨║╨░╤З╨╕╨▓╨░╨╡╤В ╨╕╨╖╨╛╨▒╤А╨░╨╢╨╡╨╜╨╕╤П ╨┐╨╛ URL (Pollinations AI ╨╕ ╨┤╤А.) ╨╕ ╤Б╨╛╤Е╤А╨░╨╜╤П╨╡╤В ╨╗╨╛╨║╨░╨╗╤М╨╜╨╛.
    ╨Я╨╛╨┤╨┤╨╡╤А╨╢╨║╨░ retry ╤Б ╤Н╨║╤Б╨┐╨╛╨╜╨╡╨╜╤Ж╨╕╨░╨╗╤М╨╜╨╛╨╣ ╨╖╨░╨┤╨╡╤А╨╢╨║╨╛╨╣.
    """
    
    def __init__(self, base_dir: str = "/app/assets"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"AssetManager initialized: {self.base_dir}")
    
    def _download_with_retry(
        self,
        url: str,
        timeout: int = 120,
        max_retries: int = 3,
        backoff: float = 2.0
    ) -> requests.Response:
        """╨б╨║╨░╤З╨╕╨▓╨░╨╡╤В ╤Д╨░╨╣╨╗ ╤Б retry ╨╗╨╛╨│╨╕╨║╨╛╨╣."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Download attempt {attempt+1}/{max_retries}: {url[:80]}...")
                response = requests.get(url, timeout=timeout, stream=True)
                response.raise_for_status()
                
                # ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╨╝ content-type
                content_type = response.headers.get("content-type", "")
                if "image" not in content_type and "octet-stream" not in content_type:
                    logger.warning(f"Unexpected content-type: {content_type}")
                
                logger.info(f"тЬЕ Download successful ({len(response.content)} bytes)")
                return response
            
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = backoff ** attempt
                    logger.warning(f"Download failed (attempt {attempt+1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Download failed after {max_retries} attempts: {e}")
        
        raise last_error
    
    def save_from_url(
        self,
        image_url: str,
        content_id: str,
        prompt: str = "",
        model: str = "pollinations",
        seed: Optional[int] = None,
        width: int = 1024,
        height: int = 576
    ) -> Optional[AssetORM]:
        """╨б╨║╨░╤З╨╕╨▓╨░╨╡╤В ╨╕╨╖╨╛╨▒╤А╨░╨╢╨╡╨╜╨╕╨╡ ╨┐╨╛ URL ╨╕ ╤Б╨╛╤Е╤А╨░╨╜╤П╨╡╤В ╨╗╨╛╨║╨░╨╗╤М╨╜╨╛."""
        db = SessionLocal()
        try:
            asset_id = str(uuid.uuid4())
            date_path = datetime.utcnow().strftime("%Y/%m")
            filename = f"{asset_id}.png"
            storage_path = f"assets/{date_path}/{filename}"
            
            full_path = self.base_dir / date_path
            full_path.mkdir(parents=True, exist_ok=True)
            file_path = full_path / filename
            
            start_time = datetime.utcnow()
            
            # ╨б╨║╨░╤З╨╕╨▓╨░╨╡╨╝ ╤Б retry
            response = self._download_with_retry(image_url, timeout=120, max_retries=3)
            
            # ╨б╨╛╤Е╤А╨░╨╜╤П╨╡╨╝ ╤Д╨░╨╣╨╗
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            generation_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            file_size = file_path.stat().st_size
            
            # ╨Т╨░╨╗╨╕╨┤╨░╤Ж╨╕╤П: ╤Д╨░╨╣╨╗ ╨╜╨╡ ╨┤╨╛╨╗╨╢╨╡╨╜ ╨▒╤Л╤В╤М ╨┐╤Г╤Б╤В╤Л╨╝
            if file_size == 0:
                logger.error(f"Downloaded file is empty (0 bytes)")
                file_path.unlink()  # ╨г╨┤╨░╨╗╤П╨╡╨╝ ╨┐╤Г╤Б╤В╨╛╨╣ ╤Д╨░╨╣╨╗
                raise ValueError("Downloaded file is empty (0 bytes)")
            
            # ╨Т╨░╨╗╨╕╨┤╨░╤Ж╨╕╤П: ╨╝╨╕╨╜╨╕╨╝╨░╨╗╤М╨╜╤Л╨╣ ╤А╨░╨╖╨╝╨╡╤А ╨┤╨╗╤П ╨╕╨╖╨╛╨▒╤А╨░╨╢╨╡╨╜╨╕╤П (1KB)
            if file_size < 1024:
                logger.warning(f"File too small ({file_size} bytes), might be corrupted")
            
            public_url = f"/assets/{date_path}/{filename}"
            
            asset = AssetORM(
                id=asset_id,
                content_id=content_id,
                type="image",
                storage_path=storage_path,
                public_url=public_url,
                prompt=prompt,
                model=model,
                seed=seed,
                width=width,
                height=height,
                generation_time_ms=generation_time_ms,
                status="generated",
                extra_data={
                    "source": "pollinations",
                    "original_url": image_url,
                    "file_size_bytes": file_size
                }
            )
            
            db.add(asset)
            db.commit()
            db.refresh(asset)
            
            logger.info(f"Asset saved: {asset.id} -> {storage_path} ({generation_time_ms}ms, {file_size} bytes)")
            return asset
        
        except Exception as e:
            logger.exception(f"AssetManager.save_from_url failed: {e}")
            db.rollback()
            return None
        
        finally:
            db.close()
    
    def get_asset(self, asset_id: str) -> Optional[AssetORM]:
        """╨Я╨╛╨╗╤Г╤З╨░╨╡╤В asset ╨┐╨╛ ID."""
        db = SessionLocal()
        try:
            return db.query(AssetORM).filter(AssetORM.id == asset_id).first()
        finally:
            db.close()
    
    def get_assets_for_content(self, content_id: str) -> list:
        """╨Я╨╛╨╗╤Г╤З╨░╨╡╤В ╨▓╤Б╨╡ assets ╨┤╨╗╤П ╨║╨╛╨╜╤В╨╡╨╜╤В╨░."""
        db = SessionLocal()
        try:
            return db.query(AssetORM).filter(
                AssetORM.content_id == content_id
            ).order_by(AssetORM.created_at.desc()).all()
        finally:
            db.close()
`

**Key:** _download_with_retry (3 попытки, backoff 2.0, timeout 120s)
Validation: file_size>1KB. Saves /app/assets/YYYY/MM/uuid.png.
extra_data вместо metadata. Creates AssetORM, updates content.asset_id.

### 6.5 TelegramEngine wrapper (engines/telegram/engine.py)

`python
﻿import logging
from datetime import datetime

from .publisher import TelegramPublisher
from .models import TelegramPublishResult
from .exceptions import TelegramPublishError


logger = logging.getLogger(__name__)


class TelegramEngine:
    """
    Engine layer for Telegram publishing.
    Hides Telegram API implementation from automation layer.
    """

    def publish(self, text: str, bot_token: str, chat_id: str) -> TelegramPublishResult:
        try:
            publisher = TelegramPublisher(bot_token=bot_token, chat_id=chat_id)
            result = publisher.publish(text)
            return TelegramPublishResult(
                status=result["status"],
                message_id=result["message_id"],
                chat_id=result["chat_id"],
                published_at=datetime.utcnow(),
                text_length=result["text_length"]
            )
        except Exception as e:
            logger.exception("Telegram publish failed")
            raise TelegramPublishError(str(e))

    def publish_photo(self, text: str, image_url: str, bot_token: str, chat_id: str) -> TelegramPublishResult:
        try:
            publisher = TelegramPublisher(bot_token=bot_token, chat_id=chat_id)
            result = publisher.publish_photo(text=text, image_url=image_url)
            return TelegramPublishResult(
                status=result["status"],
                message_id=result["message_id"],
                chat_id=result["chat_id"],
                published_at=datetime.utcnow(),
                text_length=result["text_length"]
            )
        except Exception as e:
            logger.exception("Telegram publish_photo failed")
            raise TelegramPublishError(str(e))
`


---

## 7. Real Code: Jobs

### 7.1 ImageJob (backend/automation/jobs/image_job.py)

`python
﻿"""Image Job - ╨│╨╡╨╜╨╡╤А╨░╤Ж╨╕╤П ╨║╨░╤А╤В╨╕╨╜╨╛╨║ ╨┤╨╗╤П ╨┐╨╛╤Б╤В╨╛╨▓."""
import logging
from typing import Any
from core.database import SessionLocal
from core.repositories.content_repository import ContentRepository
from engines.image.engine import ImageEngine

logger = logging.getLogger(__name__)


class ImageJob:
    """
    Sprint 11: ╨У╨╡╨╜╨╡╤А╨╕╤А╤Г╨╡╤В ╨║╨░╤А╤В╨╕╨╜╨║╨╕ ╨┤╨╗╤П approved ╨┐╨╛╤Б╤В╨╛╨▓.
    
    ╨Ш╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╤В ImageEngine ╨┤╨╗╤П ╤Б╨╛╨╖╨┤╨░╨╜╨╕╤П URL ╤З╨╡╤А╨╡╨╖ Pollinations AI.
    ╨б╨╛╤Е╤А╨░╨╜╤П╨╡╤В image_url ╨▓ content ╨┤╨╗╤П ╨┐╨╛╤Б╨╗╨╡╨┤╤Г╤О╤Й╨╡╨╣ ╨┐╤Г╨▒╨╗╨╕╨║╨░╤Ж╨╕╨╕.
    """
    
    def run(self, channel=None, execution_id: str = None) -> dict[str, Any]:
        logger.info("ImageJob started")
        
        db = SessionLocal()
        processed = 0
        generated = 0
        failed = 0
        
        try:
            repo = ContentRepository(db)
            
            # ╨С╨╡╤А╤С╨╝ approved ╨┐╨╛╤Б╤В╤Л ╨С╨Х╨Ч image_url
            items = repo.list_all(status="approved", limit=10)
            items = [i for i in items if not getattr(i, 'image_url', None)]
            
            logger.info(f"Items without images: {len(items)}")
            
            if not items:
                logger.info("No items need images")
                return {"status": "ok", "processed": 0, "generated": 0, "failed": 0}
            
            image_engine = ImageEngine()
            
            for item in items:
                try:
                    processed += 1
                    
                    logger.info(f"Generating image for: {item.headline[:50]}...")
                    
                    # ╨У╨╡╨╜╨╡╤А╨╕╤А╤Г╨╡╨╝ image_url ╤З╨╡╤А╨╡╨╖ ImageEngine
                    result = image_engine.generate(
                        headline=item.headline,
                        text=item.draft_text or "",
                        platform="telegram",
                        style="anime"
                    )
                    
                    if result and result.get("image_url"):
                        item.image_url = result["image_url"]
                        item.image_prompt = result.get("prompt", "")
                        db.commit()
                        generated += 1
                        logger.info(f"тЬЕ Image URL generated for {item.id}")
                        logger.info(f"   URL: {result['image_url'][:80]}...")
                    else:
                        logger.warning(f"Failed to generate image for {item.id}")
                        failed += 1
                
                except Exception as e:
                    logger.exception(f"Image generation failed for {item.id}: {e}")
                    failed += 1
                    db.rollback()
            
            logger.info(f"ImageJob finished: processed={processed}, generated={generated}, failed={failed}")
            return {
                "status": "ok",
                "processed": processed,
                "generated": generated,
                "failed": failed
            }
        
        except Exception as e:
            logger.exception(f"ImageJob failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()
`

**Key:** approved posts без image_url (limit 10) -> ImageEngine -> image_url/image_prompt.

### 7.2 Jobs Registry (backend/automation/jobs/__init__.py)

`python
﻿from .automation_jobs import (
    ResearchJob,
    DecisionJob,
    WritingJob,
    EvaluatorJob,
    PublishJob,
)
from .image_job import ImageJob
from .revision_job import RevisionJob
from .re_evaluation_job import ReEvaluationJob

__all__ = [
    "ResearchJob",
    "DecisionJob",
    "WritingJob",
    "EvaluatorJob",
    "PublishJob",
    "ImageJob",
    "RevisionJob",
    "ReEvaluationJob",
]
`

**ВАЖНО:** все 8 классов экспортируются - не удалять!

---

## 8. Real Code: Publishers

### 8.1 TelegramPublisher automation layer (backend/automation/publishers/telegram.py)

`python
﻿"""Telegram Publisher."""
from .base import PublisherInterface, PublishResult
from engines.telegram.engine import TelegramEngine
from datetime import datetime
from typing import Any
import logging


logger = logging.getLogger(__name__)


class TelegramPublisher(PublisherInterface):
    """Publisher ╨┤╨╗╤П Telegram."""

    def __init__(self):
        self.engine = TelegramEngine()

    @property
    def platform_name(self) -> str:
        return "telegram"

    def validate_credentials(self, credentials: dict) -> bool:
        """╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╤В ╤З╤В╨╛ ╨╡╤Б╤В╤М bot_token ╨╕ chat_id."""
        return bool(
            credentials.get("bot_token") and
            credentials.get("chat_id")
        )

    def publish(
        self,
        text: str,
        credentials: dict,
        channel: Any = None,
        **kwargs
    ) -> PublishResult:
        """╨Я╤Г╨▒╨╗╨╕╨║╤Г╨╡╤В ╤В╨╡╨║╤Б╤В ╨▓ Telegram (╤Б ╨┐╨╛╨┤╨┤╨╡╤А╨╢╨║╨╛╨╣ ╨║╨░╤А╤В╨╕╨╜╨╛╨║)."""

        if not self.validate_credentials(credentials):
            return PublishResult(
                success=False,
                error="Missing bot_token or chat_id"
            )

        # Sprint 11: ╨┐╨╛╨┤╨┤╨╡╤А╨╢╨║╨░ ╨║╨░╤А╤В╨╕╨╜╨╛╨║ ╤З╨╡╤А╨╡╨╖ image_url
        image_url = kwargs.get('image_url')
        
        try:
            if image_url:
                # ╨Я╤Г╨▒╨╗╨╕╨║╤Г╨╡╨╝ ╤Б ╨║╨░╤А╤В╨╕╨╜╨║╨╛╨╣ ╤З╨╡╤А╨╡╨╖ sendPhoto
                logger.info(f"Publishing with image: {image_url[:80]}...")
                result = self.engine.publish_photo(
                    text=text,
                    image_url=image_url,
                    bot_token=credentials["bot_token"],
                    chat_id=credentials["chat_id"]
                )
            else:
                # ╨Ю╨▒╤Л╤З╨╜╨░╤П ╨┐╤Г╨▒╨╗╨╕╨║╨░╤Ж╨╕╤П ╤В╨╡╨║╤Б╤В╨╛╨╝
                result = self.engine.publish(
                    text=text,
                    bot_token=credentials["bot_token"],
                    chat_id=credentials["chat_id"]
                )

            return PublishResult(
                success=True,
                message_id=str(result.message_id),
                published_at=result.published_at,
                platform_data={
                    "telegram_message_id": result.message_id,
                    "has_image": bool(image_url)
                }
            )

        except Exception as e:
            logger.error(f"Telegram publish failed: {e}")
            return PublishResult(
                success=False,
                error=str(e)
            )
`

**Key:** wrapper over engines.telegram.publisher, принимает image_url через kwargs.

### 8.2 VkPublisher (backend/automation/publishers/vk.py)

`python
﻿"""VK Publisher - ╤А╨╡╨░╨╗╤М╨╜╨░╤П ╨╕╨╜╤В╨╡╨│╤А╨░╤Ж╨╕╤П ╤Б VK API."""
import requests
from datetime import datetime
from typing import Any
import logging

from .base import PublisherInterface, PublishResult


logger = logging.getLogger(__name__)


class VkPublisher(PublisherInterface):
    """
    Sprint 11: Publisher ╨┤╨╗╤П VK (╨Т╨Ъ╨╛╨╜╤В╨░╨║╤В╨╡).
    
    ╨Ш╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╤В VK API ╨╝╨╡╤В╨╛╨┤ wall.post ╨┤╨╗╤П ╨┐╤Г╨▒╨╗╨╕╨║╨░╤Ж╨╕╨╕ ╨┐╨╛╤Б╤В╨╛╨▓ ╨▓ ╨│╤А╤Г╨┐╨┐╨╡.
    
    API ╨┤╨╛╨║╤Г╨╝╨╡╨╜╤В╨░╤Ж╨╕╤П: https://dev.vk.com/ru/method/wall.post
    
    ╨в╤А╨╡╨▒╤Г╨╡╨╝╤Л╨╡ credentials:
        - group_id: ID ╨│╤А╤Г╨┐╨┐╤Л VK (╨╜╨░╨┐╤А╨╕╨╝╨╡╤А: -123456789 ╨╕╨╗╨╕ 123456789)
        - access_token: Access token ╤Б ╨┐╤А╨░╨▓╨░╨╝╨╕ wall, groups
    """
    
    VK_API_URL = "https://api.vk.com/method/wall.post"
    VK_API_VERSION = "5.199"
    
    @property
    def platform_name(self) -> str:
        return "vk"
    
    def validate_credentials(self, credentials: dict) -> bool:
        """╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╤В ╨╜╨░╨╗╨╕╤З╨╕╨╡ group_id ╨╕ access_token."""
        return bool(
            credentials.get("group_id") and
            credentials.get("access_token")
        )
    
    def publish(
        self,
        text: str,
        credentials: dict,
        channel: Any = None,
        **kwargs
    ) -> PublishResult:
        """
        ╨Я╤Г╨▒╨╗╨╕╨║╤Г╨╡╤В ╨┐╨╛╤Б╤В ╨▓ VK ╨│╤А╤Г╨┐╨┐╤Г ╤З╨╡╤А╨╡╨╖ wall.post.
        
        Args:
            text: ╨в╨╡╨║╤Б╤В ╨┐╨╛╤Б╤В╨░
            credentials: {
                "group_id": str,      # ID ╨│╤А╤Г╨┐╨┐╤Л (╤Б ╨╝╨╕╨╜╤Г╤Б╨╛╨╝ ╨┤╨╗╤П ╨│╤А╤Г╨┐╨┐)
                "access_token": str   # VK access token
            }
            channel: Channel ╨╛╨▒╤К╨╡╨║╤В (╨╛╨┐╤Ж╨╕╨╛╨╜╨░╨╗╤М╨╜╨╛)
            **kwargs: ╨Ф╨╛╨┐╨╛╨╗╨╜╨╕╤В╨╡╨╗╤М╨╜╤Л╨╡ ╨┐╨░╤А╨░╨╝╨╡╤В╤А╤Л (attachments, ╨╕ ╤В.╨┤.)
        
        Returns:
            PublishResult ╤Б post_id ╨╕ published_at
        """
        if not self.validate_credentials(credentials):
            logger.error("VK: Missing group_id or access_token")
            return PublishResult(
                success=False,
                error="Missing group_id or access_token"
            )
        
        group_id = credentials["group_id"]
        access_token = credentials["access_token"]
        
        # ╨Х╤Б╨╗╨╕ group_id ╨▒╨╡╨╖ ╨╝╨╕╨╜╤Г╤Б╨░ тАФ ╨┤╨╛╨▒╨░╨▓╨╗╤П╨╡╨╝ (╨┤╨╗╤П ╨│╤А╤Г╨┐╨┐ ╨╜╤Г╨╢╨╡╨╜ ╨╛╤В╤А╨╕╤Ж╨░╤В╨╡╨╗╤М╨╜╤Л╨╣ owner_id)
        owner_id = str(group_id)
        if not owner_id.startswith("-") and not owner_id.startswith("club"):
            owner_id = f"-{owner_id}"
        
        try:
            logger.info(f"VK: Publishing to group {owner_id}")
            
            # VK API wall.post
            payload = {
                "owner_id": owner_id,
                "from_group": 1,  # ╨Я╤Г╨▒╨╗╨╕╨║╨░╤Ж╨╕╤П ╨╛╤В ╨╕╨╝╨╡╨╜╨╕ ╨│╤А╤Г╨┐╨┐╤Л
                "message": text,
                "access_token": access_token,
                "v": self.VK_API_VERSION,
            }
            
            # ╨Ф╨╛╨▒╨░╨▓╨╗╤П╨╡╨╝ ╨┤╨╛╨┐╨╛╨╗╨╜╨╕╤В╨╡╨╗╤М╨╜╤Л╨╡ ╨┐╨░╤А╨░╨╝╨╡╤В╤А╤Л (attachments, ╨╕ ╤В.╨┤.)
            for key in ["attachments", "services", "signed", "publish_date", 
                       "lat", "long", "place_id", "post_id", "guid", 
                       "mark_as_ads", "close_comments", "donut_paid_duration",
                       "mute_notifications", "copyright"]:
                if key in kwargs:
                    payload[key] = kwargs[key]
            
            response = requests.post(
                self.VK_API_URL,
                data=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # ╨Я╤А╨╛╨▓╨╡╤А╤П╨╡╨╝ ╨╛╤И╨╕╨▒╨║╨╕ VK API
            if "error" in data:
                error = data["error"]
                error_msg = f"VK API error {error.get('error_code')}: {error.get('error_msg')}"
                logger.error(error_msg)
                return PublishResult(
                    success=False,
                    error=error_msg
                )
            
            # ╨г╤Б╨┐╨╡╤Е тАФ ╨┐╨╛╨╗╤Г╤З╨░╨╡╨╝ post_id
            post_id = data.get("response", {}).get("post_id")
            if post_id:
                full_post_id = f"{owner_id}_{post_id}"
                logger.info(f"VK: Published successfully. Post ID: {full_post_id}")
                return PublishResult(
                    success=True,
                    message_id=full_post_id,
                    published_at=datetime.utcnow(),
                    platform_data={
                        "vk_post_id": full_post_id,
                        "vk_owner_id": owner_id,
                        "vk_post_number": post_id
                    }
                )
            else:
                logger.error("VK: No post_id in response")
                return PublishResult(
                    success=False,
                    error="No post_id in VK API response"
                )
        
        except requests.exceptions.Timeout:
            logger.error("VK: Request timeout")
            return PublishResult(success=False, error="VK API timeout")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"VK: Connection error: {e}")
            return PublishResult(success=False, error=f"Connection error: {str(e)}")
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"VK: HTTP error: {e}")
            return PublishResult(success=False, error=f"HTTP error: {str(e)}")
        
        except Exception as e:
            logger.exception(f"VK: Unexpected error: {e}")
            return PublishResult(success=False, error=str(e))
    
    def get_post_url(self, owner_id: str, post_id: str) -> str:
        """╨Т╨╛╨╖╨▓╤А╨░╤Й╨░╨╡╤В URL ╨┐╨╛╤Б╤В╨░ ╨▓ VK."""
        # ╨г╨▒╨╕╤А╨░╨╡╨╝ ╨╝╨╕╨╜╤Г╤Б ╨╕╨╖ owner_id ╨┤╨╗╤П URL
        clean_owner_id = owner_id.lstrip("-")
        return f"https://vk.com/wall{owner_id}_{post_id}"
`

**Key:** wall.post, vk_group_id (negative), vk_access_token, v=5.199

---

## 9. Real Code: Runner (Workflow)

### 9.1 AutomationRunner (backend/automation/runner.py)

`python
﻿import asyncio
import logging
from datetime import datetime

from .jobs import (
    ResearchJob,
    DecisionJob,
    WritingJob,
    EvaluatorJob,
    PublishJob,
    RevisionJob,
    ReEvaluationJob,
)
from .workflow_engine_v2 import WorkflowEngineV2
from .runtime import WorkflowRuntime
from core.database import SessionLocal
from core.models.workflow_orm import WorkflowORM


logger = logging.getLogger(__name__)


class AutomationRunner:

    def __init__(self):

        logger.info(
            "AutomationRunner initialized"
        )

        self.stage_map = {
            "research": ResearchJob,
            "decision": DecisionJob,
            "writing": WritingJob,
            "evaluation": EvaluatorJob,
            "revision": RevisionJob,
            "re_evaluation": ReEvaluationJob,
            "publish": PublishJob,
        }
        
        # Маппинг node_type (из workflow definition) на Job classes
        # Поддерживает разные названия: "writing" или "brief", "evaluator" или "evaluation"
        self.node_type_to_job = {
            "research": ResearchJob,
            "decision": DecisionJob,
            "writing": WritingJob,
            "brief": WritingJob,  # alias для writing
            "evaluation": EvaluatorJob,
            "evaluator": EvaluatorJob,  # alias для evaluation
            "publish": PublishJob,
            "publisher": PublishJob,  # alias для publish
            # Future: "fact_checker": FactCheckJob, "image": ImageJob, etc.
        }



    async def retry_stage(self, channel, stage_name: str, execution_id: str) -> dict:
        """Повторяет один конкретный этап пайплайна для канала."""
        if stage_name not in self.stage_map:
            return {"status": "failed", "error": f"Unknown stage: {stage_name}"}

        job_class = self.stage_map[stage_name]
        job = job_class()

        logger.info(
            "Retrying stage=%s channel=%s execution_id=%s",
            stage_name,
            getattr(channel, "name", None),
            execution_id
        )

        try:
            import inspect
            if inspect.iscoroutinefunction(job.run):
                job_result = await job.run(channel=channel, execution_id=execution_id)
            else:
                job_result = await asyncio.to_thread(job.run, channel=channel, execution_id=execution_id)
            return job_result
        except Exception as e:
            logger.exception("Retry failed %s", stage_name)
            return {"status": "failed", "error": str(e)}

    async def run_now(self, channel=None, workflow_id: str = None) -> dict:
        """
        Sprint 8.4.1: Запускает pipeline для канала.
        Если workflow_id указан — делегирует WorkflowRuntime (универсальный исполнитель графов).
        Если не указан — fallback на hardcoded список (обратная совместимость).
        """
        execution_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        if channel:
            execution_id = f"{execution_id}-{channel.id}"

        logger.info("Automation started execution_id=%s channel=%s",
                    execution_id, getattr(channel, "name", None))

        result = {
            "execution_id": execution_id,
            "channel": {
                "id": getattr(channel, "id", None),
                "name": getattr(channel, "name", None),
                "platform": getattr(channel, "platform", None)
            } if channel else None
        }

        # Sprint 8.4.1: если есть workflow_id — делегируем WorkflowRuntime
        if workflow_id:
            logger.info("Using WorkflowRuntime for workflow %s", workflow_id)
            runtime = WorkflowRuntime()
            runtime_result = await runtime.execute(
                workflow_id=workflow_id,
                channel=channel,
                execution_id=execution_id
            )

            result["workflow_id"] = workflow_id
            result["workflow_name"] = runtime_result.workflow_name
            result["status"] = runtime_result.status
            if runtime_result.error:
                result["error"] = runtime_result.error

            for node_id, node_result in runtime_result.node_results.items():
                result[node_id] = {
                    "status": node_result.status.value,
                    "output": node_result.output,
                    "error": node_result.error,
                    "metrics": node_result.metrics
                }
            return result

        # Fallback: старый hardcoded список (для каналов без workflow_id)
        logger.info("No workflow_id provided, using hardcoded job list")
        jobs = [
            ("research", ResearchJob()),
            ("decision", DecisionJob()),
            ("writing", WritingJob()),
            ("evaluation", EvaluatorJob()),
            ("revision", RevisionJob()),
            ("re_evaluation", ReEvaluationJob()),
            ("publish", PublishJob()),
        ]

        for name, job in jobs:
            logger.info("Starting job=%s channel=%s", name, getattr(channel, "name", None))
            try:
                import inspect
                if inspect.iscoroutinefunction(job.run):
                    job_result = await job.run(channel=channel, execution_id=execution_id)
                else:
                    job_result = await asyncio.to_thread(job.run, channel=channel, execution_id=execution_id)
                result[name] = job_result
                logger.info("Job %s completed: %s", name, job_result.get("status", "unknown"))
            except Exception as e:
                logger.exception("Job %s failed", name)
                result[name] = {"status": "failed", "error": str(e)}
                result["status"] = "failed"
                break

        return result
`

**Key:** stage_map (stage_name -> Job), node_type_to_job (с алиасами),
run_now() с fallback jobs list: research->decision->writing->evaluation->publish.

---

## 10. Real Code: ORM Models

### 10.1 AssetORM (core/models/asset_orm.py)

`python
﻿"""Asset ORM model for storing generated media."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON

from core.database import Base


class AssetORM(Base):
    """
    Sprint 11: Asset model for storing generated images/videos.
    
    Stores metadata about generated media files (prompts, models, seeds, etc).
    Linked to content via content_id.
    
    NOTE: SQLAlchemy ╤А╨╡╨╖╨╡╤А╨▓╨╕╤А╤Г╨╡╤В ╨╕╨╝╤П 'metadata' ╨┤╨╗╤П Base.metadata,
    ╨┐╨╛╤Н╤В╨╛╨╝╤Г ╨╕╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╨╝ ╨░╤В╤А╨╕╨▒╤Г╤В 'extra_data' ╨║╨╛╤В╨╛╤А╤Л╨╣ ╨╝╨░╨┐╨┐╨╕╤В╤Б╤П ╨╜╨░ ╨║╨╛╨╗╨╛╨╜╨║╤Г 'metadata'.
    """
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String, ForeignKey("content.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String, nullable=False, default="image")  # image/video/audio
    storage_path = Column(String, nullable=False)  # assets/2026/07/uuid.png
    public_url = Column(String, nullable=True)
    prompt = Column(Text, nullable=True)
    model = Column(String, nullable=True)  # flux/sdxl/comfyui
    seed = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    generation_time_ms = Column(Integer, nullable=True)
    status = Column(String, default="generated")  # generating/generated/failed
    # SQLAlchemy ╤А╨╡╨╖╨╡╤А╨▓╨╕╤А╤Г╨╡╤В 'metadata' тАФ ╨╕╤Б╨┐╨╛╨╗╤М╨╖╤Г╨╡╨╝ 'extra_data' ╤Б ╨╝╨░╨┐╨┐╨╕╨╜╨│╨╛╨╝ ╨╜╨░ ╨║╨╛╨╗╨╛╨╜╨║╤Г 'metadata'
    extra_data = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AssetORM(id={self.id}, type={self.type}, status={self.status})>"
`

**ВАЖНО:** extra_data = Column("metadata", JSON) - SQLAlchemy резервирует metadata.

### 10.2 ContentORM (core/models/content_orm.py)

`python
﻿import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean, ForeignKey

from core.database import Base


class ContentORM(Base):
    """ORM-╨╝╨╛╨┤╨╡╨╗╤М ╨╡╨┤╨╕╨╜╨╕╤Ж╤Л ╨║╨╛╨╜╤В╨╡╨╜╤В╨░ (╨┐╨╛╤Б╤В/╤В╨╡╨╝╨░) ╨▓ ╨╢╨╕╨╖╨╜╨╡╨╜╨╜╨╛╨╝ ╤Ж╨╕╨║╨╗╨╡ research -> published."""
    __tablename__ = "content"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    channel_id = Column(
        String,
        nullable=True,
        index=True
    )  # nullable ╨┤╨╗╤П ╤Б╤В╨░╤А╤Л╤Е ╨┤╨╡╨╝╨╛-╨╖╨░╨┐╨╕╤Б╨╡╨╣ ╨▒╨╡╨╖ ╨║╨░╨╜╨░╨╗╨░

    source_url = Column(
        String,
        nullable=False
    )

    headline = Column(
        String,
        nullable=False
    )

    source_text = Column(
        Text,
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        default="research"
    )

    prompt_version = Column(
        String,
        nullable=True
    )

    draft_text = Column(
        String,
        nullable=True
    )


    asset_id = Column(String, ForeignKey("assets.id"), nullable=True)  # Sprint 11
    image_url = Column(String(500), nullable=True)  # Sprint 11
    image_prompt = Column(Text, nullable=True)  # Sprint 11
    # Telegram publishing metadata
    telegram_message_id = Column(
        String,
        nullable=True
    )

    published_at = Column(
        DateTime,
        nullable=True
    )

    publish_error = Column(
        Text,
        nullable=True
    )

    fact_score = Column(
        Integer,
        nullable=True
    )

    quality_score = Column(
        Integer,
        nullable=True
    )

    revision_count = Column(
        Integer,
        default=0
    )

    last_revision_reason = Column(
        Text,
        nullable=True
    )


    # === WritingEngine v2 fields ===
    validation_issues = Column(
        JSON,
        nullable=True,
        default=list
    )

    fact_check_passed = Column(
        Boolean,
        nullable=True,
        default=True
    )

    model_used = Column(
        String(100),
        nullable=True,
        default=""
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
`

**Key:** image_url, image_prompt, asset_id FK, status lifecycle.

### 10.3 ChannelORM (core/models/channel_orm.py)

`python
﻿import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey

from core.database import Base


class ChannelORM(Base):
    """
    ORM-модель канала в PostgreSQL.
    Pydantic-модель ChannelConfig (core/models/channel.py) остаётся
    доменным/API контрактом и не меняется.
    """
    __tablename__ = "channels"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    platform = Column(String, default="telegram")
    language_search = Column(String, default="en")
    language_publish = Column(String, default="ru")
    style_profile = Column(String, default="minimal")
    timezone = Column(String, default="UTC")
    description = Column(String, nullable=True)

    bot_token = Column(String, nullable=True)
    chat_id = Column(String, nullable=True)
    # Sprint 11: VK credentials
    vk_group_id = Column(String(50), nullable=True)
    vk_access_token = Column(String(255), nullable=True)

    # Sprint 11: YouTube credentials
    youtube_channel_id = Column(String(100), nullable=True)
    youtube_api_key = Column(String(255), nullable=True)
    youtube_access_token = Column(String, nullable=True)
    youtube_refresh_token = Column(String, nullable=True)

    # Sprint 11: Dzen credentials
    dzen_channel_id = Column(String(100), nullable=True)
    dzen_api_key = Column(String(255), nullable=True)

    is_connected = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    workflow_id = Column(String, nullable=True, index=True)

    # Sprint 8.2: ссылки на шаблон и профиль
    template_id = Column(String, ForeignKey("channel_templates.id"), nullable=True, index=True)
    profile_id = Column(String, ForeignKey("channel_profiles.id"), nullable=True, index=True)

    # Источники храним как JSON-массив (для MVP; отдельная таблица - если понадобится позже)
    sources = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
`

**Key:** Telegram (bot_token, chat_id), VK (vk_group_id, vk_access_token), sources JSON.

---

## 11. Image Domain Pipeline (полный поток)
`
Content (status=approved, image_url=None)
  -> ImageJob.run()
  -> ImagePromptEngine.generate_prompt(headline, draft_text)
     # Ollama переводит RU -> EN, короткие промпты <100 chars
     -> image_prompt (EN, avg 62 chars)
  -> ImageEngine.generate(prompt)
     -> image_url (avg 168 chars)
  -> AssetManager.save_from_url(image_url)
     # Download + retry (3 попытки) + save to /app/assets/
     -> asset (AssetORM)
  -> Content.image_url = image_url
  -> Content.asset_id = asset.id
  -> PublishJob.run()
  -> TelegramPublisher.publish(text, image_url, credentials)
  -> POST https://api.telegram.org/bot{token}/sendPhoto
     data={  # ВАЖНО: data=, не json=
       "chat_id": chat_id,
       "photo": image_url,
       "caption": text[:1024]
     }
  -> Post с картинкой в Telegram
`

---

## 12. Database Schema

### channels
| Column | Type | Note |
|--------|------|------|
| id | VARCHAR PK | UUID |
| name | VARCHAR | |
| platform | VARCHAR | telegram/vk/youtube/dzen |
| bot_token, chat_id | VARCHAR | Telegram |
| vk_group_id, vk_access_token | VARCHAR | VK |
| is_connected, is_active | BOOLEAN | |
| style_profile, language_publish | VARCHAR | |
| workflow_id | VARCHAR FK | |
| sources | JSON | KnowledgeSource[] |

### content
| Column | Type | Note |
|--------|------|------|
| id | VARCHAR PK | |
| channel_id | VARCHAR FK | |
| source_url | VARCHAR NOT NULL | |
| headline, source_text | TEXT | |
| status | VARCHAR | research/draft/needs_revision/approved/published/rejected |
| draft_text | TEXT | generated |
| quality_score | INTEGER | 0-100 |
| image_url | VARCHAR(500) | Pollinations |
| image_prompt | TEXT | prompt used |
| asset_id | VARCHAR FK | -> assets |
| telegram_message_id | VARCHAR | |
| published_at | TIMESTAMP | |

### assets
| Column | Type | Note |
|--------|------|------|
| id | VARCHAR PK | |
| content_id | VARCHAR FK | |
| type | VARCHAR | image/video/audio |
| storage_path | VARCHAR | assets/2026/08/uuid.png |
| public_url | VARCHAR | /assets/... |
| prompt, model | VARCHAR/TEXT | |
| seed, width, height | INTEGER | |
| generation_time_ms | INTEGER | |
| status | VARCHAR | generating/generated/failed |
| extra_data | JSON | maps to "metadata" column |

### Production Stats
`
﻿        tbl        | count 
-------------------+-------
 channels          |     4
 content           |  1345
 content_published |   486
 content_approved  |   673
 assets            |     2
 workflows         |     4
 channel_schedules |     4
 execution_logs    |  2905
(8 rows)
`

---

## 13. Workflow Templates
`
﻿             name             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    definition                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Simple                       | {"nodes": [{"id": "research", "type": "research", "config": {}, "status": "pending", "output": null}, {"id": "writing", "type": "writing", "config": {}, "status": "pending", "output": null}, {"id": "evaluation", "type": "evaluation", "config": {}, "status": "pending", "output": null}, {"id": "publish", "type": "publish", "config": {}, "status": "pending", "output": null}], "edges": [{"source_node_id": "research", "target_node_id": "writing"}, {"source_node_id": "writing", "target_node_id": "evaluation"}, {"source_node_id": "evaluation", "target_node_id": "publish"}]}
 Default Full                 | {"nodes": [{"id": "research", "type": "research", "config": {}, "status": "pending", "output": null}, {"id": "decision", "type": "decision", "config": {}, "status": "pending", "output": null}, {"id": "writing", "type": "writing", "config": {}, "status": "pending", "output": null}, {"id": "evaluation", "type": "evaluation", "config": {}, "status": "pending", "output": null}, {"id": "revision", "type": "revision", "config": {}, "status": "pending", "output": null}, {"id": "re_evaluation", "type": "re_evaluation", "config": {}, "status": "pending", "output": null}, {"id": "publish", "type": "publish", "config": {}, "status": "pending", "output": null}], "edges": [{"source_node_id": "research", "target_node_id": "decision"}, {"source_node_id": "decision", "target_node_id": "writing"}, {"source_node_id": "writing", "target_node_id": "evaluation"}, {"source_node_id": "evaluation", "target_node_id": "revision"}, {"source_node_id": "revision", "target_node_id": "re_evaluation"}, {"source_node_id": "re_evaluation", "target_node_id": "publish"}]}
 Research Only                | {"nodes": [{"id": "research", "type": "research", "config": {}, "status": "pending", "output": null}], "edges": []}
 Telegram Research to Publish | {"id": "telegram-default", "name": "Telegram Research to Publish", "description": "Research -> Decision -> Writing -> Fact Check -> Image -> Review -> Telegram", "nodes": [{"id": "research", "type": "research", "config": {}, "status": "pending", "output": null}, {"id": "decision", "type": "decision", "config": {}, "status": "pending", "output": null}, {"id": "writing", "type": "brief", "config": {}, "status": "pending", "output": null}, {"id": "fact_check", "type": "fact_checker", "config": {}, "status": "pending", "output": null}, {"id": "image", "type": "image", "config": {}, "status": "pending", "output": null}, {"id": "review", "type": "evaluator", "config": {}, "status": "pending", "output": null}, {"id": "publisher", "type": "publisher", "config": {}, "status": "pending", "output": null}], "edges": [{"source_node_id": "research", "target_node_id": "decision"}, {"source_node_id": "decision", "target_node_id": "writing"}, {"source_node_id": "writing", "target_node_id": "fact_check"}, {"source_node_id": "fact_check", "target_node_id": "image"}, {"source_node_id": "image", "target_node_id": "review"}, {"source_node_id": "review", "target_node_id": "publisher"}], "is_active": true}
(4 rows)
`

Presets: Simple | Default Full | Research Only | Legacy

---

## 14. API Endpoints
### Channels
- GET /api/v1/channels
- POST /api/v1/channels
- GET/PATCH/DELETE /api/v1/channels/{id}
- POST /api/v1/channels/{id}/connect-telegram
- POST /api/v1/channels/{id}/connect-vk
- PUT /api/v1/channels/{id}/schedule
### Content
- GET /api/v1/content?channel_id=&status=
- PATCH /api/v1/content/{id}
### Workflows
- GET /api/v1/workflows
- POST /api/v1/workflows/{id}/run
### Other
- GET /health
- GET /assets/... (StaticFiles)
- GET /api/v1/logs

---

## 15. Configuration
### docker-compose.yml
`yaml
services:

  # ==========================
  # PostgreSQL Database
  # ==========================
  postgres:
    image: postgres:16-alpine
    container_name: amf_postgres

    environment:
      POSTGRES_DB: ai_media_factory
      POSTGRES_USER: amf_user
      POSTGRES_PASSWORD: amf_password_2026

    ports:
      - "5432:5432"

    volumes:
      - postgres_data:/var/lib/postgresql/data

    healthcheck:
      test:
        [
          "CMD-SHELL",
          "pg_isready -U amf_user -d ai_media_factory"
        ]
      interval: 10s
      timeout: 5s
      retries: 5

    networks:
      - amf_network

    restart: unless-stopped



  # ==========================
  # Redis
  # ==========================
  redis:
    image: redis:7-alpine
    container_name: amf_redis

    ports:
      - "6379:6379"

    volumes:
      - redis_data:/data

    healthcheck:
      test:
        [
          "CMD",
          "redis-cli",
          "ping"
        ]
      interval: 10s
      timeout: 5s
      retries: 5

    networks:
      - amf_network

    restart: unless-stopped



  # ==========================
  # Backend API
  # ==========================
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend

    container_name: amf_backend

    ports:
      - "8000:8000"


    environment:

      DATABASE_URL:
        postgresql://amf_user:amf_password_2026@postgres:5432/ai_media_factory

      REDIS_URL:
        redis://redis:6379/0

      SECRET_KEY:
        change-this-secret-in-production

      OLLAMA_URL:
        http://host.docker.internal:11434

      USE_AUTOMATION_V2: "true"


      ENVIRONMENT:
        development


    extra_hosts:
      - "host.docker.internal:host-gateway"



    depends_on:

      postgres:
        condition: service_healthy

      redis:
        condition: service_healthy



    volumes:

      # Project root

      - ./:/app

      # API

      - ./backend:/app/backend

      # Core architecture
      - ./core:/app/core

      # AI Engines
      - ./engines:/app/engines

      # Prompt library
      - ./prompts:/app/prompts

      # Connectors
      - ./connectors:/app/connectors

      # Tests
      - ./tests:/app/tests

      # Scripts
      - ./scripts:/app/scripts

      # Documentation
      - ./docs:/app/docs


    networks:
      - amf_network


    restart:
      unless-stopped



  # ==========================
  # Frontend
  # ==========================
  frontend:

    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend


    container_name:
      amf_frontend


    ports:
      - "3001:80"


    depends_on:
      - backend


    networks:
      - amf_network


    restart:
      unless-stopped



  # ==========================
  # Nginx
  # ==========================
  nginx:

    image:
      nginx:alpine


    container_name:
      amf_nginx


    ports:
      - "80:80"


    volumes:

      - ./nginx.conf:/etc/nginx/nginx.conf:ro


    depends_on:

      - backend
      - frontend


    networks:

      - amf_network


    restart:
      unless-stopped



# ==========================
# Persistent volumes
# ==========================

volumes:

  postgres_data:

  redis_data:



# ==========================
# Network
# ==========================

networks:

  amf_network:

    driver:
      bridge
`

### Environment
- DATABASE_URL: postgresql://amf_user:amf_password@postgres:5432/ai_media_factory
- REDIS_URL: redis://redis:6379
- OLLAMA_BASE_URL: http://host.docker.internal:11434
- VK_API_VERSION: 5.199

### LLM Models (Ollama)
- mistral-nemo:12b (main writing + prompts)
- llama3.1:8b, gemma2:9b (alternatives)
- qwen2.5-coder:7b (tech)
- nomic-embed-text (embeddings)

---

## 16. Main Application

### FastAPI app (backend/main.py)

`python
﻿import sys
import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.api.v1.router import api_v1_router
from backend.app.api.v1.health import router as health_router
from backend.automation.scheduler import automation_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 AI Media Factory Dashboard starting...", flush=True)
    
    # Безопасный асинхронный запуск планировщика в фоне
    asyncio.create_task(automation_scheduler.start())
    print("🚀 Automation scheduler task created in background", flush=True)

    yield
    print("👋 Shutting down...", flush=True)

app = FastAPI(
    title="AI Media Factory Dashboard API",
    description="API и интерфейс для управления AI Media Factory",
    version="1.0.0 Beta",
    lifespan=lifespan
)


# Sprint 11: Serving generated assets
import os
os.makedirs("/app/assets", exist_ok=True)
app.mount("/assets", StaticFiles(directory="/app/assets"), name="assets")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Безопасное монтирование статики (с проверкой существования папок)
static_dir = "backend/static"
templates_dir = "backend/templates"

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=templates_dir)
app.include_router(api_v1_router)
app.include_router(health_router, prefix="/api/v1")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health")
def health():
    return {"status": "ok", "service": "backend"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
`

**ВАЖНО:** app.mount("/assets", StaticFiles(directory="/app/assets")) для доступа к картинкам.

---

## 17. Known Issues & Solutions

| # | Problem | Solution |
|---|---------|----------|
| 1 | Pollinations 0 bytes at URL>200 | Короткие EN промпты <100 chars через Ollama |
| 2 | Telegram sendPhoto 400 | data=payload вместо json=payload |
| 3 | SQLAlchemy metadata reserved | extra_data = Column("metadata", JSON) |
| 4 | Ollama недоступен из контейнера | host.docker.internal:11434 |
| 5 | ContentORM ломается патчами | py_compile.validate + show diff |
| 6 | RevisionJob/ReEvaluationJob удалены случайно | импорты в __init__.py и runner.py |
| 7 | Assets не персистентны | TODO: volume ./assets:/app/assets |
| 8 | Нет image validation | TODO Sprint 13: ImageValidator |
| 9 | PowerShell Invoke-WebRequest | -UseBasicParsing |
| 10 | xargs/grep недоступны в PS | Select-String/Select-Object |
| 11 | Telegram caption>1024 | Автообрезка с ... |
| 12 | Пустые файлы Pollinations | file_size>1KB в AssetManager |

### Coding Standards
- Engines: чистая бизнес-логика, без FastAPI
- Jobs: тонкая обёртка над Engines, логирование
- Publishers: credentials validation, retry, fallback
- ORM: nullable=True кроме PK, FK с ondelete
- API: только вызовы repositories/engines
- Патчи: Python-скрипт + py_compile
- PowerShell: single-quoted here-strings, -UseBasicParsing

---

## 18. Roadmap
### Sprint 12: Monitoring & Alerting (NEXT)
- [ ] Telegram bot уведомлений
- [ ] Health checks (Ollama, Pollinations, VK, Telegram)
- [ ] SLA metrics, Grafana
- [ ] Alerting: 5xx, low quality, API failures

### Sprint 13: ComfyUI Integration
- [ ] Local ComfyUI Docker
- [ ] Flux/SDXL модели
- [ ] ImageValidator (LLM score)
- [ ] A/B testing картинок
- [ ] Volume ./assets:/app/assets

### Sprint 14: YouTube Shorts
- [ ] YouTube Data API v3, OAuth2
- [ ] Vertical 9:16, auto-thumbnail

### Sprint 15: Dzen Publishing
### Sprint 16: Experience Engine (engagement, learning loop)
### Sprint 17: Workflow Designer v2 (conditional branching)
### Sprint 18: Marketplace (public templates)
### Sprint 19-25: TikTok/Instagram/X, realtime analytics, SaaS

---

## 19. Appendix

### Production URLs
| Service | URL |
|---------|-----|
| React Dashboard | http://localhost:3000 |
| API docs | http://localhost:8000/docs |
| API v1 | http://localhost:8000/api/v1 |
| Health | http://localhost:8000/health |
| Assets | http://localhost:8000/assets/... |
| PostgreSQL | localhost:5432 (amf_user / ai_media_factory) |
| Redis | localhost:6379 |
| Ollama | http://localhost:11434 |

### Test Channels
- Telegram AI Anime News: chat_id=-1003901198631, wf-simple
- Telegram AI News: inactive
- Telegram AI News RU (Test): chat_id=-1004324099845, inactive
- Test VK Channel: vk_group_id=-240792540

### CHANGELOG
- v0.1-v1.10: internal development
- **v1.11 (Sprint 11)**: VK Publisher + Image Domain + Telegram sendPhoto
- v1.12 (planned): Monitoring & Alerting

---
**End of Document**
Generated: 2026-08-11 | Sprint 11 Complete