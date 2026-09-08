# AI Media Factory — System Architecture

**Last Updated:** __2026-09-08__
**Version:** 2.0 (Post Sprint 72)

---

## Architecture Overview

### High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                     Channel Profile                         │
│  (archetype, sources, publishing policies, media policies) │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Universal Pipeline                        │
│  Research → Decision → Writing → Evaluation → Media        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  PublicationBuilder                         │
│         (applies archetype policies, builds Publication)    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Publication Contract                       │
│   (text, media, source, article_url, formatting, metadata) │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
┌──────────────────────┐    ┌──────────────────────┐
│  TelegramRenderer    │    │    VKRenderer        │
│  - HTML source links │    │  - Plain text        │
│  - InlineKeyboard    │    │  - URL attachments   │
│  - parse_mode=HTML   │    │  - Media attachments │
└──────────┬───────────┘    └──────────┬───────────┘
           │                           │
           ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│  Telegram Publisher  │    │    VK Publisher      │
│  (Bot API)           │    │  (wall.post API)     │
└──────────┬───────────┘    └──────────┬───────────┘
           │                           │
           └─────────────┬─────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Database Update                          │
│          (status=published, message_id tracking)            │
└─────────────────────────────────────────────────────────────┘
Component Details
1. Channel Profile

Purpose: Defines channel configuration and editorial policies.

Location: core/models/channel_profile_orm.py

Key Fields:

archetype — content type (news, educational, entertainment, etc.)
content_profile — JSON configuration including sources and content settings
publishing — JSON publishing policies
media — JSON media policies
learning — JSON learning parameters

Production content sources are stored in:

channel.content_profile["sources"]

The legacy channel.sources field is not the production source of truth for the Universal Pipeline.

2. Universal Pipeline

Purpose: Orchestrates the complete content production lifecycle.

Production Path:

automation_manager_v2.run_channel_now(channel_id)
        ↓
ChannelTask
        ↓
UniversalContentPipeline
        ↓
StrategyRegistry
        ↓
Research
        ↓
Decision
        ↓
Writing
        ↓
Evaluation
        ↓
Revision
        ↓
Re-evaluation
        ↓
Media
        ↓
Publication
        ↓
Platform Publishing

Main locations:

backend/automation/automation_manager_v2.py
backend/engines/universal_pipeline.py
backend/engines/generic_strategies.py
backend/engines/news_strategies.py

The Universal Pipeline supports multiple content archetypes through strategy-based processing.

3. Publication Layer — Sprint 72

The Publication Layer separates editorial content from platform-specific rendering.

3.1 Publication Contract

Location:

core/models/publication.py

The contract contains:

@dataclass
class Publication:
    text: str
    media: List[MediaAsset]
    source: Optional[str]
    source_url: Optional[str]
    article_url: Optional[str]
    formatting: FormattingOptions
    platform_metadata: Dict[str, Any]

Supporting models:

MediaAsset
FormattingOptions
Key Principle

Publication describes WHAT should be published, not HOW it is rendered.

This allows the same publication object to be rendered differently for Telegram, VK, and future platforms.

3.2 PublicationBuilder

Location:

core/models/publication_builder.py

Purpose: Converts generated content into the canonical Publication contract.

Responsibilities:

Apply archetype-based defaults
Apply profile-level overrides
Resolve source attribution
Resolve article-link policy
Resolve media policy
Build media assets
Apply formatting constraints
Policy Resolution
Profile settings
       ↓
Archetype defaults
       ↓
Global defaults

The visible publication format is therefore controlled by metadata and policies rather than hard-coded text templates.

Editorial Principle

The platform should standardize the internal publication contract, not force every channel to use identical visible text.

For example, a news channel may use source attribution while an entertainment channel may not. An article link may be rendered as a button on Telegram while being represented as an attachment on VK.

4. Platform Renderers

Location:

core/models/renderers/

Renderers transform a platform-independent Publication into platform-specific output.

4.1 TelegramRenderer

Output includes:

rendered text
parse_mode
reply_markup
media information
web preview configuration

Current features:

