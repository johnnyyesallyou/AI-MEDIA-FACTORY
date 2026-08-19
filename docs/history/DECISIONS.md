# AI Media Factory

# Architecture Decision Records

Version: 1.0

Status: Active Development


---

# Overview


This document stores important architectural decisions made during project development.


AI agents MUST read this document before proposing major architectural changes.



---

# Decision 001

## Modular Monolith Architecture


Date:

2026-07-23



Status:

Accepted



## Decision


AI Media Factory starts as a modular monolith.



## Reason


The project is in early development stage.



Advantages:



- faster development
- easier debugging
- simpler deployment
- lower infrastructure complexity



Future migration to distributed architecture remains possible.



## Consequence


Modules must have clear boundaries.



Communication must happen through Services.



---

# Decision 002

## FastAPI Backend


Date:

2026-07-23



Status:

Accepted



## Decision


Backend framework:



FastAPI



## Reason


FastAPI provides:



- high performance
- async support
- modern Python ecosystem
- automatic API documentation
- strong typing support



## Consequence


API layer must remain separated from business logic.



---

# Decision 003

## PostgreSQL as Primary Database


Date:

2026-07-23



Status:

Accepted



## Decision


Use PostgreSQL for persistent storage.



## Reason


Required capabilities:



- relational data model
- transactions
- JSON support
- scalability
- analytics support



## Consequence


All persistence goes through Repository Layer.



---

# Decision 004

## Redis Infrastructure


Date:

2026-07-23



Status:

Accepted



## Decision


Redis is included from the beginning.



## Reason


Future requirements:



- caching
- background jobs
- queues
- temporary state
- event processing



## Consequence


Redis is infrastructure, not business storage.



---

# Decision 005

## Local AI Through Ollama


Date:

2026-07-23



Status:

Accepted



## Decision


Local models are supported through Ollama.



## Reason


Benefits:



- privacy
- lower API costs
- offline operation
- local experimentation



## Consequence


AI engines must work with replaceable model providers.



---

# Decision 006

## Separate AI Engines


Date:

2026-07-23



Status:

Accepted



## Decision


Each AI capability is an independent engine.



Examples:



- Research Engine
- Writing Engine
- Image Engine
- Analytics Engine



## Reason


Allows:



- independent development
- model replacement
- isolated testing



## Consequence


Engines must not contain database logic.



---

# Decision 007

## Repository Pattern


Date:

2026-07-23



Status:

Accepted



## Decision


Database access is isolated through repositories.



## Reason


Benefits:



- easier testing
- database independence
- clean architecture



## Consequence


Direct SQL access outside repositories is forbidden.



---

# Decision 008

## Event Bus Is Future Architecture


Date:

2026-07-23



Status:

Planned



## Decision


Event Bus will be introduced later.



## Reason


Current project size does not require distributed communication.



## Migration Plan


Current:



Services

↓

Direct Calls



Future:



Service

↓

Event Bus

↓

Agents



---

# Decision 009

## Documentation First Approach


Date:

2026-07-23



Status:

Accepted



## Decision


Documentation is part of the development process.



## Reason


AI-assisted development requires clear context.



## Consequence


Any architectural change requires documentation update.



---

# Decision 010

## AI Agents Must Update STATUS.md


Date:

2026-07-23



Status:

Accepted



## Decision


Every completed development task requires STATUS.md update.



## Reason


Local AI models need current project state.



## Consequence


A task is incomplete until STATUS.md is updated.



---

# Rules For New Decisions


Every new architectural decision must include:



- date
- status
- problem
- chosen solution
- reason
- consequences



---

# End Of Architecture Decisions

