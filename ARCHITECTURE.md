# Архитектура AI Media Factory

## Обзор

AI Media Factory — это автономная фабрика управления медиа-каналами в Telegram, VK и (в будущем) Dzen.

**Ключевая идея:**
\\\
Пользователь создаёт канал → указывает тему → подключает платформу → нажимает START
→ система сама исследует, создаёт, публикует, собирает статистику и оптимизирует.
\\\

---

## Текущая архитектура (после Sprint 53)

\\\
┌─────────────────────────────────────────────────────────────────┐
│                        CHANNELS (БД)                             │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  ChannelORM                                                │ │
│  │  ├── id, name, platform                                    │ │
│  │  ├── profile_id (ссылка на шаблон)                         │ │
│  │  ├── content_profile (JSONB - эффективная конфигурация)    │ │
│  │  │    ├── profile_key: "manga_releases"                    │ │
│  │  │    ├── content_type: "manga"                            │ │
│  │  │    ├── topic: "new_chapters"                            │ │
│  │  │    ├── sources: ["remanga", "mangadex"]                 │ │
│  │  │    └── job_type: "manga_pipeline"                       │ │
│  │  ├── bot_token, chat_id (Telegram)                         │ │
│  │  └── vk_access_token, vk_group_id (VK)                     │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ resolve_channel_profile()
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    CHANNEL PROFILES (code)                       │
│  engines/channel_profiles.py                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  PROFILES = {                                              │ │
│  │      "manga_releases": {                                   │ │
│  │          "content_type": "chapter_release",                │ │
│  │          "sources": ["remanga", "mangadex"],               │ │
│  │          "image_policy": {...},                            │ │
│  │          "publishing_policy": {...},                       │ │
│  │          "formatting_profile": {...},                      │ │
│  │      },                                                    │ │
│  │      "anime_news": {...},                                  │ │
│  │      "ai_news": {...},                                     │ │
│  │  }                                                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│  + _deep_merge(profile, overrides) для эффективной конфигурации│
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ job_type dispatch
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE JOBS (orchestration)                 │
│  backend/automation/jobs/                                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │ MangaPipeline│ │ AnimePipeline│ │ NewsPipeline │           │
│  │ Job          │ │ Job          │ │ Job          │           │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘           │
│         │                │                │                     │
│         ↓                ↓                ↓                     │
│  Research→Enrich   Research→Publish   Research→Publish          │
│  →Image→Publish                                                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    RESEARCH + KNOWLEDGE                          │
│  engines/                                                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  MangaResearchJob → MangaKnowledgeEngine → MangaTitle     │ │
│  │  AnimeResearchJob → AnimeKnowledgeEngine → AnimeEpisode   │ │
│  │  NewsResearchJob  → NewsKnowledgeEngine  → NewsArticle    │ │
│  └───────────────────────────────────────────────────────────┘ │
│  + CrossSourceEnricher (manga: remanga+mangadex+readmanga)     │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCE REGISTRY (Sprint 53) ⭐                │
│  engines/source_registry.py                                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  @dataclass SourceDefinition:                              │ │
│  │      id, name, content_types, topics, languages,           │ │
│  │      adapter, capabilities                                 │ │
│  │                                                            │ │
│  │  SourceRegistry.get_sources_for(content_type, topic, lang)│ │
│  │  → возвращает список подходящих источников                 │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PUBLISHING LAYER                              │
│  engines/publishing/                                             │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  get_publisher_for_channel(channel) → BasePublisher        │ │
│  │                                                            │ │
│  │  TelegramPlatformPublisher    VKPlatformPublisher           │ │
│  │       ↓                            ↓                        │ │
│  │  TelegramPublisher (API)      VK API                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│  + TelegraphPublisher для Telegraph страниц                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PLATFORMS                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ Telegram │  │    VK    │  │  Dzen    │ (planned)             │
│  └──────────┘  └──────────┘  └──────────┘                      │
└─────────────────────────────────────────────────────────────────┘
\\\

---

## Принципы архитектуры