HTML source links
HTML escaping
Читать полностью inline button when article_url is available
media support
platform-specific formatting

Example source representation:

<a href="https://example.com">Источник</a>
4.2 VKRenderer

Output includes:

plain text message
media attachments
article URL / attachment information

Current principles:

no Telegram-specific HTML
platform-native text representation
media attachments
article link fallback
5. Publishing Strategies

Publishing strategies connect the editorial pipeline with the Publication Layer and platform publishers.

5.1 NewsPublishingStrategy

Location:

backend/engines/news_strategies.py

Status: Integrated — Sprint 72.4

Current flow:

Generated post
      ↓
ContentORM
      ↓
PublicationBuilder
      ↓
Publication
      ↓
TelegramRenderer / VKRenderer
      ↓
Platform Publisher
      ↓
Database status update
      ↓
success result

The Sprint 72.4 integration has been validated with real Telegram publications.

Verified result:

published = 6
telegram_message_id = 504–509
status = published
5.2 GenericPublishingStrategy

Location:

backend/engines/generic_strategies.py

Status: Next integration step.

Sprint 72.5 will migrate GenericPublishingStrategy to the same Publication Layer:

Generic post
      ↓
PublicationBuilder
      ↓
Publication
      ↓
TelegramRenderer / VKRenderer
      ↓
Publisher
      ↓
Database

The goal is to remove duplicated platform formatting logic from individual publishing strategies.

6. Platform Publishers
6.1 Telegram Publisher

Location:

backend/engines/telegram_publisher.py

API: Telegram Bot API

Current capabilities include:

send_message
send_photo
HTML parsing
reply markup
web preview control
message ID tracking
rate limiting
sanitization
6.2 VK Publisher

Location:

backend/engines/vk_publisher.py

API: VK API / wall.post

Current capabilities include:

text publication
media attachments
VK post ID tracking
platform-specific publication
7. Content Engines
7.1 Research

Primary RSS infrastructure:

backend/engines/rss_fetcher.py

Research receives source configuration from the channel profile and produces topics for downstream processing.

Capabilities include:

RSS parsing
topic extraction
freshness filtering
source handling
error handling
7.2 Decision

Responsible for selecting and prioritizing topics.

Current mechanisms include:

URL-based deduplication
relevance / priority processing
existing-content checks
7.3 Writing

Location:

backend/engines/llm_post_generator.py

Primary local model:

llama3.1:8b

Current goals:

Russian-language generation
natural editorial text
archetype-aware generation
length control
source-aware content generation

Source attribution is increasingly handled by the Publication Layer rather than being hard-coded into LLM prompts.

7.4 Evaluation

Responsible for quality evaluation before publication.

The broader pipeline supports:

quality scoring
fact evaluation
revision
re-evaluation
7.5 Media

Responsible for media selection/generation.

Media requirements are controlled by channel/archetype policy.

The Publication Layer receives normalized media assets before rendering.

8. Database Layer
8.1 ContentORM

Location:

core/models/content_orm.py

Important fields include:

id
channel_id
headline
draft_text
source_url
status
telegram_message_id
published_at
quality/fact fields
media references

The database remains the source of truth for content lifecycle state.

8.2 ChannelORM

Contains channel/platform configuration including:

channel identity
platform
Telegram credentials
VK configuration
profile relationship
active state
8.3 ChannelProfileORM

Location:

core/models/channel_profile_orm.py

Contains:

archetype
theme
niche
audience
language
tone
content configuration
research configuration
media configuration
publishing configuration
learning configuration
9. Data Flow
Successful News Publication
1. automation_manager_v2.run_channel_now(channel_id)
                    ↓
2. Load Channel + Channel Profile
                    ↓
3. Universal Pipeline
                    ↓
4. Research
                    ↓
5. Decision
                    ↓
6. Writing
                    ↓
7. Evaluation / Revision
                    ↓
8. Media
                    ↓
9. NewsPublishingStrategy
                    ↓
10. PublicationBuilder
                    ↓
11. Publication
                    ↓
12. TelegramRenderer / VKRenderer
                    ↓
13. Platform Publisher
                    ↓
