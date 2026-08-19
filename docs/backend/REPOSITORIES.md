# AI Media Factory

# Repository Architecture

Version: 1.0

Status: Active Development


---

# 1. Overview


Repository Layer provides the only database access interface.


Architecture:



Services

↓

Repositories

↓

SQLAlchemy

↓

PostgreSQL



Repositories hide database implementation details from business logic.



---

# 2. Repository Responsibilities


Repositories are responsible for:



- CRUD operations
- database queries
- filtering
- pagination
- persistence
- entity retrieval



Repositories MUST NOT contain:



- business rules
- AI logic
- workflow logic
- API logic



---

# 3. Repository Rules


Required:



1.

All database operations go through repositories.



2.

Services never execute SQL directly.



3.

API never accesses database.



4.

AI Engines never access database.



---

# 4. Repository Structure


Recommended structure:



backend/

repositories/


channel_repository.py

research_repository.py

content_repository.py

media_repository.py

publication_repository.py

analytics_repository.py



---

# 5. Channel Repository


Purpose:


Manage Telegram channel storage.



Operations:



create()

get_by_id()

get_all()

update()

delete()



Example:



ChannelService

↓

ChannelRepository

↓

Database



---

# 6. Research Repository


Purpose:


Manage research topics.



Operations:



create_topic()

get_topics()

get_by_score()

update_status()

find_duplicate()



Used by:



Research Service



---

# 7. Content Repository


Purpose:


Manage generated content.



Operations:



create_draft()

get_drafts()

update_content_status()

get_pending_review()



Used by:



Content Service

Writing Service



---

# 8. Media Repository


Purpose:


Store generated assets.



Operations:



create_asset()

get_asset()

link_to_post()



---

# 9. Publication Repository


Purpose:


Store Telegram publication history.



Operations:



create_publication()

get_history()

update_statistics()



---

# 10. Analytics Repository


Purpose:


Store performance data.



Operations:



save_metrics()

get_statistics()

calculate_reports()



---

# 11. Query Rules


Queries should be:



- simple
- readable
- optimized
- documented



Avoid:



- complex business decisions inside queries
- hidden calculations
- duplicated SQL



---

# 12. Pagination Rules


Large collections must support pagination.



Required parameters:



limit

offset



Example:



GET /content?limit=50&offset=0



---

# 13. Transaction Rules


Transactions are controlled by Services.



Repository:


executes database operations.



Service:


decides when transaction starts and ends.



---

# 14. SQLAlchemy Rules


Models:


Only describe database structure.



Repositories:


Use SQLAlchemy ORM.



Services:


Use repositories.



---

# 15. Testing Rules


Repositories require tests for:



- CRUD operations
- filtering
- relations
- error cases



---

# 16. Future Improvements


Planned:



- caching layer
- async repositories
- database optimization
- read replicas
- vector database integration



---

# End of Repository Architecture

