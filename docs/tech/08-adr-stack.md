# 08 — ADR: MVP stack decisions

**Status: v1 — decisions taken autonomously by Claude during the MVP delivery sprint (2026-04-17).** **Language: English.**

Context: the user asked for an MVP delivered end-to-end in autonomy. The decisions below were taken without back-and-forth validation; all are reversible, and none are load-bearing beyond MVP.

---

## ADR-01 — Backend language & framework: Python 3.11 + FastAPI

**Decision:** Python 3.11 with FastAPI as the web framework.

**Why:**
- Claude Agent SDK (and the wider Anthropic ecosystem) is best-supported in Python.
- FastAPI gives OpenAPI, async SSE, Pydantic v2 validation out of the box.
- Single language across backend + agents + CLI + scripts.

**Alternatives considered:** Node.js / Hono (rejected: agent ecosystem weaker); Go (rejected: Claude SDK only via HTTP, loses ergonomics).

## ADR-02 — Agent orchestration: thin in-house harness over Anthropic Python SDK

**Decision:** A thin in-house orchestrator calling `anthropic.Anthropic.messages.create()` with tool-use loops. No heavy framework.

**Why:**
- Claude Agent SDK is the long-term target but ecosystem maturity is uneven at MVP; building on primitives is safer.
- LangGraph / CrewAI add abstraction that the MVP doesn't need (3 agents, clear flow).
- Keeps testability high: each agent is a pure-ish function.

**Revisit:** when we hit multi-agent concurrency or long-lived missions with checkpoint / resume needs → evaluate LangGraph + Temporal.

## ADR-03 — Frontend: FastAPI + Jinja2 + HTMX + Tailwind

**Decision:** Server-rendered templates with HTMX for interactivity. Tailwind for styling via CDN at MVP.

**Why:**
- One codebase, one deployment, zero Node.js build step.
- HTMX covers all onboarding screens with minimal JS.
- Streaming Copilot events via SSE integrates cleanly with HTMX `hx-sse`.

**Alternatives considered:** Next.js (rejected for MVP velocity; keep for Phase 2 when DX becomes a competitive axis).

## ADR-04 — Database: SQLite at MVP → PostgreSQL in production

**Decision:** SQLite single file (`symbiose.db`), migrate to PostgreSQL once >1 concurrent writer user or >100 missions.

**Why:** zero setup, fits single-process FastAPI deploy, supports JSON columns.

**Constraint:** no SQLite-specific SQL outside `backend/symbiose/db/`; all queries go through Pydantic models + SQLAlchemy 2.0 (async) so the PG migration is mechanical.

## ADR-05 — Auth: session cookies, argon2id

**Decision:** server-side sessions (SQLite-backed) + argon2id for password hashing + CSRF double-submit for state changes.

**Why:** simplest secure default. OAuth / SSO deferred to Phase 2.

## ADR-06 — Skill bundles layout: filesystem source of truth

**Decision:** `skills/native/<id>/skill.yaml` is the source of truth. `skill_registry` table is a **derived index** rebuilt on app start from the filesystem + imported skills.

**Why:** skills are versioned in git alongside the code; rebuilds are deterministic; community / external skills live in a separate namespace on disk (`skills/community/...`, `skills/external/...`) populated by the Skill-Importer Agent.

## ADR-07 — LLM call isolation for tests

**Decision:** every LLM call goes through `backend/symbiose/llm/client.py`. Tests substitute a `RecordedLLMClient` that returns canned responses from `backend/tests/fixtures/llm/`.

**Why:** tests don't consume API credits and remain deterministic.

## ADR-08 — i18n scope at MVP

**Decision:**
- Skill manifests: i18n-structured (fr + en) as per `02-skill-format.md`.
- Frontend + agent messages: **fr only** at MVP.
- EN support added in Phase 2 once the FR UX is validated with real PMEs.

## ADR-09 — Deployment target

**Decision:** single Docker image, runnable anywhere. No cloud-specific primitives at MVP.

**Why:** keeps options open (Fly.io, Render, Scaleway, self-host). Cloud lock-in happens once we have traction.

## ADR-10 — Observability

**Decision:** structured JSON logs to stdout + `ledger_entry` for business events. No external APM at MVP.

**Revisit:** when ops load > 1h/week, add Sentry + a metrics sink.
