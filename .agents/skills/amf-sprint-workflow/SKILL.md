---
name: amf-sprint-workflow
description: Plan, execute, verify, and document AI Media Factory sprint work while preserving project priorities, test evidence, and change boundaries.
---

# AMF Sprint Workflow

Use this skill for sprint planning, implementation handoff, regression verification, and completion reporting.

## Source priority and scope

When project documents disagree, use [STATUS.md](../../../STATUS.md), then [TASK.md](../../../TASK.md), [PROJECT_CONTEXT.md](../../../PROJECT_CONTEXT.md), and [ARCHITECTURE.md](../../../ARCHITECTURE.md). Mention material drift rather than silently merging contradictory claims.

Before work, define the user outcome, affected pipeline path, acceptance criteria, non-goals, and protected surfaces. Preserve channel isolation, profile-over-legacy configuration, platform-independent publication, and database lifecycle invariants.

## Sprint loop

1. Plan from the current status and backlog; identify dependencies, risks, and the smallest coherent change.
2. Inspect the relevant implementation and tests before editing. Follow existing naming, fixtures, error taxonomy, and API conventions.
3. Implement only the approved scope. Keep Docker, database, credentials, and unrelated documentation untouched unless explicitly authorized.
4. Add or update focused tests for success, failure, isolation, and regression behavior. Prefer deterministic mocks/injected timing for external systems.
5. Verify proportionally: targeted tests first, then regression; distinguish skipped environment-dependent checks from passing checks.
6. Update project status/backlog/architecture documents only when the user authorizes documentation changes, and record exact evidence and limitations.
7. Handoff with changed files, tests and commands, known warnings/failures, migration/runtime requirements, and the next smallest follow-up.

Do not claim completion from a green unit suite alone when the acceptance criteria require Docker, live APIs, or database state. Never commit or push unless explicitly requested. Keep skills concise and link to the project sources instead of duplicating them.
