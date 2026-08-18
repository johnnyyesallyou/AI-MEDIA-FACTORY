# AI Media Factory

# Development Rules

Version: 1.0

Status: Active Development


---

# 1. Overview


This document defines development rules for AI agents and human developers working on AI Media Factory.


The goal:

- maintain stable architecture
- avoid unnecessary refactoring
- keep documentation synchronized
- ensure predictable development



---

# 2. AI Developer Role


AI assistant acts as:

Senior Python / FastAPI Developer



Responsibilities:


- understand existing architecture
- write production-quality code
- preserve project structure
- create tests
- update documentation



---

# 3. Mandatory Reading Before Development


Before changing code AI MUST read:



1.

AI_CONTEXT.md



2.

STATUS.md



3.

TASK.md



4.

PROJECT_CONTEXT.md



5.

Relevant documentation from docs/



Only after this analysis development may begin.



---

# 4. Development Workflow


Every task follows:



Analysis

↓

Plan

↓

Implementation

↓

Testing

↓

Documentation Update

↓

STATUS.md Update



---

# 5. Before Writing Code


AI must:



- inspect existing files
- understand dependencies
- check current implementation
- avoid duplicate functionality



AI must NOT:



- create duplicate modules
- replace working systems unnecessarily
- ignore existing architecture



---

# 6. Architecture Rules


Required architecture:



API

↓

Services

↓

Repositories

↓

Database



AI Engines:



Services

↓

AI Engines



Forbidden:



API → Database



API → AI Engine



AI Engine → Database



---

# 7. Code Change Rules


Small changes are preferred.



Avoid:



- massive rewrites
- unrelated improvements
- changing many modules at once



Every change should have a clear purpose.



---

# 8. Documentation Rules


After changes:



New feature:


Update PROJECT_CONTEXT.md



New API:


Update API_CONTRACT.md



New architecture:


Update architecture docs



Completed task:


Update STATUS.md



---

# 9. STATUS.md Mandatory Update


IMPORTANT:



After completing any task AI MUST update STATUS.md.



Update:



Current phase



Completed items



Active tasks



Known problems



Next steps



Example:



Completed:

[+] Writing Engine skeleton



Current:

Phase 3 Intelligence Layer



Next:

Implement prompt builder



---

# 10. Error Handling Rules


Every error must:



- be logged
- have clear message
- not silently fail
- provide recovery path



---

# 11. Security Rules


Never commit:



- passwords
- API keys
- tokens
- secrets



Secrets belong in:



.env



---

# 12. Git Rules


Every logical change should have:



- clear commit message
- tested code
- updated documentation



Example:



feat: add writing engine service



---

# 13. Refactoring Rules


Refactoring allowed only when:



- current architecture blocks progress
- bug cannot be fixed otherwise
- performance requires change



Before refactoring:


Explain reason.



---

# 14. Definition of Done


Task is complete only when:



✓ Code implemented


✓ Tests passed


✓ Documentation updated


✓ STATUS.md updated


✓ No critical errors



---

# End of Development Rules

