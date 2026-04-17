# 04 — Brief-Parser Agent (spec)

**Status: v1 — MVP spec.** **Language: English.**

The **Brief-Parser Agent** is the entry-point of Symbiose's mission funnel. It converts an unstructured client description (raw text, voice transcript, or short-form inputs) into a **structured Mission Brief** consumed by the Matching Agent.

---

## 1. Purpose

Turn this:

> "On a une boutique Shopify qui convertit mal, surtout sur mobile. Budget 5k, il nous faut un regard extérieur UX sous 10 jours, livrable un plan d'action actionnable. On parle français."

Into this:

```jsonc
{
  "title": "Audit UX d'un e-commerce Shopify mobile-first",
  "domains": ["design", "ux", "ecommerce"],
  "sub_domains": ["mobile", "conversion"],
  "deliverables": ["rapport d'audit", "plan d'action priorisé"],
  "constraints": { "budget_eur": 5000, "deadline_days": 10, "language": "fr" },
  "phase_hints": ["audit", "handover"],
  "persona_hints": ["dirigeant e-commerce", "non-technique"],
  "red_flags": [],
  "confidence": 0.88,
  "raw_brief": "..."
}
```

## 2. Inputs

Three entry formats (normalized to a single text payload):
- Free-text form on the PME onboarding flow.
- Structured form (title + domain picker + budget + deadline fields) — still run through the agent for enrichment.
- (Phase 2) Voice transcript from a 2-minute call-in.

## 3. Output contract (strict JSON)

Required fields: `title`, `domains`, `deliverables`, `constraints.language`, `raw_brief`, `confidence`.

Optional but strongly recommended: `sub_domains`, `phase_hints`, `persona_hints`, `red_flags`.

- `confidence` ∈ [0, 1]: the agent's own assessment of how well it understood the brief. < 0.5 triggers a clarification step (chat loop with the client).
- `red_flags`: non-empty when the brief signals trouble (unrealistic budget, unclear scope, ethical concerns). Passed to the Safety-Review Agent.

## 4. Tools

Zero MCP tools in v1. The agent is a pure LLM transformation with a structured-output schema (JSON mode). Adds one helper:

| Tool | Purpose |
|------|---------|
| `taxonomy.list_domains()` | Surfaces the registry's domain vocabulary so the agent stays in-vocab. |

## 5. System prompt (sketch)

> You are Symbiose's Brief-Parser Agent. You turn messy client descriptions into structured mission briefs.
>
> Rules:
> 1. Extract only what is **explicitly** stated or strongly implied — never fabricate constraints.
> 2. If a required field is missing (budget, deadline), leave it `null` and add an entry to `missing_info` so the client is asked back.
> 3. Map domains to the registry's vocabulary (use `taxonomy.list_domains`). Propose new vocab only if nothing matches.
> 4. Language of the `title` follows `constraints.language`. Keep the original `raw_brief` untouched.
> 5. Flag anything suspicious in `red_flags`: unrealistic ratios (budget/scope), sensitive domains (legal, medical), potential abuse.
> 6. Output **only** the JSON schema above.

## 6. Clarification loop

If `confidence < 0.5` OR `missing_info` non-empty, the Brief-Parser returns a follow-up question set (≤ 3 questions) served back to the client as a chat turn. The answers are fed into a re-run. Max 2 clarification rounds before escalation to a human.

## 7. Eval

Fixtures: 30 briefs (10 clean, 10 ambiguous, 10 edge-cases with red flags).
Metrics:
- **Domain accuracy** (exact match on primary domain): ≥ 0.90.
- **Missing-info recall** (detects when budget / deadline is absent): ≥ 0.95.
- **Red-flag precision**: ≥ 0.80 (don't over-flag benign briefs).

## 8. Interactions

- **Upstream**: PME onboarding form (`docs/flows/onboarding-pme.md`).
- **Downstream**: `MissionBrief` → Matching Agent (`03-matching-agent.md`), `red_flags` → Safety-Review Agent.
