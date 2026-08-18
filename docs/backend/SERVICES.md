# AI Media Factory

# Services Architecture

Version: 1.0

Status: Active Development


---

# 1. Overview


Services layer contains business logic of AI Media Factory.


The Service Layer is responsible for:


- business workflows
- orchestration
- validation
- coordination between components
- state transitions



Services connect:



API

↓

Services

↓

Repositories

↓

Database



and:



Services

↓

AI Engines



---

# 2. Service Layer Rules


Services:


MUST:


- contain business logic
- validate operations
- coordinate workflows
- manage entity states
- call repositories
- call AI engines



Services MUST NOT:


- contain HTTP logic
- contain SQL queries
- access database sessions directly
- store API keys
- contain prompts



---

# 3. Core Services


Current and planned services:



## Channel Service


Purpose:


Manage Telegram channels.



Responsibilities:


- create channels
- update channels
- configure channel settings
- manage channel status



Input:


Channel data



Output:


Channel entity



---

## Research Service


Purpose:


Coordinate Research Engine.



Responsibilities:


- start research workflow
- collect topics
- validate results
- save research data
- update topic status



Workflow:



Channel Service

↓

Research Service

↓

Research Engine

↓

Repository



---

## Content Service


Purpose:


Manage content lifecycle.



Responsibilities:


- retrieve topics
- select topics
- create drafts
- manage statuses



States:



research

↓

selected

↓

draft

↓

review

↓

approved

↓

published



---

## Writing Service


Purpose:


Coordinate Writing Engine.



Responsibilities:


- send topics to AI
- create briefs
- generate drafts
- validate output



Workflow:



Content Service

↓

Writing Service

↓

Writing Engine



---

## Media Service


Purpose:


Manage generated media.



Responsibilities:


- request image generation
- store assets
- connect images with posts



Workflow:



DraftPost

↓

Media Service

↓

Image Engine



---

## Publishing Service


Purpose:


Publish content to Telegram.



Responsibilities:


- prepare messages
- call Telegram API
- store publication result
- handle failures



Workflow:



Approved Draft

↓

Publishing Service

↓

Telegram Bot API



---

## Analytics Service


Purpose:


Process channel statistics.



Responsibilities:


- collect metrics
- calculate performance
- generate reports



---

# 4. Workflow Orchestration


Complex operations must be controlled by services.



Example:



Run Research:



API Request

↓

Channel Service

↓

Research Service

↓

Research Engine

↓

Repository

↓

Database



API should never execute this chain directly.



---

# 5. Service Dependencies


Allowed:



Channel Service

↓

Repository



Research Service

↓

Research Repository

↓

Research Engine



Writing Service

↓

Content Repository

↓

Writing Engine



Forbidden:



API

↓

Repository



API

↓

AI Engine



AI Engine

↓

Repository



---

# 6. Transaction Management


Services control business transactions.



Example:



Create Draft:



1.

Get ResearchTopic



2.

Generate content



3.

Validate result



4.

Save DraftPost



5.

Update status



---

# 7. Error Handling


Services must:


- catch expected errors
- create meaningful logs
- return controlled exceptions
- support retries



---

# 8. Service Testing


Every service requires tests.



Test types:



Unit tests:


Business rules.



Integration tests:


Database interaction.



Workflow tests:


Complete scenarios.



---

# 9. Future Service Layer


Planned:



Scheduler Service


Responsibilities:


- run automatic jobs
- control timing



Notification Service


Responsibilities:


- alerts
- system messages



AI Manager Service


Responsibilities:


- coordinate AI agents
- monitor performance



---

# 10. Development Rules


Before creating new service:



Check:


- existing functionality
- existing services
- business rules



Avoid:


- duplicate services
- oversized services
- hidden business logic



---

# End of Services Architecture

