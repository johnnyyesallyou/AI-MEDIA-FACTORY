---
name: amf-reliability
description: Review and design reliability behavior for AI Media Factory pipelines, publishers, source health, retries, pauses, circuit breakers, DLQ, and recovery.
---

# AMF Reliability

Use this skill for reliability audits, incident analysis, resilience changes, and verification of failure handling.

## Canonical reliability model

- Use [STATUS.md](../../../STATUS.md) as the current state, followed by [TASK.md](../../../TASK.md), [PROJECT_CONTEXT.md](../../../PROJECT_CONTEXT.md), and [ARCHITECTURE.md](../../../ARCHITECTURE.md) for context.
- Treat `backend/core/reliability.py` and its `get_breaker(platform)` registry as the single circuit-breaker decision source. `rate_limiter.py` compatibility behavior must not become a second breaker.
- Keep error taxonomy meaningful: retry transient/network failures; fail fast on permanent/configuration failures; honor Retry-After for 429 responses.
- A 429 pause is channel-wide and must prevent expensive pipeline work, not merely one outbound request. Channel keys must preserve Telegram/VK isolation.
- Exhausted delivery failures go to the dead-letter queue; self-healing retries the stored payload, respects due time, channel pause, and breaker state, and has bounded attempts.
- Health checks, alerts, metrics, and dashboard data are observability aids; they do not replace persisted lifecycle state.

## Analysis workflow

1. Trace the failure from source/API call through classification, retry, breaker/pause, DLQ, recovery, and persisted result.
2. Check state-machine transitions, consecutive-failure semantics, recovery timeout, idempotency, bounded retries, and per-channel/platform isolation.
3. Check fail-fast behavior for credentials/configuration errors and ensure secrets are not exposed in logs or reports.
4. Prefer injected clocks/sleep, mocks, and isolated fixtures for deterministic tests; avoid real API calls and unbounded waits.
5. Report whether evidence is unit-tested, integration-tested, runtime-observed, or merely documented. Include failure mode, blast radius, and recovery path.

Do not add a new retry, breaker, pause, or DLQ mechanism without first locating the existing canonical owner. Keep recommendations focused and link to project sources instead of copying them.
