# AI Media Factory

# Environment Configuration Guide

Version: 1.0

Status: Active Development


---

# 1. Overview


This document describes environment variables used by AI Media Factory.


Configuration is separated from application code.


Secrets must never be stored inside source code.



---

# 2. Environment File


Main configuration file:



.env



Example template:



.env.example



The .env file must not be committed to Git.



---

# 3. Application Configuration


## Application Mode


Variable:



APP_ENV



Values:



development

production



Example:



APP_ENV=development



---

## Secret Key


Variable:



SECRET_KEY



Purpose:



Application security key.



Example:



SECRET_KEY=change-me-in-production



Production requirement:



Use strong random value.



---

# 4. Database Configuration


## PostgreSQL URL


Variable:



DATABASE_URL



Example:



DATABASE_URL=postgresql://amf_user:password@postgres:5432/ai_media_factory



Used by:



SQLAlchemy



Alembic



---

## Database Host


Variable:



POSTGRES_HOST



Example:



postgres



---

## Database Port


Variable:



POSTGRES_PORT



Default:



5432



---

## Database Name


Variable:



POSTGRES_DB



Example:



ai_media_factory



---

## Database User


Variable:



POSTGRES_USER



Example:



amf_user



---

## Database Password


Variable:



POSTGRES_PASSWORD



Required:



Yes



---

# 5. Redis Configuration


Redis URL:



Variable:



REDIS_URL



Example:



redis://redis:6379/0



Purpose:



- caching
- queues
- future workers



---

# 6. Ollama Configuration


Local AI runtime:



Variable:



OLLAMA_BASE_URL



Default:



http://localhost:11434



Purpose:



Connect backend with local LLM models.



---

# 7. AI Models


Research model:



Variable:



RESEARCH_MODEL



Example:



qwen2.5-coder:3b



---

Writing model:



Variable:



WRITING_MODEL



Example:



qwen-coder-plus



---

Image model:



Variable:



IMAGE_MODEL



Example:



stable-diffusion



---

# 8. AI Generation Parameters


Temperature:



AI_TEMPERATURE



Default:



0.7



---


Top P:



AI_TOP_P



Default:



0.9



---


Maximum tokens:



AI_MAX_TOKENS



Default:



2048



---

# 9. External APIs


## DashScope


Variable:



DASHSCOPE_API_KEY



Purpose:



Cloud LLM access.



Required:



Only when using cloud models.



---

## Telegram Bot


Variable:



TELEGRAM_BOT_TOKEN



Purpose:



Publishing posts to Telegram.



Status:



TODO



---

# 10. Storage Configuration


Media directory:



MEDIA_PATH



Example:



./storage/media



Purpose:



Generated images and files.



---

# 11. Logging Configuration


Log level:



LOG_LEVEL



Values:



DEBUG

INFO

WARNING

ERROR



Example:



LOG_LEVEL=INFO



---

# 12. Development Environment


Recommended:



APP_ENV=development



Features:



- detailed logs
- local Ollama
- debug mode
- test database



---

# 13. Production Environment


Required:



APP_ENV=production



Requirements:



- strong SECRET_KEY
- HTTPS
- external database backup
- restricted access
- monitoring



---

# 14. Security Rules


Never commit:



.env



API keys



tokens



passwords



Allowed:



.env.example



---

# 15. Example .env


```env
APP_ENV=development

SECRET_KEY=change-me

DATABASE_URL=postgresql://amf_user:password@postgres:5432/ai_media_factory

REDIS_URL=redis://redis:6379/0

OLLAMA_BASE_URL=http://localhost:11434

RESEARCH_MODEL=qwen2.5-coder:3b

WRITING_MODEL=qwen-coder-plus

AI_TEMPERATURE=0.7

AI_TOP_P=0.9

AI_MAX_TOKENS=2048

TELEGRAM_BOT_TOKEN=

DASHSCOPE_API_KEY=

LOG_LEVEL=INFO
16. Configuration Rules For AI

Before adding a new environment variable:

Required:

document variable here
add to .env.example
update related documentation
explain purpose

Never create hidden configuration.

End of Environment Configuration Guide

