# AI Media Factory

Project Context

Version: 1.0

Status: Active Development

---

# 1. Vision

AI Media Factory is a modular AI-driven platform designed for fully autonomous creation, management, publishing, and optimization of multiple Telegram media channels.

The long-term goal is to build a scalable media ecosystem where specialized AI agents cooperate to perform the complete content lifecycle without continuous human involvement.

The platform must support:

- Unlimited Telegram channels
- Independent content styles
- Multiple AI models
- Local and cloud inference
- Modular architecture
- Horizontal scalability
- Human approval workflows
- Continuous learning from analytics

The system is designed around independent components that communicate through well-defined interfaces.

---

# 2. Primary Objectives

The project aims to automate the complete media production pipeline.

Core objectives include:

• Automated news discovery

• Topic clustering

• Duplicate removal

• Topic scoring

• Content planning

• Brief generation

• Draft generation

• Image generation

• Telegram publishing

• Analytics collection

• Performance evaluation

• AI-assisted optimization

No manual work should be required during normal operation except optional approval.

---

# 3. Current Development Phase

Current Version

0.2

Current Phase

Research Engine → Content Persistence

Current State

Implemented

✓ Docker infrastructure

✓ FastAPI backend

✓ PostgreSQL

✓ SQLAlchemy

✓ Alembic

✓ Redis

✓ RSS collection

✓ Topic deduplication

✓ Topic scoring

✓ Topic persistence

✓ REST API

✓ Channel management

✓ Content entities

✓ Metrics foundation

In Progress

• Writing Engine

Planned

• Brief Generator

• Prompt Builder

• Image Engine

• Telegram Publisher

• Analytics Engine

• Recommendation Engine

---

# 4. High-Level Architecture

The platform consists of multiple independent layers.

Presentation Layer

↓

REST API

↓

Application Layer

↓

Business Services

↓

AI Engines

↓

Repository Layer

↓

Database

↓

Infrastructure

Every layer has a single responsibility.

Business logic must never exist inside API routes.

Database logic must never exist inside AI engines.

Repositories provide the only access to persistence.

Services orchestrate business operations.

AI engines generate intelligence but never perform persistence directly.

---

# 5. Design Principles

The architecture follows these principles.

1.

Modularity

Every component can be replaced independently.

2.

Loose Coupling

Components communicate through interfaces.

3.

Single Responsibility

Every module has exactly one responsibility.

4.

Dependency Injection

Dependencies are injected rather than created directly.

5.

Testability

Every business component should be unit-testable.

6.

Scalability

The system must support multiple workers and multiple AI models.

7.

Maintainability

Readable code is preferred over clever code.

8.

Documentation First

Architecture documentation is part of the project itself.

Any architectural change must also update documentation.

---

# 6. Technology Stack

Backend

FastAPI

Python

SQLAlchemy

Alembic

Pydantic

PostgreSQL

Redis

Frontend

Next.js (planned)

React

TypeScript

TailwindCSS

shadcn/ui

AI

Ollama

DashScope

Stable Diffusion

Infrastructure

Docker

Docker Compose

Git

GitHub

Future

NATS

Celery (optional)

Prometheus

Grafana


---

# 7. Project Directory Structure

The project follows a modular architecture.

Each directory has a clearly defined responsibility.
AI-MEDIA-FACTORY/

├── backend/
├── frontend/
├── docker/
├── docs/
├── scripts/
├── tests/
├── .github/
├── README.md
├── PROJECT_CONTEXT.md
├── STATUS.md
├── TASK.md
├── ROADMAP.md
├── AI_CONTEXT.md
└── MEMORY_PROTOCOL.md

---

# 8. Backend Structure
backend/

app/

api/

core/

db/

engines/

models/

repositories/

schemas/

services/

workers/

utils/

tests/


Every directory has a single responsibility.

---

# 9. Directory Responsibilities

## api/

Contains REST API endpoints.

Responsibilities:

- request validation

- response serialization

- authentication

- routing

Must NOT contain:

