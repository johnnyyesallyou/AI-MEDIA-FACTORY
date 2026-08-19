# AI Media Factory

# System Architecture

Version: 1.0

Status: Active Development


---

# 1. Overview


AI Media Factory is a modular AI-powered platform for autonomous Telegram media channel management.


The system is designed to automate the complete content lifecycle:


Research

↓

Analysis

↓

Content Generation

↓

Image Creation

↓

Publication

↓

Analytics

↓

Optimization



The architecture is designed as a scalable modular monolith with future support for distributed services.


---

# 2. High Level Architecture


The system consists of the following layers:


## Presentation Layer


Responsible for communication with external users and systems.


Components:

- REST API
- Future Web Dashboard
- Telegram integrations


Technology:

FastAPI


---

## Application Layer


Responsible for business workflows.


Components:

- Services
- Workflow managers
- Task orchestration


Responsibilities:

- coordinate operations
- validate processes
- manage state transitions


---

## Repository Layer


Responsible for data access.


Components:

- repositories
- database adapters


Responsibilities:

- CRUD operations
- queries
- persistence


Direct database access outside this layer is prohibited.


---

## Database Layer


Primary database:


PostgreSQL


Stores:


- channels
- research topics
- drafts
- publications
- analytics


---

## AI Layer


Contains specialized AI engines.


Components:


Research Engine

Writing Engine

Image Engine

Publishing Engine

Analytics Engine

Recommendation Engine


Each engine has one responsibility.


---

# 3. Main System Flow


Complete production pipeline:


RSS Sources

↓

Research Engine

↓

Research Topics

↓

Content Selection

↓

Writing Engine

↓

Draft Post

↓

Image Engine

↓

Media Asset

↓

Publishing Engine

↓

Telegram Channel

↓

Analytics Engine

↓

Optimization



---

# 4. Backend Architecture


Backend structure:


backend/


app/


api/

core/

db/

models/

schemas/

repositories/

services/

engines/

workers/

utils/



---

# 5. Component Responsibilities


## API Layer


Responsible for:


- receiving requests
- validation
- authentication
- returning responses


Forbidden:


- business logic
- SQL queries
- AI operations



---

## Services Layer


Responsible for:


- business rules
- workflows
- coordination


Services connect:


API

↓

Repositories

↓

AI Engines



---

## Repository Layer


Responsible for:


- database communication
- persistence
- queries


Repositories never call AI engines.


---

## AI Engines


Responsible for intelligence operations.


Examples:


Research Engine:

Collect and analyze information.


Writing Engine:

Generate content.


Image Engine:

Generate visuals.


Publishing Engine:

Deliver content.


Analytics Engine:

Measure results.



---

# 6. Current Implemented Architecture


Implemented:


✓ FastAPI backend

✓ PostgreSQL database

✓ Redis infrastructure

✓ SQLAlchemy ORM

✓ Repository layer

✓ Research Engine

✓ Topic persistence

✓ REST API



---

# 7. Current Missing Components


Not implemented:


Writing Engine


Responsibilities:

- generate briefs
- generate Telegram posts
- create prompts



Image Engine


Responsibilities:

- generate images
- manage media



Publishing Engine


Responsibilities:

- Telegram Bot API
- scheduling



Analytics Engine


Responsibilities:

- statistics collection
- performance analysis



---

# 8. Architectural Rules


All components must:


- have one responsibility
- communicate through interfaces
- be replaceable
- be testable


Forbidden:


API → Database


AI Engine → Database


Repository → AI Engine


Model → Service


---

# 9. Future Scaling


The architecture supports:


Future:


Message broker:

NATS


Background processing:

Celery


Monitoring:

Prometheus

Grafana


Frontend:

Next.js


Multi-agent AI management.



---

# 10. Architecture Decision


Current decision:


Use modular monolith first.


Reason:


- easier development
- easier debugging
- lower infrastructure complexity


Migration to microservices is possible later without rewriting core logic.


---

# End of Architecture

