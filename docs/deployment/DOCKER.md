# AI Media Factory

# Docker Infrastructure Guide

Version: 1.0

Status: Active Development


---

# 1. Overview


AI Media Factory uses Docker to provide isolated and reproducible environments.


Docker responsibilities:



- run backend application
- run database
- run cache layer
- provide networking
- simplify deployment



---

# 2. Current Container Architecture


Current services:



## Backend


Technology:



FastAPI



Purpose:



- REST API
- business services
- workflow orchestration



Port:



8000



---


## PostgreSQL


Technology:



PostgreSQL



Purpose:



- persistent storage
- application data
- AI workflow states



Port:



5432



---


## Redis


Technology:



Redis



Purpose:



- cache
- temporary storage
- future queues



Port:



6379



---


## Ollama


Technology:



Ollama



Purpose:



- local LLM inference
- AI model execution



Port:



11434



---

# 3. Docker Compose


Main infrastructure file:



docker-compose.yml



Responsibilities:



- create containers
- configure networks
- configure volumes
- define environment variables



---

# 4. Container Communication


Internal Docker network:



backend

↓

postgres



backend

↓

redis



backend

↓

ollama



Containers communicate using service names.



Example:



postgres:5432



Not:



localhost:5432



---

# 5. Volumes


Persistent data must use volumes.



Required volumes:



PostgreSQL data



Redis data



Generated media files



AI model storage



Volumes prevent data loss after container restart.



---

# 6. Development Commands


Start services:



docker compose up -d



Stop services:



docker compose down



Restart:



docker compose restart



View status:



docker compose ps



---

# 7. Logs


All services:



docker compose logs



Backend:



docker compose logs backend



Database:



docker compose logs postgres



Redis:



docker compose logs redis



Follow mode:



docker compose logs -f



---

# 8. Rebuilding Containers


After dependency changes:



docker compose build



Start again:



docker compose up -d



---

# 9. Database Migrations


Before migration:



backup database



Run:



alembic upgrade head



Never modify production database manually.



---

# 10. Docker Rules For AI Agents


AI must NOT:



- remove existing volumes
- delete containers without reason
- change ports without documentation
- modify production settings blindly



Before changing Docker configuration:



1.

Understand current setup



2.

Explain reason



3.

Update documentation



4.

Test startup



---

# 11. Health Checks


Every important container should provide health information.



Required:



Backend:

/health



Database:

connection check



Redis:

ping check



---

# 12. Future Scaling


Possible future architecture:



Load Balancer

↓

Multiple Backend Containers

↓

Shared PostgreSQL

↓

Redis Cluster

↓

Event Bus



---

# 13. Common Problems


Container does not start:



Check logs:



docker compose logs



Database connection error:



Check:



- environment variables
- database status
- network configuration



Port conflict:



Check:



docker ps



---

# 14. Docker Security Rules


Never store:



- passwords
- API keys
- tokens



inside:



Dockerfile

docker-compose.yml



Use:



.env



---

# End of Docker Infrastructure Guide

