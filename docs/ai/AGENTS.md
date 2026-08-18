# AI Media Factory

# AI Agents Architecture

Version: 1.0

Status: Active Development


---

# 1. Overview


AI Media Factory is built around specialized AI agents.


Each agent has:


- specific responsibility
- defined input
- defined output
- independent configuration
- isolated prompts



Agents must cooperate through Services and future Event Bus.



---

# 2. Agent Design Rules


Every AI agent must:


- have one primary responsibility
- receive structured input
- produce structured output
- be replaceable
- be testable
- store prompts separately
- use configured AI models



Agents must NOT:


- access database directly
- modify system state directly
- call other agents directly
- contain business rules



---

# 3. Agent Communication


Current architecture:



Service

↓

AI Engine



Future architecture:



Agent

↓

Event Bus

↓

Agent



Direct communication between agents is forbidden.



---

# 4. Current Agents


## Research Agent


Status:


Implemented



Purpose:


Discover and analyze external information.



Responsibilities:


- collect RSS sources
- parse articles
- normalize content
- detect duplicates
- score topics



Input:


RSS feeds



Output:


ResearchTopic



Model:


qwen2.5-coder:3b



Execution:


Local Ollama



---

# 5. Writing Agent


Status:


Planned



Purpose:


Create Telegram content.



Responsibilities:


- analyze research topics
- generate briefs
- write posts
- create titles
- create hashtags
- create image prompts



Input:


ResearchTopic



Output:


DraftPost



Models:


Local Ollama


Cloud LLM fallback



---

# 6. Image Agent


Status:


Planned



Purpose:


Generate visual content.



Responsibilities:


- create image prompts
- call image generation model
- store generated assets



Input:


DraftPost



Output:


MediaAsset



Model:


Stable Diffusion



---

# 7. Publishing Agent


Status:


Planned



Purpose:


Publish content to Telegram.



Responsibilities:


- prepare Telegram message
- attach media
- call Telegram Bot API
- store publication result



Input:


Approved DraftPost



Output:


Publication



---

# 8. Analytics Agent


Status:


Planned



Purpose:


Analyze content performance.



Responsibilities:


- collect statistics
- evaluate engagement
- detect successful patterns
- generate reports



Input:


Publication metrics



Output:


PerformanceReport



---

# 9. Manager Agent


Status:


Future



Purpose:


Coordinate the complete autonomous system.



Responsibilities:


- assign tasks
- monitor agents
- detect failures
- optimize workflow
- manage priorities



The Manager Agent does not perform specialized work.



It coordinates other agents.



---

# 10. Quality Control Agent


Status:


Future



Purpose:


Improve generated content quality.



Responsibilities:


- fact checking
- style validation
- content evaluation
- safety checks



---

# 11. Agent Lifecycle


Every agent follows lifecycle:



Created

↓

Configured

↓

Tested

↓

Active

↓

Monitored

↓

Optimized



---

# 12. Agent Development Rules


When adding a new agent:


Required:


1. Define responsibility

2. Define input schema

3. Define output schema

4. Select model

5. Create prompts

6. Add tests

7. Update documentation

8. Update STATUS.md



---

# 13. AI Autonomy Rules


AI agents may:


- analyze information
- generate content
- suggest actions



AI agents may not:


- change architecture without approval
- delete data
- modify security settings
- bypass validation



---

# End of AI Agents Architecture

