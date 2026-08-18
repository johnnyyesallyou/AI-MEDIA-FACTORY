# AI Media Factory

# Pipeline Documentation

Version: 1.0

Status: Active Development


---

# 1. Pipeline Overview


AI Media Factory works as an automated content production pipeline.


Main lifecycle:


Research

↓

Analysis

↓

Selection

↓

Brief Generation

↓

Content Generation

↓

Image Generation

↓

Review

↓

Publishing

↓

Analytics

↓

Optimization



Each stage has:

- input
- processing logic
- output
- status transition



---

# 2. Content State Machine


Every content item moves through predefined states.
research

↓

selected

↓

brief

↓

draft

↓

review

↓

approved

↓

published

↓

analytics

↓

learning



State transition rules must be validated.


A stage cannot be skipped without explicit permission.



---

# 3. Research Pipeline


Status:


Implemented



Purpose:


Collect relevant information from external sources.



Flow:


RSS Sources

↓

RSS Collector

↓

Article Parser

↓

Content Normalization

↓

Duplicate Detection

↓

Topic Analysis

↓

Topic Scoring

↓

Database Persistence



---

# 4. Research Engine


Input:


RSS feeds



Processing:


1. Download articles

2. Extract metadata

3. Normalize text

4. Generate content hash

5. Detect duplicates

6. Calculate relevance score



Output:


ResearchTopic



Stored status:


research



---

# 5. Topic Scoring System


Every discovered topic receives a score.


Range:


0-10



Rules:


High priority:

score > 7.0


Medium priority:

5.0 - 7.0


Rejected:

< 5.0



High priority topics are candidates for generation.



---

# 6. Writing Pipeline


Status:


Planned



Purpose:


Convert research data into Telegram posts.



Flow:


ResearchTopic

↓

Content Brief

↓

LLM Generation

↓

Quality Check

↓

DraftPost



---

# 7. Writing Engine Processing


Input:


ResearchTopic



Steps:


1. Analyze topic

2. Generate brief

3. Select writing style

4. Generate title

5. Generate body

6. Generate hashtags

7. Generate image prompt



Output:


DraftPost



---

# 8. Image Pipeline


Status:


Planned



Purpose:


Create visual assets.



Flow:


DraftPost

↓

Image Prompt

↓

Stable Diffusion

↓

Image Processing

↓

Media Storage

↓

MediaAsset



---

# 9. Publishing Pipeline


Status:


Planned



Purpose:


Publish approved content.



Flow:


Approved DraftPost

↓

Telegram Formatter

↓

Telegram Bot API

↓

Channel Publication

↓

Publication Record



---

# 10. Telegram Publishing Rules


Every post must follow:


Maximum length:


1024 characters



Media:


1 image



Links:


1-2 links



Content requirements:


- readable
- relevant
- fact checked
- adapted to channel style



---

# 11. Analytics Pipeline


Status:


Planned



Purpose:


Understand content performance.



Flow:


Published Post

↓

Statistics Collector

↓

Metrics Processing

↓

Performance Report



Collected data:


- views
- reactions
- shares
- comments
- engagement rate



---

# 12. Optimization Pipeline


Future component.


Purpose:


Improve future content generation.



Input:


Analytics data



Processing:


- identify successful patterns
- optimize prompts
- improve schedules
- improve topic selection



Output:


Recommendations



---

# 13. Background Execution


Current:


Research pipeline runs synchronously.



Future:


Workers:


- scheduled research
- generation queue
- image queue
- publishing queue
- analytics queue



Technology:


Redis

Celery

Future message broker



---

# 14. Error Handling


Every pipeline stage must:


- validate input
- handle failures
- log errors
- provide recovery possibility



Failed tasks should not corrupt system state.



---

# 15. Pipeline Extension Rules


Adding a new stage requires:


1. Define purpose

2. Define input

3. Define output

4. Define state transition

5. Add documentation

6. Update STATUS.md



---

# End of Pipeline Documentation