### 1. Profile ≠ источник истины

\\\python
# НЕПРАВИЛЬНО:
channel → profile → всё определяется профилем

# ПРАВИЛЬНО:
channel → profile (template) + overrides (content_profile JSONB)
            ↓
      effective config (merged)
\\\

**Реализация:** \esolve_channel_profile()\ делает \_deep_merge(profile, overrides)\

### 2. SourceDefinition = dataclass (не ORM)

Источники — это **capabilities системы**, не пользовательские данные.

\\\python
@dataclass(frozen=True)
class SourceDefinition:
    id: str
    content_types: tuple
    topics: tuple
    languages: tuple
    adapter: str
    capabilities: tuple
\\\

**Почему не ORM?** Потому что \emanga\, \nilist\, \habr\ — это не редактируемые пользователем объекты. Позже, если понадобится UI для custom RSS, можно добавить DB-модель.

### 3. AI отвечает за интеллектуальные операции, не за инфраструктуру

\\\
┌─────────────────────────────────────┐
│  RULES / CONFIG (детерминировано)  │
│  • Что искать → Source Registry    │
│  • Где искать → content_type       │
│  • Формат     → channel_profile    │
│  • Расписание → schedule           │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│  AI (интеллектуальные операции)    │
│  • Translation (EN→RU)             │
│  • Summarization (RSS→summary)     │
│  • Hallucination filtering         │
│  • Channel suggestion (wizard)     │
│  • Learning Loop (паттерны)        │
└─────────────────────────────────────┘
\\\

### 4. Content Formatter Layer (планируется в Sprint 54) ⭐

\\\
СЕЙЧАС (архитектурный долг):
MangaPublishJob._build_publication() → сам решает формат
NewsPublishJob._build_publication()  → сам решает формат

БУДЕТ:
Knowledge Object → Formatter → Publication → Publisher
\\\

---

## Data Flow: создание и публикация поста

### Manga channel

\\\
1. Scheduler (каждые 30 мин)
   ↓
2. MangaPipelineJob.run()
   ↓
3. MangaResearchJob
   - SourceRegistry.get_sources_for("manga", "new_chapters")
   - → ["remanga", "mangadex", "readmanga"]
   - Fetch chapters from each source
   ↓
4. MangaKnowledgeEngine
   - Dedup by canonical_url
   - Create MangaTitle + MangaChapter
   ↓
5. CrossSourceEnricher
   - Merge descriptions, genres, covers
   ↓
6. MangaImageJob
   - Download covers from ReManga/MangaDex
   ↓
7. MangaPublishJob
   - resolve_channel_profile(channel) → manga_releases config
   - TelegraphPublisher.upload_images_to_telegraph(preview_pages)
   - TelegramPlatformPublisher.publish(publication)
   ↓
8. Telegram: @manga_new_chapters
   - Обложка + RU/EN названия
   - Описание + жанры
   - Telegraph страница с 5 preview pages
   - Кнопки: "Читать на Telegraph" + "Читать на сайте"
\\\

### News channel

\\\
1. Scheduler (каждые 30 мин)
   ↓
2. NewsPipelineJob.run()
   ↓
3. NewsResearchJob
   - Fetch RSS: habr, vc, techcrunch, theverge
   - Dedup by canonical_url
   - Create NewsArticle
   ↓
4. NewsPublishJob
   - _translate_to_russian() через gemma2:9b
   - resolve_channel_profile() → ai_news config
   - PublicationImageResolver (og:image)
   ↓
5. Telegram: @news_bot_ag
   - Заголовок на русском (переведён)
   - Описание на русском (переведено)
   - Картинка с источника
   - Telegraph страница
   - Кнопки
\\\

### Anime channel

\\\
1. Scheduler (каждые 30 мин)
   ↓
2. AnimePipelineJob.run()
   ↓
3. AnimeResearchJob
   - AniList API + MyAnimeList
   - Create AnimeEpisode
   ↓
4. AnimePublishJob
   - _translate_to_russian() через gemma2:9b
   - Real key visual (не AI-generated)
   ↓
