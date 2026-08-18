# AI Media Factory

# Components Documentation

Version: 1.0

Status: Active Development


---

# 1. Component Overview


AI Media Factory consists of independent functional components.


Each component has:

- clear responsibility
- defined input
- defined output
- isolated implementation


Main components:


1. API Layer

2. Core System

3. Research Engine

4. Writing Engine

5. Image Engine

6. Publishing Engine

7. Analytics Engine

8. Recommendation Engine

9. Database Layer

10. Worker System



---

# 2. API Layer


Location:

backend/app/api/


Purpose:


Provides external communication interface.


Responsibilities:


- receive HTTP requests
- validate input
- return responses
- expose system functions


Uses:


FastAPI


Must not:


- contain business logic
- access database directly
- call AI models directly



---

# 3. Core System


Location:

backend/app/core/


Purpose:


Application foundation.


Contains:


- configuration
- dependency injection
- logging
- middleware
- security settings



Responsibilities:


- application startup
- global configuration
- service registration



---

# 4. Database Layer


Location:

backend/app/db/

backend/app/models/


Technology:


PostgreSQL

SQLAlchemy


Responsibilities:


Store:


- channels
- research topics
- drafts
- publications
- analytics


Rules:


Database access only through repositories.



---

# 5. Research Engine


Location:


backend/app/engines/research/


Status:


Implemented


Purpose:


Discover and analyze external information.



Input:


RSS sources



Process:


1. Fetch articles

2. Normalize content

3. Remove duplicates

4. Analyze topics

5. Calculate score

6. Save results



Output:


ResearchTopic



Current metrics:


RSS sources:

7


Stored topics:

76+



---

# 6. Writing Engine


Location:


backend/app/engines/writing/


Status:


Planned



Purpose:


Convert research information into Telegram content.



Input:


ResearchTopic



Process:


- create brief
- generate title
- write post
- create hashtags
- create image prompt



Output:


DraftPost



AI models:


Ollama

Cloud LLM APIs



---

# 7. Image Engine


Location:


backend/app/engines/image/


Status:


Planned



Purpose:


Generate visual content.



Input:


DraftPost



Process:


- create image prompt
- call image generation model
- save media



Output:


MediaAsset



Technology:


Stable Diffusion



---

# 8. Publishing Engine


Location:


backend/app/engines/publishing/


Status:


Planned



Purpose:


Publish content to Telegram.



Input:


Approved DraftPost



Process:


- format message
- attach image
- send through Telegram Bot API
- save publication data



Output:


Publication



---

# 9. Analytics Engine


Location:


backend/app/engines/analytics/


Status:


Planned



Purpose:


Measure content performance.



Collect:


- views
- reactions
- shares
- comments


Generate:


- engagement metrics
- reports
- recommendations



---

# 10. Recommendation Engine


Location:


backend/app/engines/recommendation/


Status:


Future



Purpose:


Improve autonomous operation.



Responsibilities:


- analyze successful posts
- optimize prompts
- optimize schedules
- improve topic selection



---

# 11. Worker System


Location:


backend/app/workers/


Purpose:


Execute background tasks.



Examples:


- scheduled research
- content generation
- image creation
- publishing
- analytics collection



Future technology:


Celery

Redis Queue



---

# 12. Telegram Integration


Purpose:


Connect AI Media Factory with Telegram ecosystem.



Responsibilities:


- bot communication
- channel publishing
- statistics collection



Status:


Planned



---

# 13. Frontend Dashboard


Location:


frontend/


Status:


Planned



Purpose:


Provide human control interface.



Future functions:


- manage channels
- approve posts
- view analytics
- configure AI agents
- monitor pipelines



---

# 14. Component Communication Rules


Allowed:


API

↓

Services

↓

Repositories


Services

↓

AI Engines


Workers

↓

Services



Forbidden:


API

↓

Database


AI Engine

↓

Database


Repository

↓

AI Engine



---

# 15. Adding New Components


Before creating a new component:


1. Define responsibility

2. Define input/output

3. Add documentation

4. Update PROJECT_CONTEXT.md

5. Update STATUS.md



---

# End of Components Documentation

