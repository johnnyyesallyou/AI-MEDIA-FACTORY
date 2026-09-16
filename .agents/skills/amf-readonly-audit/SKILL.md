---
name: amf-readonly-audit
description: Perform a strictly read-only audit of the AI Media Factory repository, reporting evidence, risks, and gaps without changing files, containers, databases, or Git state.
---

# AMF Read-only Audit

Use this skill for repository health checks, security reviews, regression audits, and evidence-based status reports.

## Non-negotiable safety boundary

This skill is strictly read-only. Do not run commands or tools that can:

- create, edit, delete, rename, or format files;
- write to PostgreSQL, SQLite, migrations, volumes, caches, or any other database state;
- start, stop, rebuild, exec into, or reconfigure Docker containers;
- create commits, branches, tags, stashes, merges, resets, checkouts, or other Git state;
- install dependencies, regenerate artifacts, publish, or contact external services with side effects.

Treat tests as potentially mutating: inspect them first and execute none unless their read-only behavior is proven. Prefer static inspection, `rg`, file metadata, `git status`, `git diff --check`, and other commands whose side effects are known to be absent. If a requested check needs a mutating action, report it as not run.

## Audit method

1. Read sources in this priority order when they disagree: [STATUS.md](../../../STATUS.md), [TASK.md](../../../TASK.md), [PROJECT_CONTEXT.md](../../../PROJECT_CONTEXT.md), [ARCHITECTURE.md](../../../ARCHITECTURE.md).
2. Inspect the local code and test layout; distinguish documented claims from directly observed implementation.
3. Check production-path boundaries: channel profile configuration, Universal Pipeline, Publication Layer, renderers/publishers, persistence, scheduler, and discovery/health components.
4. Check isolation and safety boundaries: channel IDs, credentials, legacy source fields, error handling, and external integrations.
5. Report findings with severity, evidence paths/lines, impact, and a minimal recommended next step. Separate confirmed facts, documentation drift, and unverified runtime claims.

Do not copy project documentation into the report or this skill. Link to the relevant source and quote only the minimum needed to identify it.

## Expected output

Return a concise scope statement, inspected evidence, findings ordered by severity, test/runtime checks skipped or performed with reasons, and remaining uncertainty. Never imply a green runtime or database verification when the environment was not actually verified.