- business logic

- SQL

- AI prompts

---

## core/

Contains application core.

Includes:

- configuration

- dependency injection

- startup

- middleware

- logging

- settings

---

## db/

Contains persistence layer.

Includes:

- database session

- migrations

- initialization

- connection management

---

## models/

Contains SQLAlchemy ORM models.

Models describe database structure only.

Business logic is prohibited.

---

## schemas/

Contains Pydantic schemas.

Responsibilities:

- request validation

- response models

- serialization

No business logic.

---

## repositories/

Contains all database access.

Repositories are the ONLY layer allowed to communicate with SQLAlchemy sessions.

Responsibilities:

- CRUD

- filtering

- pagination

- persistence

Repositories never call AI.

Repositories never contain business logic.

---

## services/

Contains business logic.

Responsibilities:

- orchestration

- validation

- workflows

- coordination

Services may call repositories.

Services may call AI engines.

Services must never execute raw SQL.

---

## engines/

Contains AI logic.

Responsibilities:

- research

- scoring

- writing

- image generation

- evaluation

AI engines must never directly access the database.

Persistence always goes through Services.

---

## workers/

Background processing.

Examples:

- scheduled research

- image generation

- analytics

- publishing

Workers communicate through Services.

---

## utils/

Shared helper functions.

Must not contain business logic.

Examples:

- hashing

- parsing

- date formatting

- helper functions

---

# 10. Layer Communication Rules

Allowed

API

↓

Services

↓

Repositories

↓

Database

Services

↓

AI Engines

Workers

↓

Services

Forbidden

API

→ Database

API

→ SQLAlchemy

AI Engine

→ Database

Repository

→ AI Engine

Models

→ Services

Schemas

→ Database

Violating these rules is considered an architectural error.

---

# 11. Dependency Rules

Higher layers may depend on lower layers.

Lower layers must never depend on higher layers.

Correct

API

↓

Services

↓

Repositories

↓

Database

Incorrect

Repository

↓

API

Incorrect

Database

↓

AI Engine

---

# 12. Code Organization Principles

Every new module should follow existing architecture.

Never duplicate functionality.

Prefer extension over replacement.

Reuse existing services whenever possible.

Large files should be split into logical modules.

Every public function should include:

- type hints

- docstring

- meaningful naming

Avoid global state whenever possible.


---

# 13. AI System Overview

The AI Media Factory is built around multiple specialized AI engines.

Each engine has a single responsibility.

The platform follows a pipeline architecture.

Every stage receives structured input and produces structured output.

No engine should perform responsibilities belonging to another engine.

---

# 14. AI Engines

Current and planned AI engines.

Research Engine

Status:
Implemented

Responsibilities:

- Collect RSS feeds
- Parse articles
- Normalize content
- Remove duplicates
- Calculate topic score
- Store research topics

Input:

RSS feeds

Output:

ResearchTopic

---

Writing Engine

Status:
Planned

Responsibilities:

- Read approved research topics
- Generate brief
- Generate Telegram draft
- Generate hashtags
- Generate image prompt

Input:

ResearchTopic

Output:

DraftPost

---

Image Engine

Status:
Planned

Responsibilities:

- Build Stable Diffusion prompt
- Generate image
- Store generated image
- Return image path

Input:

DraftPost

Output:

GeneratedImage

---

Publishing Engine

Status:
Planned

Responsibilities:

- Format Telegram message
- Upload image
- Publish post
- Store Telegram message id

Input:

PublishedPost

Output:

TelegramPublication

---

Analytics Engine

Status:
Planned

Responsibilities:

- Collect statistics
- Calculate engagement
- Detect successful posts
- Produce recommendations

Input:

Telegram statistics

Output:

PerformanceReport

---

Recommendation Engine

Status:
Planned

Responsibilities:

- Learn from analytics

- Improve prompts

- Improve posting schedule

- Improve topic selection

Input:

Analytics

Output:

Recommendations

---

# 15. AI Models Configuration