14. Database Update
                    ↓
15. status = published
                    ↓
16. platform message/post ID persisted
10. Design Principles
1. Separation of Concerns
Publication
    = WHAT to publish

Renderer
    = HOW to represent it on a platform

Publisher
    = HOW to communicate with the platform API
2. Natural Editorial Style

The system should avoid rigid AI-looking templates.

Preferred approach:

[media]

Natural short text.

Optional source attribution.
Optional full-article link.

The exact visible structure depends on archetype and channel profile.

3. Archetype-Based Configuration

Different archetypes may have different:

source policies
media requirements
article-link policies
formatting rules
length limits
paragraph limits
emoji preferences
4. Platform Independence

The same Publication can be rendered for:

Telegram
VK
Future platforms

without changing the editorial generation layer.

5. Database as Source of Truth

Publication lifecycle is persisted in the database.

Important final state:

status = published
platform message/post ID = persisted
published_at = persisted
11. Current Supported Archetypes

The platform currently defines eight core content archetypes:

News
Releases
Educational
Entertainment
Viral
Reviews
Community
Aggregator

Generic strategies allow the Universal Pipeline to support non-news archetypes without creating an entirely separate pipeline for each one.

12. Current Platform State

As of Sprint 72:

Channels:             14
Telegram channels:    13
VK channels:           1

Universal Pipeline:   operational
Generic LLM:          operational
Deduplication:        operational
Telegram publishing:  operational
VK publishing:        operational
Publication Contract: operational
PublicationBuilder:   operational
TelegramRenderer:     operational
VKRenderer:            operational

Sprint 72.4 validated the complete News publishing path with real Telegram publications.

13. Performance Characteristics

Observed Universal Pipeline duration is approximately:

100–330 seconds

depending on:

number of topics
RSS response time
LLM generation time
evaluation/revision
publishing workload

LLM generation is currently one of the dominant latency sources.

14. Security Considerations
API Credentials

Platform credentials must not be committed to source control.

They are stored through the application's channel configuration and runtime environment.

Rate Limiting

Telegram publication is rate-limited.

VK rate limiting requires further hardening.

Input Validation

The system validates:

source URLs
RSS input
generated content
platform publication data
15. Technical Debt / Known Follow-Up Work

The following areas should not be confused with the production Universal Pipeline:

Legacy Research Path
engines/research/engine.py

This is an older research path and should not become the production source architecture.

Legacy Channel Sources
channel.sources

Production source configuration uses:

channel.content_profile["sources"]
Scheduler

The scheduler contains legacy job-ID assumptions that should be reviewed during reliability/observability work.

VK Async Publishing

VK publishing paths should be reviewed to ensure all network operations are fully asynchronous.

16. Roadmap
Sprint 72.5 — Generic Publishing Integration
Migrate GenericPublishingStrategy to PublicationBuilder
Use TelegramRenderer
Use VKRenderer
Remove duplicated formatting logic
Validate non-news archetypes
Sprint 72.6 — 14-Channel Regression
Run all active channels
Verify publication status
Verify platform IDs
Verify source/article-link policies
Verify media policies
Sprint 72.7 — Editorial QA
Validate natural Russian-language output
Remove rigid AI-looking structures
Validate paragraph/length policies
Validate source attribution
Validate article-link behavior
Sprint 73 — Observability
Pipeline duration per stage
Posts/hour per channel
Success/failure rates
LLM latency
Telegram/VK health
Structured metrics
Sprint 74 — Reliability
Retry policies
Exponential backoff
Timeouts
Circuit breakers
Dead-letter handling
Automatic recovery
Sprint 75+ — Discovery Engine
Source discovery
RSS validation
Source scoring
Source Registry
Subscribe.ru discovery integration
Later — Learning and Smart Scaling
Analytics-driven optimization
A/B testing
Learning Loop
Multi-platform expansion
Smart channel scaling
Pilot network expansion
References
STATUS.md — current project state
ROADMAP.md — development roadmap
TASK.md — current backlog
PROJECT_CONTEXT.md — project context
AI_CONTEXT.md — AI-assisted development context