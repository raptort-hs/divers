# 01 — Agent Architecture

**Status: v1 — first draft to iterate on.**
**Language note:** technical documents live in English, per project rules.

This document sketches the agent-native architecture that powers Symbiose. It anchors the product vision described in `docs/08-environnement-prestataire.md` (French).

---

## 1. Philosophy

Symbiose is **AI-native and agent-native**. The platform is not a classic web app that occasionally calls an LLM: it is an **orchestration of specialized agents**, each with a clear role, its own tools, its own memory, and its own evaluation metrics.

Core implications:

1. **Agents are first-class citizens**, like microservices in a traditional architecture.
2. **Every high-value function is an agent**, not a function call or a hand-coded algorithm (matching, brief parsing, planning, copiloting, importing, reviewing).
3. **Skills are tools or sub-agents** that agents can invoke.
4. **Deterministic code handles only plumbing** (auth, payments, data access, transport), never core product reasoning.
5. **Traceability & transparency**: every agent call is logged, explainable, replayable.

## 2. Agent catalog (MVP)

| Agent | Role | Inputs | Outputs | Tools |
|-------|------|--------|---------|-------|
| **Brief-Parser** | Turn a raw PME brief into a structured mission object | free-text brief, PME profile, domain | `Mission{domain, deliverables[], urgency, budget, seniority, tags[]}` | LLM, taxonomy lookup |
| **Matching Agent** | Compose the talent's mission environment | Talent profile + structured mission + Skill registry | Environment: `{skills_activated[], plan_draft, copilot_persona, rationale}` | Registry search, Skill scorer, Profile reader |
| **Plan-Builder** | Generate a first action plan from the mission + skills | Mission + selected skills + talent profile | Ordered steps + checklists + deliverables per step | LLM, skill schema readers |
| **Mission Copilot** | Assist the talent during execution (chat, drafting, reviewing) | Mission context, skill set activated, live workspace state | Chat answers, drafts, reviews, nudges | All activated skills, web search (optional), file ops |
| **Skill-Importer** | Pull skills from external sources (Claude Skills, MCP, GitHub) and adapt them to Symbiose format | External URL / package / repo | Normalized Skill manifest + safety report | HTTP fetch, YAML/JSON parser, static analyzer |
| **Safety-Review** | Review skills (native, community, external) for prompt injection, PII leakage, bias, misuse | Skill manifest + system prompt + sample runs | Safety verdict + mitigations + required tags | Prompt-injection detector, PII scanner |

### Candidates (Phase 2)

- **Skill-Author Agent**: assists a senior talent in creating a new skill (guided authoring).
- **Feedback-Analyzer Agent**: post-mission, extracts learnings to improve the Matching Agent.
- **Gap-Detector Agent**: continuous analysis of a talent's evolving profile vs market demand.
- **Client-Onboarding Agent**: assists the PME during signup + need qualification (consumed by the onboarding flow).

## 3. The Matching Agent (deep dive)

This is the differentiator. Its quality determines the value Symbiose creates.

### 3.1 Inputs

- **Talent profile object**: declared skills, seniority, values, completed-mission history, preferred working style, copilot mode preference (peer/mentor/exec).
- **Structured mission** (from Brief-Parser Agent): domain, deliverables, deadline, budget, seniority required, constraints, values tags.
- **Skill registry**: searchable, vectorized, with metadata (author, domain, level, certification badge, past usage metrics).

### 3.2 Tools exposed to the Matching Agent

- `search_skills(query, filters)` — semantic + structured search over the registry.
- `read_profile(talent_id)` — fetch full profile with narrative history.
- `read_mission(mission_id)` — fetch structured mission.
- `score_skill(skill_id, talent, mission)` — deterministic scoring helper (cosine sim + rule-based heuristics) that the agent can consult but does not blindly follow.
- `ask_gap_detector(talent, mission)` — delegates gap analysis to a sub-agent.
- `propose_copilot_persona(talent)` — suggests tone/role (peer/mentor/exec).

### 3.3 Output contract

```json
{
  "mission_id": "…",
  "talent_id": "…",
  "environment": {
    "skills_activated": [
      { "skill_id": "audit-ux-express", "source": "native", "role": "core", "rationale": "…" },
      { "skill_id": "google-analytics-reader", "source": "external:mcp", "role": "complement-gap", "rationale": "…" }
    ],
    "plan_draft": [
      { "step": "Discovery & audit", "checklist": ["…"], "expected_skills": ["audit-ux-express"] },
      …
    ],
    "copilot_persona": { "tone": "supportive", "role": "peer-mentor" },
    "gaps_identified": [
      { "gap": "Quantitative UX analysis", "compensating_skill": "google-analytics-reader" }
    ]
  },
  "trace_id": "…"
}
```

