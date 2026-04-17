# 07 — API surface v1

**Status: v1 — MVP.** **Language: English.**

REST + SSE. Backend: FastAPI (see `08-adr-stack.md`). All routes are prefixed `/api/v1`.

---

## 1. Authentication

- Session-cookie based (FastAPI `SessionMiddleware` + itsdangerous).
- `POST /auth/signup`, `POST /auth/login`, `POST /auth/logout`.
- CSRF token for state-changing requests (double-submit cookie pattern).
- MVP: no OAuth, no 2FA. Deferred.

## 2. Routes

### 2.1 Onboarding PME

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/company` | Create a company (called on signup if role=company_admin). |
| `POST` | `/needs` | Submit raw brief. Body: `{ raw_brief, language?, budget_eur?, deadline? }`. Returns `Need` with `status=clarifying` or `ready`. |
| `GET`  | `/needs/{id}` | Fetch need + parsed brief. |
| `POST` | `/needs/{id}/clarify` | Answer follow-up questions from Brief-Parser. Body: `{ answers: {q_id: text} }`. |
| `POST` | `/needs/{id}/match` | Triggers Matching Agent. Returns proposed `Mission` (status=`proposed`). |

### 2.2 Mission

| Method | Path | Purpose |
|--------|------|---------|
| `GET`  | `/missions/{id}` | Fetch mission + plan + activated skills. |
| `POST` | `/missions/{id}/accept` | Talent accepts. Status → `accepted`. |
| `POST` | `/missions/{id}/start` | Freezes skill activations. Status → `running`. |
| `POST` | `/missions/{id}/close` | Close. Triggers feedback collection. |
| `GET`  | `/missions/{id}/stream` | **SSE** stream of Mission Copilot events (see `05-mission-copilot-agent.md` §3). |
| `POST` | `/missions/{id}/message` | Send a message to the Copilot. Body: `{text}`. |

### 2.3 Skills

| Method | Path | Purpose |
|--------|------|---------|
| `GET`  | `/skills` | List skills (query: `?domain&phase&certified&search`). Paginated. |
| `GET`  | `/skills/{id}@{version}` | Full manifest. |
| `GET`  | `/skills/{id}/examples` | Example bundle (for display + matching debugging). |
| `POST` | `/skills/import` | **Internal / staff** — trigger Skill-Importer Agent on a URL. |

### 2.4 Workspace

| Method | Path | Purpose |
|--------|------|---------|
| `GET`  | `/missions/{id}/workspace` | List workspace tree. |
| `GET`  | `/missions/{id}/workspace/{path}` | Read a file. |
| `POST` | `/missions/{id}/workspace/{path}` | Write a file (talent only; Copilot uses server-side bypass). |

### 2.5 Governance / tokens

| Method | Path | Purpose |
|--------|------|---------|
| `GET`  | `/me/tokens` | `{ balance, recent_tx: [...] }`. |
| `POST` | `/feedback` | Submit feedback. |
| `GET`  | `/skills/{id}/governance` | Public stats (usage, rating, certification level). |

## 3. SSE event format (mission stream)

`GET /api/v1/missions/{id}/stream` — `text/event-stream`:

```
event: assistant_message
data: {"text": "Je lance l'audit UX sur la home et le tunnel d'achat."}

event: skill_run_start
data: {"run_id":"sr_01...","skill_id":"audit-ux-express","version":"1.2.0","inputs":{...}}

event: skill_run_result
data: {"run_id":"sr_01...","outputs":{...},"duration_ms":182000,"cost_tokens":50}

event: plan_update
data: {"plan":[...]}
```

Reconnection: `Last-Event-ID` header support; server replays from last ack.

## 4. Error envelope

```jsonc
{ "error": { "code": "MATCHING_NO_SKILLS", "message": "No skill covers the brief", "hint": "..." } }
```

Error codes are stable strings. HTTP status follows convention (400 bad request, 409 conflict on resource state, 422 validation).

## 5. OpenAPI

FastAPI auto-generates OpenAPI 3.1 at `/openapi.json` and Swagger UI at `/docs`. Pydantic models derive directly from `06-data-model.md`.

## 6. Rate limits (MVP)

- `POST /needs`: 20 / user / hour (brief parsing is expensive).
- `POST /missions/*/message`: 60 / min (Copilot streaming).
- Others: default FastAPI (none) + Cloudflare in front.
