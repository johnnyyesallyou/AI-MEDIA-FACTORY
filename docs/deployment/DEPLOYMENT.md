# AI Media Factory

# Deployment Guide

Version: 1.0

Status: Active Development


---

# 1. Overview


This document describes deployment procedures for AI Media Factory.


The project uses containerized infrastructure.



Main components:



- FastAPI Backend
- PostgreSQL Database
- Redis
- Ollama AI Runtime
- Future Frontend Application



---

# 2. Deployment Architecture


Current architecture:



Developer Machine

↓

Docker Compose

↓

Backend Container

↓

PostgreSQL Container

↓

Redis Container



AI Models:



Application

↓

Ollama

↓

Local LLM Models



---

# 3. Current Deployment Type


Current environment:



Development



Purpose:



- feature development
- testing
- local AI experiments



Production deployment is planned.



---

# 4. Requirements


Required software:



Docker Desktop



Docker Compose



Git



Python 3.11+



Ollama



Recommended:



16GB RAM+

NVIDIA GPU

CUDA support



---

# 5. First Installation


Clone repository:



git clone <repository>



Enter project directory:



cd AI-MEDIA-FACTORY



Create environment file:



copy .env.example .env



Start infrastructure:



docker compose up -d



Check containers:



docker compose ps



---

# 6. Backend Startup


Backend runs inside Docker container.



Main service:



FastAPI



Default port:



8000



API documentation:



/docs



Example:



http://localhost:8000/docs



---

# 7. Database Startup


Database:



PostgreSQL



Responsibilities:



- store channels
- store research topics
- store generated content
- store analytics



Database migrations:



alembic upgrade head



---

# 8. Redis


Redis responsibilities:



- caching
- temporary data
- future queues
- background jobs



Current usage:



basic infrastructure



Future:



Celery

Event Bus

Workers



---

# 9. AI Runtime


Local AI runtime:



Ollama



Connection:



http://localhost:11434



Required models are configured separately.



See:



docs/ai/MODELS.md



---

# 10. Deployment Workflow


Standard workflow:



Pull changes

↓

Update dependencies

↓

Run migrations

↓

Restart containers

↓

Check logs

↓

Run tests



---

# 11. Logs


View all logs:



docker compose logs



Backend logs:



docker compose logs backend



Follow logs:



docker compose logs -f backend



---

# 12. Restart Procedure


Restart all services:



docker compose restart



Full restart:



docker compose down

docker compose up -d



---

# 13. Backup Strategy


Future production requirement:



Database backup:

daily



Media files backup:

daily



Configuration backup:

version controlled



---

# 14. Production Roadmap


Future production deployment:



Reverse Proxy

↓

HTTPS

↓

Load Balancer

↓

Multiple Backend Workers

↓

External Database

↓

Monitoring



---

# 15. Deployment Rules


Before deployment:



✓ Tests passed


✓ STATUS.md updated


✓ Documentation updated


✓ Database migrations checked



---

# End of Deployment Guide