5. Telegram: @Anime_news_ai
   - Key visual
   - RU описание + теги
   - Ссылка на AniList
\\\

---

## Технологии

### Backend
- **FastAPI** — REST API
- **SQLAlchemy** — ORM
- **PostgreSQL** — БД (JSONB для content_profile)
- **APScheduler** — cron jobs
- **httpx/requests** — HTTP клиенты

### AI/ML
- **Ollama + gemma2:9b** — перевод, evaluation
- **Ollama + qwen2.5:0.5b** — fast model для простых задач

### Publishing
- **Telegram Bot API** — публикация в Telegram
- **VK API** — публикация в VK
- **Telegraph API** — Telegraph страницы

### Источники
- **ReManga API** — манга (RU)
- **MangaDex API** — манга (EN)
- **ReadManga** — манга (RU)
- **AniList GraphQL API** — аниме
- **MyAnimeList API** — аниме
- **RSS feeds** — новости (habr, vc, techcrunch, theverge)

---

## Структура проекта

\\\
AI-MEDIA-FACTORY/
├── backend/
│   ├── app/
│   │   ├── api/v1/              # REST endpoints
│   │   │   ├── channels.py
│   │   │   ├── sources.py       # Sprint 53 ⭐
│   │   │   ├── templates.py
│   │   │   └── router.py
│   │   └── services/
│   ├── automation/
│   │   ├── jobs/                # Pipeline jobs
│   │   │   ├── manga_pipeline_job.py
│   │   │   ├── manga_publish_job.py
│   │   │   ├── anime_pipeline_job.py
│   │   │   ├── anime_publish_job.py
│   │   │   ├── news_pipeline_job.py
│   │   │   └── news_publish_job.py
│   │   └── scheduler.py         # Cron jobs
│   └── core/
│       ├── models/
│       │   ├── channel_orm.py
│       │   ├── content_orm.py
│       │   ├── channel_profile_orm.py
│       │   └── __init__.py
│       └── database.py
├── engines/
│   ├── source_registry.py       # Sprint 53 ⭐
│   ├── channel_profiles.py      # PROFILES dict + resolve_channel_profile()
│   ├── publishing/
│   │   ├── factory.py           # get_publisher_for_channel()
│   │   ├── telegram_publisher_adapter.py
│   │   └── vk_publisher.py
│   ├── telegraph/
│   │   └── publisher.py         # upload_images_to_telegraph()
│   ├── source_adapters/
│   │   ├── manga_registry.py
│   │   ├── anime_registry.py
│   │   ├── remanga_adapter.py
│   │   ├── mangadex_adapter.py
│   │   └── anilist_adapter.py
│   └── evaluator/
│       └── engine.py            # LLM evaluation
├── scripts/                     # Utility scripts
└── status.md                    # Project status
\\\

---

## Следующие архитектурные шаги

### Sprint 54: Formatter Layer (самый важный)

**Проблема:** формат поста захардкожен в publish_job-ах.

**Решение:**
\\\python
# engines/formatters/base.py
class BaseFormatter(ABC):
    @abstractmethod
    def format(self, knowledge_object, channel_config) -> Publication:
        pass

# engines/formatters/manga_formatter.py
class MangaFormatter(BaseFormatter):
    def format(self, manga_title: MangaTitle, channel_config) -> Publication:
        # Формат: обложка + RU/EN название + описание + Telegraph + кнопки
        ...

# engines/formatters/formatter_registry.py
def get_formatter(content_type: str, topic: str) -> BaseFormatter:
    # manga/new_chapters → MangaFormatter
    # anime/news → AnimeFormatter
    # news/technology → NewsFormatter
    ...
\\\

**Результат:**
- Формат определяется \channel_profile\, а не job-ом
- Новые типы контента = новые formatter-ы (не jobs)
- Основа для Sprint 55 (Wizard)

### Sprint 55+: Wizard, One-Click START, Learning Loop

(см. status.md для деталей)
