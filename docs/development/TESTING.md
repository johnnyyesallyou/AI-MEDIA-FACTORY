# AI Media Factory

# Testing Guide

Version: 1.0

Status: Active Development


---

# 1. Overview


This document defines testing standards for AI Media Factory.


Testing goals:


- prevent regressions
- verify business logic
- ensure architecture stability
- validate AI pipeline components



---

# 2. Testing Stack


Primary framework:



pytest



Additional tools:



pytest-asyncio

httpx

coverage



---

# 3. Test Structure


Tests are located:



tests/



Recommended structure:



tests/

├── api/

├── services/

├── repositories/

├── engines/

├── integration/

└── fixtures/



---

# 4. Testing Principles


Every new feature must include tests.



Priority:



1.

Business logic tests



2.

API tests



3.

Integration tests



4.

AI Engine tests



---

# 5. Unit Tests


Unit tests verify isolated components.



Examples:



Services:



- workflow execution
- validation
- business rules



Repositories:



- database operations
- filtering
- persistence



AI Engines:



- prompt generation
- model response handling



---

# 6. API Testing


Every API endpoint should have tests.



Check:



- successful response
- invalid input
- missing data
- authorization errors
- unexpected failures



Example:



POST:



/api/v1/channels/{id}/run-research



Expected:



200 OK



Response:



{
    "status": "started"
}



---

# 7. Service Testing


Services must be tested independently from API.



Example:



ResearchService



Tests:



- starts research workflow
- saves topics
- handles errors
- validates input



---

# 8. Repository Testing


Repositories must verify:



- create operations
- read operations
- filtering
- updates
- deletion where applicable



Database tests should use isolated test database.



---

# 9. AI Engine Testing


AI engines require special validation.



Test:



- correct input format
- prompt creation
- model communication
- invalid responses
- fallback behavior



AI responses must be validated before usage.



---

# 10. Integration Tests


Integration tests verify complete workflows.



Examples:



Research pipeline:



RSS

↓

Research Engine

↓

Database



Content pipeline:



ResearchTopic

↓

Writing Engine

↓

DraftPost



---

# 11. Workflow Testing


Every pipeline transition must be tested.



Example:



research

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



Forbidden:



research

↓

published



without validation.



---

# 12. Async Testing


Async functions require:



pytest-asyncio



Example:



```python
@pytest.mark.asyncio
async def test_research():
    result = await service.run()
    assert result.success
13. Mocking Rules

External services must be mocked.

Mock:

Telegram API
Ollama
DashScope
RSS sources

Do not call real external services during tests.

14. Test Data

Test data must:

be predictable
not contain secrets
represent real scenarios

Fixtures should be stored separately.

15. Coverage Requirements

Target coverage:

Core business logic:

80%+

Critical workflows:

90%+

API endpoints:

70%+

16. Before Completing a Task

AI must run:

Tests

Check errors

Update documentation

Update STATUS.md

17. Definition Of Successful Test Run

A successful implementation requires:

✓ All tests passed

✓ No critical errors

✓ No architecture violations

✓ Documentation updated

✓ STATUS.md updated

18. Future CI/CD

Planned:

GitHub Actions

Pipeline:

Commit

↓

Install dependencies

↓

Run tests

↓

Check formatting

↓

Build Docker

↓

Deploy

End of Testing Guide

