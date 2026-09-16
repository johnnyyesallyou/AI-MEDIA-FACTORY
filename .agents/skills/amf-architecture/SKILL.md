---
name: amf-architecture
description: Analyze or evolve AI Media Factory architecture using its pipeline boundaries, source-of-truth rules, and platform-independent publication model.
---

# AMF Architecture

Use this skill for architecture reviews, dependency tracing, design decisions, and refactor proposals in AI Media Factory.

## Architectural anchors

- Resolve documentation conflicts using [STATUS.md](../../../STATUS.md), then [TASK.md](../../../TASK.md), [PROJECT_CONTEXT.md](../../../PROJECT_CONTEXT.md), and [ARCHITECTURE.md](../../../ARCHITECTURE.md).
- Treat the local code as the implementation source of truth; treat the PostgreSQL database as lifecycle data source of truth.
- Trace the production path as Channel Profile → Research/Decision/Writing/Evaluation/Media → PublicationBuilder/Publication → platform renderer → publisher → persisted status and platform ID.
- Keep `Publication` platform-independent: it describes what to publish; renderers describe platform representation; publishers communicate with platform APIs.
- Use `channel.content_profile["sources"]` for production source configuration. Treat `channel.sources` and `engines/research/engine.py` as legacy boundaries unless current code proves otherwise.

## Review and design rules

1. Start from the affected user-visible flow and trace data, ownership, and failure behavior across layers.
2. Identify the canonical owner of each decision before proposing a new abstraction; avoid duplicate policy, formatting, breaker, or persistence logic.
3. Preserve archetype/profile policy resolution and channel isolation. Never let a convenience fallback silently become the production source of truth.
4. For new platform behavior, extend the contract/renderer/publisher boundary rather than embedding platform formatting in editorial engines.
5. Call out stale documentation, legacy paths, sync network calls, route-order hazards, and persistence boundaries explicitly.

Prefer a small flow diagram or dependency table when it clarifies three or more components. Proposals must name affected files, invariants, migration risk, and tests to add or update. Do not reproduce the project documentation; link to it.
