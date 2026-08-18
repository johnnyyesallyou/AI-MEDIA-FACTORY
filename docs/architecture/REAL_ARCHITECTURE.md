# AI Media Factory

# Real Architecture

Version: 1.0

Status:
Verified


---

# 1. Overview

Current system is a modular monolith.

The project contains:

- FastAPI backend
- AI engines
- Core layer
- Repository layer
- Workflow system
- Prompt system
- Local AI inference


---

# 2. Current Architecture


API Layer

↓

Services / Workflows

↓

Core Layer

↓

Repositories

↓

Database



AI Engines operate independently:

Research Engine

Writing Engine

Fact Checker

Evaluator


---

# 3. Current Components


## Research Engine

Location:

engines/research/


Responsibilities:

- RSS collection
- Article parsing
- Deduplication
- Topic clustering
- Topic scoring


Status:

Implemented


---


## Writing Engine

Location:

engines/writing/


Responsibilities:

- Content generation
- Prompt construction
- Style adaptation
- Ollama communication


Status:

Implemented


---


## Telegram Engine

Location:

engines/telegram/


Responsibilities:

- Telegram publishing


Status:

Partially implemented


---


## Fact Checker

Location:

engines/fact_checker/


Status:

Prototype


---


## Evaluator

Location:

engines/evaluator/


Status:

Prototype


---


# 4. Core Layer


Location:

core/


Contains:


Models

Repositories

Workflow system

Prompt management

Policies



Responsibility:

Application infrastructure and shared logic.


---

# 5. Database


Current:

SQLite


Future:

PostgreSQL


Database access:

Only through repositories.


---

# 6. AI Infrastructure


Current model provider:

Ollama


Current generation models:

qwen2.5


Future:

Multiple providers.


---

# 7. Current Data Flow


RSS

↓

Research Engine

↓

Topics

↓

Writing Engine

↓

Draft Post

↓

Telegram Publisher

↓

Analytics


---

# 8. Current Development Priority


1.

Stabilize existing engines.


2.

Add tests.


3.

Connect full pipeline.


4.

Add background workers.


5.

Move to PostgreSQL.


---

# End

