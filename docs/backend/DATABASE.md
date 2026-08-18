# AI Media Factory

# Database Architecture

Version: 1.0

Status: Active Development


---

# 1. Overview


AI Media Factory uses PostgreSQL as the primary database.


Database responsibilities:


- persistent data storage
- entity relationships
- workflow state management
- analytics storage



All database operations must go through the Repository Layer.



Forbidden:


API → Database

AI Engine → Database

Worker → Database



---

# 2. Database Technology


Engine:


PostgreSQL



ORM:


SQLAlchemy



Migration system:


Alembic



Connection:


DATABASE_URL environment variable



---

# 3. Database Design Principles


Rules:



1. Every table must have:


- id
- created_at



2. Mutable entities should have:


- updated_at



3. Status fields must use controlled values.



4. Schema changes require:


- migration
- testing
- documentation update



---

# 4. Core Entities Overview


Main entities:



Channel

↓

SourceArticle

↓

ResearchTopic

↓

DraftPost

↓

MediaAsset

↓

Publication

↓

AnalyticsRecord



---

# 5. Channel Table


Purpose:


Stores Telegram channel configuration.



Example fields:



id

name

telegram_username

category

language

description

style_profile

status

created_at

updated_at



Relations:



Channel

has many

ResearchTopic



Channel

has many

DraftPost



Channel

has many

Publication



---

# 6. SourceArticle Table


Purpose:


Stores original external information.



Fields:



id

url

title

description

content

source_name

published_at

hash

created_at



Purpose of hash:


Duplicate detection.



---

# 7. ResearchTopic Table


Purpose:


Stores processed information before writing.



Fields:



id

channel_id

title

description

content

score

sources

hash

status

created_at

updated_at



Status values:



research

selected

processed

rejected



Relations:



ResearchTopic

belongs to

Channel



---

# 8. DraftPost Table


Purpose:


Stores AI generated Telegram content.



Fields:



id

channel_id

research_topic_id

title

body

image_prompt

tags

status

created_at

updated_at



Status values:



draft

review

approved

rejected

published



Relations:



DraftPost

belongs to

ResearchTopic



---

# 9. MediaAsset Table


Purpose:


Stores generated images and media.



Fields:



id

draft_post_id

file_path

media_type

model

prompt

created_at



Examples:



Stable Diffusion image

Generated illustration

Thumbnail



---

# 10. Publication Table


Purpose:


Stores Telegram publication results.



Fields:



id

channel_id

draft_post_id

telegram_message_id

published_at

views

created_at



Relations:



Publication

belongs to

DraftPost



---

# 11. AnalyticsRecord Table


Purpose:


Stores performance metrics.



Fields:



id

publication_id

views

likes

shares

comments

engagement_rate

score

created_at



---

# 12. Entity Relationships


Logical diagram:



Channel

|

|

ResearchTopic

|

|

DraftPost

|

|

MediaAsset

|

|

Publication

|

|

AnalyticsRecord



---

# 13. Index Rules


Important indexes:



ResearchTopic:


- hash
- score
- status
- channel_id



DraftPost:


- status
- channel_id



Publication:


- published_at
- channel_id



---

# 14. JSON Fields


Some flexible data may use JSON.



Examples:



style_profile

sources

tags



JSON data must have documented structure.



---

# 15. Migration Rules


All database changes require:



Step 1:


Modify SQLAlchemy model.



Step 2:


Create Alembic migration.



Step 3:


Test migration.



Step 4:


Update documentation.



Step 5:


Commit changes.



---

# 16. Backup Rules


Production database requires:



- regular backups
- migration history
- restore testing



---

# 17. Database Security


Rules:



Never store:


- API keys
- passwords
- tokens



Secrets belong in:


.env



---

# 18. Future Database Improvements


Planned:



- vector embeddings storage
- semantic search
- AI memory storage
- analytics warehouse
- PostgreSQL optimization



---

# End of Database Architecture

