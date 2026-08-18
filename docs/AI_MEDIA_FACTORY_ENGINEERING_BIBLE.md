# AI Media Factory

# Engineering Bible

Version: 1.0

Status: Active


---

# 1. Purpose


This document defines the engineering standards of AI Media Factory.


It is the highest level technical guideline for:

- developers
- AI coding agents
- automation systems


All development decisions must follow this document.


---

# 2. Project Philosophy


AI Media Factory is built as a long-term autonomous media platform.


The main principles:


## Stability over speed

Existing working functionality must not be broken.


## Documentation first

Architecture and decisions must be documented.


## Modular design

Every component must have a clear responsibility.


## Automation

Manual repetitive work should become automated processes.


## Observability

Important system operations must be measurable.


---

# 3. AI Developer Role


The AI coding agent acts as:


Senior Python Engineer

+

System Architect

+

Documentation Maintainer


The AI must:

- understand existing architecture
- implement requested features
- preserve compatibility
- update documentation


The AI must not:

- rewrite the project without reason
- introduce unnecessary technologies
- ignore existing decisions


---

# 4. Mandatory Reading Order


Before any coding task:


1. AI_CONTEXT.md

2. STATUS.md

3. TASK.md

4. PROJECT_CONTEXT.md

5. Relevant docs/


Coding without reading these files is prohibited.


---

# 5. Architecture Rules


The project follows layered architecture.


Allowed dependency flow:


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


AI Engines:

- process information
- generate results
- return structured data


AI Engines must not:

- access database
- modify persistence
- control workflows


---

# 6. Code Standards


Python code must:


Use:

- type hints
- clear naming
- docstrings
- small functions
- explicit dependencies


Avoid:

- duplicated logic
- unnecessary abstractions
- hidden global state


---

# 7. Documentation Rules


Documentation is part of the product.


After every significant change update:


STATUS.md


If architecture changes:


PROJECT_CONTEXT.md


If engineering rules change:


Engineering Bible


---

# 8. STATUS.md Protocol


STATUS.md is the source of truth for current progress.


AI must update STATUS.md after:


- new feature
- bug fix
- database migration
- configuration change
- architectural change


Update format:


Date

Changes

Files modified

Current state

Next step


---

# 9. Testing Rules


New functionality requires:


- validation
- tests
- error handling


Priority:


1. Unit tests

2. Service tests

3. API tests

4. Integration tests


---

# 10. Security Rules


Never store inside code:


- passwords
- API keys
- tokens
- private credentials


Use:

.env


External input must always be validated.


---

# 11. Git Rules


Before committing:


Check:

- changed files
- tests
- documentation


Commit messages must describe the change.


Example:


GOOD:

Implement Writing Engine service


BAD:

Update files


---

# 12. Development Decision Rules


When choosing between solutions:


Prefer:


1. Existing architecture

2. Simplicity

3. Maintainability

4. Testability

5. Scalability


---

# 13. Completion Criteria


A feature is complete only when:


Code:

✓ implemented


Tests:

✓ passed


Documentation:

✓ updated


Status:

✓ STATUS.md updated


Task:

✓ TASK.md updated


---

# End of Engineering Bible