Research Analysis

Model

qwen2.5-coder:3b

Execution

Local Ollama

Status

Primary Local Model

Purpose

Research analysis

Topic processing

Scoring support

Writing

Primary

DashScope

Model

qwen-coder-plus

Fallback

Local Ollama

Purpose

Brief generation

Draft generation

Image Prompt Generation

Image Generation

Stable Diffusion

Execution

Local

Purpose

Telegram illustrations

Future

LLM Evaluator

Fact Checker

Prompt Optimizer

Memory Engine

---

# 16. AI Model Parameters

Default Parameters

temperature

0.7

top_p

0.9

max_tokens

2048

repeat_penalty

1.1

These parameters may be overridden for specific engines.

---

# 17. Content Lifecycle

Every topic moves through predefined states.

research

↓

brief

↓

draft

↓

review

↓

approved

↓

published

↓

analytics

↓

learning

No state may be skipped unless explicitly allowed.

State transitions must be validated.

---

# 18. Research Pipeline

Current implementation.

RSS Sources

↓

Download Articles

↓

Normalize Content

↓

Extract Metadata

↓

Deduplicate

↓

Score Topics

↓

Persist to PostgreSQL

↓

Status = research

Current metrics

RSS Sources

7

Topics Found

76

Duplicates Removed

Implemented

Persistence

Implemented

REST API

Implemented

---

# 19. Planned Writing Pipeline

Research Topics

↓

Score Filter

↓

Generate Brief

↓

Generate Draft

↓

Generate Title

↓

Generate Tags

↓

Generate Image Prompt

↓

Status = draft

Only topics above configured score threshold should continue.

---

# 20. Planned Publishing Pipeline

Draft

↓

Generate Image

↓

Telegram Formatting

↓

Telegram Bot API

↓

Publication

↓

Statistics Collection

↓

Status = published

---

# 21. Workflow Rules

Every stage must receive validated input.

Every stage produces structured output.

Every stage stores its status.

Every stage can be restarted independently.

No engine should directly invoke another engine.

Coordination belongs to Services.

---

# 22. AI Design Principles

Every AI engine must be:

Deterministic where possible.

Replaceable.

Independent.

Observable.

Testable.

Configurable.

Reusable.

Prompts must be stored separately from source code whenever possible.

Business logic must never exist inside prompts.


---

# 23. Data Architecture Overview

AI Media Factory uses PostgreSQL as the primary relational database.

Database responsibility:

- Store persistent application data
- Maintain relationships between entities
- Provide reliable state management
- Support analytics and reporting

All database operations must go through the Repository Layer.

Direct database access from:

- API layer
- AI engines
- Workers

is prohibited.

---

# 24. Core Database Entities

The system is built around several core entities.

---

## Channel

Represents a Telegram media channel managed by the platform.

Purpose:

Stores channel configuration and AI behavior settings.

Example fields:


id
name
telegram_username
description
category
language
style_profile
status
created_at
updated_at


Relations:

Channel

has many

ResearchTopics

has many

DraftPosts

has many

Publications

---

## ResearchTopic

Represents discovered information from external sources.

Purpose:

Temporary intelligence storage before content generation.

Example fields:


id
channel_id
title
description
content
score
sources
hash
status
created_at
updated_at


Status examples:


research
selected
rejected
processed


---

## SourceArticle

Represents original external information.

Purpose:

Stores collected source material.

Example fields:


id
url
title
description
content
source_name
published_at
hash
created_at


---

## DraftPost

Represents generated Telegram content.

Purpose:

Stores AI-generated content before publishing.

Example fields:


id
channel_id
research_topic_id
title
body
image_prompt
tags
status
created_at
updated_at


Status examples:


draft
review
approved
published
rejected


---

## MediaAsset

Stores generated images and media files.

Example fields:


id
draft_post_id
file_path
type
model
prompt
created_at


---

## Publication

Stores Telegram publication results.

Example fields:


id
channel_id
draft_post_id
telegram_message_id
published_at
views
likes
shares