### 3.4 System prompt (sketch — to refine)

> You are the Symbiose Matching Agent. Your job: compose the ideal AI-augmented work environment for a specific talent taking on a specific mission. You have access to the full skill registry, the talent's profile, and the mission structure.
>
> Your primary optimization targets, in order:
> 1. Set the talent up to succeed on this mission (coverage of required skills).
> 2. Compensate identified gaps with complementary skills — never leave a gap unaddressed.
> 3. Respect the talent's seniority and preferences (don't over-augment a senior; do scaffold a junior).
> 4. Minimize cognitive overhead (activate as few skills as possible while covering needs).
> 5. Always explain each choice.
>
> You must output a structured environment plus a natural-language rationale visible to the talent.

### 3.5 Metrics

- **Coverage**: % of mission-required capabilities addressed by activated skills.
- **Gap closure**: % of detected gaps with a compensating skill activated.
- **Talent override rate**: % of skills the talent disables — too high = bad matching.
- **Mission success correlation**: downstream mission NPS / delivery quality vs matching decisions.
- **Latency**: p50 / p95 end-to-end, target < 15 s.
- **Cost per run**: LLM tokens consumed (target < €0.20 / match at MVP).

## 4. Orchestration layer

Agents need to call each other and share context. Options:

1. **Claude Agent SDK** (Anthropic): native agent primitives, tool use, sub-agents, memory. Best fit given our Claude-first stance.
2. **LangGraph / LangChain**: mature ecosystem, model-agnostic. Heavier, less aligned with our "Claude as reasoning engine" choice.
3. **Custom orchestration** on top of the Anthropic SDK: lean, tailored, but more to maintain.

**Recommendation (to validate)**: start with **Claude Agent SDK** for MVP. It gives us agents, tools, sub-agent spawning, and prompt caching out of the box. If Phase 2 needs multi-LLM orchestration, revisit.

## 5. Shared services (non-agent components)

- **Auth & identity**: classic, OIDC-based.
- **Skill registry storage**: PostgreSQL + pgvector for semantic search.
- **Mission state**: PostgreSQL, event-sourced log of decisions for replay/debug.
- **File storage & versioning**: S3-compatible (MinIO locally, AWS S3 prod).
- **Payments**: Stripe Connect (integration post-MVP, manual invoicing first).
- **Observability**: per-agent trace logs, evals dashboard (agent accuracy, drift), cost tracking.

## 6. Data flow (constitution of a mission environment)

```
PME submits need
     │
     ▼
Brief-Parser Agent ──▶ structured Mission object ──▶ persisted
     │
     ▼
Talent accepts the mission
     │
     ▼
Matching Agent ──▶ composed Environment ──▶ persisted + shown to talent
     │
     ▼
Plan-Builder Agent (invoked by Matching Agent OR standalone) ──▶ detailed plan
     │
     ▼
Mission Copilot Agent spun up, loaded with context + activated skills
     │
     ▼
Talent starts working, Copilot assists step by step
```

## 7. Open questions

1. **SDK choice**: Claude Agent SDK vs LangGraph vs custom — to validate.
2. **Agent memory**: per-mission short-term memory vs cross-mission long-term memory for the talent — where to draw the line (privacy).
3. **Agent evaluation**: how do we measure matching quality in absence of ground truth? (A/B testing on blinded talents, human eval panels, downstream mission success.)
4. **Cost ceiling**: per-mission LLM budget target and what to do when exceeded (degrade, fallback, charge extra).
5. **Determinism**: do we want the Matching Agent to be deterministic (same inputs → same outputs) or allow diversity? Trade-off transparency vs exploration.
6. **Agent-to-agent protocol**: JSON tool-use calls (SDK native) vs a more explicit bus/event model.
7. **Failover**: what happens when the Matching Agent fails (LLM outage, rate limit)? Graceful degradation to a rule-based fallback? Queue + retry?
8. **Self-improvement loop**: how do post-mission feedback signals propagate back into the Matching Agent? Fine-tuning? Prompt evolution? Retrieval augmentation?

## 8. Next steps

1. Validate SDK choice (propose Claude Agent SDK — await confirmation).
2. Define **Skill manifest format v1** in `docs/tech/02-skill-format.md`.
3. Draft **Matching Agent spec v1** (full system prompt + tool contracts + evaluation harness) in `docs/tech/03-matching-agent.md`.
4. Prototype a thin end-to-end slice: 1 hard-coded skill + Brief-Parser + Matching + static Copilot, running on Claude Agent SDK, wired to a minimal UI.
5. Iterate on 3–5 fictional missions to stress-test the matching logic.
