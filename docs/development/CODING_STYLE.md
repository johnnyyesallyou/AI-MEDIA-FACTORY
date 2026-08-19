# AI Media Factory

# Coding Style Guide

Version: 1.0

Status: Active Development


---

# 1. Overview


This document defines coding standards for AI Media Factory.


Goals:


- readable code
- maintainable architecture
- predictable structure
- easy testing
- long-term scalability



---

# 2. Programming Language


Primary language:



Python 3.11+



Framework:



FastAPI



Database:



SQLAlchemy



Validation:



Pydantic



---

# 3. General Python Rules


Code must prioritize:



- readability
- simplicity
- explicit behavior



Avoid:



- unnecessary abstractions
- hidden magic
- duplicated code
- excessive inheritance



---

# 4. Type Hints


Type hints are mandatory.



Example:



```python
def get_channel(channel_id: int) -> Channel:
    pass

Functions without type hints are not allowed.

5. Naming Convention

Classes:

PascalCase

Example:

ResearchService

Functions:

snake_case

Example:

get_research_topics()

Variables:

snake_case

Example:

channel_id

Constants:

UPPER_CASE

Example:

MAX_POST_LENGTH

6. File Structure

Each file should have one main responsibility.

Example:

research_service.py

Contains:

ResearchService

Does not contain:

API routes

database models

unrelated helpers

7. Import Rules

Imports order:

Standard library

Third-party packages

Local project imports

Example:

import logging

from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.services.research import ResearchService
8. Classes

Classes should have clear responsibility.

Good:

ResearchEngine

Bad:

UniversalManager

Avoid giant classes.

9. Functions

Functions should:

do one thing
have clear names
have type hints
have documentation when needed

Avoid:

functions longer than necessary
hidden side effects
10. Async Rules

Use async for:

API handlers
external requests
database operations where supported

Example:

async def run_research(channel_id: int) -> Result:
    pass
11. Database Rules

Database access:

ONLY through repositories.

Forbidden:

session.query()

inside:

API
Services
AI Engines
12. Service Rules

Services contain business logic.

Example:

Good:

research_service.start(channel_id)

Bad:

router.run_all_logic()
13. AI Engine Rules

AI engines:

Responsible for:

prompts
model calls
generation

Must not:

save data
modify database
call API routes
14. Error Handling

Never silently ignore errors.

Required:

logging
meaningful exceptions
recovery where possible

Example:

raise ResearchError(
    "Research source unavailable"
)
15. Logging Rules

Use project logger.

Do not use:

print()

Logs should contain:

operation
object id
error reason
16. Documentation

Public classes and functions should have docstrings.

Example:

def generate_post(topic: ResearchTopic) -> DraftPost:
    """
    Generate Telegram draft from research topic.
    """
17. Testing Requirements

New functionality requires tests.

Minimum:

happy path
error case
edge case
18. Code Review Checklist

Before completion check:

✓ Architecture preserved

✓ Type hints added

✓ Tests created

✓ No duplicated code

✓ Documentation updated

✓ STATUS.md updated

19. Forbidden Practices

Do not:

put secrets in code
hardcode configuration
bypass repositories
create circular dependencies
ignore errors
End of Coding Style Guide