---

## AnalyticsRecord

Stores performance information.

Example fields:


id
publication_id
views
engagement_rate
shares
comments
score
created_at


---

# 25. Database Rules

Database rules:

1.

Every table must have:

- id
- created_at

2.

Mutable entities should have:

- updated_at

3.

Status fields must use controlled values.

4.

Database changes require:

- migration
- documentation update
- testing

5.

Models describe structure only.

Business logic belongs to Services.

---

# 26. API Architecture Overview

The backend exposes REST API using FastAPI.

Base path:


/api/v1/


API responsibilities:

- receive requests
- validate input
- call services
- return responses

API must not contain business logic.

---

# 27. Current API Endpoints

## Health

GET


/health


Purpose:

System health check.

---

## Channels

GET


/api/v1/channels


Returns available channels.

---

GET


/api/v1/channels/{channel_id}


Returns channel details.

---

POST


/api/v1/channels/{channel_id}/run-research


Starts research pipeline.

Example response:

```json
{
  "status": "started",
  "topics_count": 76
}
Content

GET

/api/v1/content/

Query parameters:

channel_id
status
limit
offset

Example:

/api/v1/content/?channel_id=1&status=research

Example response:

[
 {
  "id":42,
  "title":"New AI Model Released",
  "score":8.5,
  "status":"research"
 }
]
28. Writing Engine Contract

Input:

ResearchTopic

Example:

{
"id":42,
"title":"New ChatGPT Feature",
"description":"OpenAI released...",
"score":8.5,
"sources":[
"https://example.com"
]
}

Output:

DraftPost

Example:

{
"title":"New AI breakthrough",
"body":"Telegram formatted text",
"image_prompt":"futuristic AI illustration",
"tags":[
"AI",
"Technology"
]
}
29. Business Rules

Content lifecycle:

Research

↓

Brief

↓

Draft

↓

Review

↓

Approved

↓

Published

↓

Analytics

Topic priority:

High priority:

score > 7.0

Medium priority:

5.0 - 7.0

Rejected:

< 5.0

Telegram rules:

Maximum:

1024 characters

Media:

1 image

Links:

1-2 links

Content must be:

readable
fact checked
relevant
adapted to channel style
30. Current Known Limitations

Current limitations:

Research pipeline is synchronous.

Future:

Background workers.

Writing Engine is not implemented.

Image generation pipeline is not implemented.

Telegram publishing is not implemented.

Advanced analytics is not implemented.

Fact checking engine is not implemented.

Prompt optimization is not implemented.

31. Known Technical Issues

Current known issues:

UTF-8 encoding issues may appear with external RSS sources.

Possible race conditions during parallel processing.

Duplicate content prevention requires improvement.

More database indexes may be required after scaling.

32. Future Development Direction

Short term:

Implement:

Writing Engine
Brief Generator
Prompt System
Telegram Publisher

Medium term:

Implement:

Multi-channel management
Image pipeline
Analytics

Long term:

Implement:

Autonomous AI Manager
Self optimization
Multi-agent collaboration
Revenue optimization


## API Details

Current endpoint:

POST

/api/v1/channels/{channel_id}/run-research


Purpose:

Starts Research Engine execution.

Example response:

status: started

topics_count: 76


---

GET

/api/v1/content/


Query parameters:

channel_id

status

limit

offset


Purpose:

Returns stored content topics.


---

# 28. Writing Engine Contract

Input object:

ResearchTopic


Required fields:

id

title

description

score

sources


Output object:

DraftPost


Required fields:

title

body

image_prompt

tags


The Writing Engine must never access the database directly.

The Writing Engine communicates through Services.

---

# 29. Business Rules

Content lifecycle:

Research

↓

Brief

↓

Draft

↓

Review

↓

Approved

↓

Published

↓

Analytics


---

Topic priority rules:

High priority:

score greater than 7.0


Medium priority:

score from 5.0 to 7.0


Rejected:

score below 5.0


---

Telegram content rules:

Maximum length:

1024 characters


Media:

One image per post


Links:

One or two links


Content requirements:

- readable
- fact checked
- relevant
- adapted to channel style


---

# 30. Current Known Limitations

Current limitations:

1.

Research pipeline works synchronously.

Future improvement:

Background workers.


2.

Writing Engine is not implemented.


3.

Image generation pipeline is not implemented.


4.

Telegram publishing is not implemented.


5.

Advanced analytics is not implemented.


6.

Fact checking engine is not implemented.


7.

Prompt optimization is not implemented.


---

# 31. Known Technical Issues

Current known issues:

UTF-8 encoding problems may appear with some RSS sources.


Possible race conditions during parallel processing.


Duplicate detection requires additional optimization.


Database indexes may require optimization after scaling.


---

# 32. Future Development Direction

Short term:

Implement:

- Writing Engine
- Brief Generator
- Prompt System
- Telegram Publisher


Medium term:

Implement:

- Multi-channel management
- Image generation pipeline
- Analytics system


Long term:

Implement:

- Autonomous AI Manager
- Self optimization
- Multi-agent collaboration
- Revenue optimization


---

# 33. Documentation Update Rules

Any developer or AI agent modifying the project must update documentation.

Required updates:

Code changes:

Update relevant technical documentation.


Architecture changes:

Update architecture documents.


New features:

Update PROJECT_CONTEXT.md.


Completed tasks:

Update STATUS.md.


---

# 34. AI Development Rules

AI agents working on this project must:

- Read AI_CONTEXT.md first
- Read STATUS.md before coding
- Read TASK.md before starting work
- Preserve existing architecture
- Avoid unnecessary refactoring
- Update documentation after changes

---

# End of Project Context


---

# Real Project Architecture (Verified)

The following structure represents the actual implementation.

## Root Architecture


AI-MEDIA-FACTORY

│

├── backend/

│   └── app/

│       └── api/

│           └── v1/

│

├── core/

│

├── engines/

│

├── infrastructure/

│

├── automation/

│

├── connectors/

│

└── docs/


---

# Backend API Layer


Location:


backend/app/api/v1/


Responsibilities:


- REST endpoints
- request validation
- API routing
- response handling


Current modules:


- channels.py
- content.py
- research.py
- workflows.py
- dashboard.py
- analytics.py
- automation.py


API layer must not contain business logic.


---

# Core Application Layer


Location:


core/


Responsibilities:


Database:

- database connection
- ORM models


Repositories:

- database operations


Workflows:

- workflow execution


Policies:

- business rules


Prompt management:

- prompt tracking
- prompt lifecycle


Structure:


core/

├── models/

├── repositories/

├── workflows/

├── policies/

└── prompts/


---

# AI Engines Layer


Location:


engines/


## Research Engine


Status:

Implemented


Location:


engines/research/


Components:


- RSS sources
- extractor
- deduplicator
- scorer
- models


Responsibilities:


- collect information
- normalize content
- remove duplicates
- calculate topic score
- create research topics



---


## Writing Engine


Status:


Implemented Skeleton



Location:


engines/writing/


Components:


- engine.py
- models.py
- prompt_manager.py
- styles/


Responsibilities:


- generate content drafts
- manage writing prompts
- apply channel styles



Next task:

Integrate with Research Pipeline.



---


## Telegram Publisher


Status:


Partial Implementation


Location:


engines/telegram/


Responsibilities:


- Telegram API communication
- publishing messages



---


## Evaluation Engine


Location:


engines/evaluator/


Status:


Foundation


Purpose:


- evaluate generated content
- quality scoring



---


## Fact Checker


Location:


engines/fact_checker/


Status:


Foundation


Purpose:


- verify information
- improve reliability



---

# Architecture Summary


Current system:


API

↓

Core Services

↓

Repositories

↓

Database



AI processing:


Core Workflow

↓

AI Engines

↓

Generated Content



Future:


Event Bus based multi-agent architecture.



---

# End Verified Architecture

