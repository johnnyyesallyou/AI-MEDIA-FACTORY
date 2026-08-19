# AI Media Factory

## Overview

AI Media Factory is a modular AI-powered platform for fully autonomous management of Telegram media channels.

The system automatically:

- Collects news from multiple sources
- Deduplicates information
- Scores topics
- Generates content using LLMs
- Creates images
- Publishes posts to Telegram
- Collects analytics
- Continuously improves future content

The project is designed as a scalable multi-agent platform.

---

# Current Status

See:

- STATUS.md

---

# Current Task

See:

- TASK.md

---

# Project Context

See:

- PROJECT_CONTEXT.md

---

# Documentation

docs/

Architecture

- architecture/ARCHITECTURE.md
- architecture/EVENT_BUS.md
- architecture/PIPELINES.md
- architecture/COMPONENTS.md

Backend

- backend/API_CONTRACT.md
- backend/DATABASE.md
- backend/SERVICES.md
- backend/REPOSITORIES.md

AI

- ai/AGENTS.md
- ai/MODELS.md
- ai/PROMPTS.md
- ai/MEMORY.md

Business

- business/BUSINESS_RULES.md
- business/WORKFLOWS.md

Development

- development/DEVELOPMENT_RULES.md
- development/CODING_STYLE.md
- development/TESTING.md

Deployment

- deployment/DEPLOYMENT.md
- deployment/ENVIRONMENT.md
- deployment/DOCKER.md

History

- history/CHANGELOG.md
- history/DECISIONS.md

Engineering

- AI_MEDIA_FACTORY_ENGINEERING_BIBLE.md

---

# AI Engineering Kit

The project includes an AI Engineering Kit that allows Large Language Models to continue development with minimal human guidance.

The AI must always read the following files in order:

1. AI_CONTEXT.md
2. STATUS.md
3. TASK.md
4. PROJECT_CONTEXT.md
5. Documentation inside docs/

---

# License

Private project.

