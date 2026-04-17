# 03 — Matching Agent v1 (spec)

**Status: v1 — MVP spec.**
**Language: English.**

The **Matching Agent** is the centerpiece of Symbiose. It takes a parsed client brief + a talent profile and returns a **curated, justified set of skills** ready to activate on the mission. It is an autonomous LLM-powered agent (not a deterministic algorithm), outfitted with retrieval tools over the skill registry.

Sibling docs: `01-agent-architecture.md` · `02-skill-format.md`.

---

## 1. Purpose

Given:
- a structured **Mission Brief** (from the Brief-Parser Agent),
- a **Talent Profile** (vectorized + structured),
- the **Skill Registry** (native + community + external skills, with governance metrics),

produce:
- a ranked set of **3–7 skills** to activate on the mission,
- for each, a short **rationale** (why this skill, why now, why this talent),
- a top-level **mission plan outline** grouped by mission phase.

## 2. Inputs (contract)

```jsonc
{
  "mission_brief": {
    "title": "Audit UX d'un parcours e-commerce",
    "domains": ["design", "ux", "ecommerce"],
    "deliverables": ["rapport audit PDF", "priorisation quick-wins"],
    "constraints": { "budget_eur": 4500, "deadline_days": 7, "language": "fr" },
    "phase_hints": ["discovery", "audit"],
    "raw_brief": "…"
  },
  "talent_profile": {
    "talent_id": "t_abc123",
    "seniority": "confirmed",
    "domains": ["design", "ux"],
    "strengths": ["heuristic evaluation", "Figma"],
    "gaps": ["copywriting", "analytics"],
    "languages": ["fr", "en"],
    "preferred_tools": ["claude-opus"],
    "budget_tokens": 500
  },
  "context": {
    "mission_id": "m_xyz789",
    "now": "2026-04-17T10:00:00Z"
  }
}
```

## 3. Output contract (strict JSON)

```jsonc
{
  "selected_skills": [
    {
      "skill_id": "audit-ux-express",
      "version": "1.2.0",
      "rationale_fr": "Couvre directement le livrable d'audit express demandé. Gold-certified, coût token dans le budget, aligné sur un profil UX confirmé.",
      "covers_deliverables": ["rapport audit PDF"],
      "covers_phases": ["audit"],
      "complements_talent_gaps": [],
      "estimated_cost_tokens": 50,
      "confidence": 0.92
    }
  ],
  "mission_plan_outline": [
    { "phase": "discovery",
      "skills": ["heuristic-framework-nielsen"],
      "rationale": "Pose le cadre méthodologique avant l'audit." },
    { "phase": "audit",
      "skills": ["audit-ux-express"],
      "rationale": "Exécute l'audit sur les 3 parcours critiques." },
    { "phase": "handover",
      "skills": ["executive-summary-generator"],
      "rationale": "Synthèse client-ready." }
  ],
  "unmet_needs": [
    { "need": "analyse analytics", "reason": "Aucun skill du registre ne couvre Matomo côté e-commerce FR. Recommandation : importer `@matomo/analytics-reader` via le Skill-Importer Agent." }
  ],
  "total_estimated_cost_tokens": 140,
  "explanation_fr": "La sélection privilégie un parcours discovery → audit → handover avec 3 skills certifiés. Pas de redondance. Complément analytics à importer si le client le demande."
}
```

Every selected skill must have a non-empty `rationale_fr`. The agent refuses to return a skill it cannot justify.

## 4. Tools exposed to the agent

| Tool | Signature | Purpose |
|------|-----------|---------|
| `skill_registry.search` | `(query: str, filters: {domains?, phases?, seniority?, certified_only?, max_cost_tokens?}) -> SkillSummary[]` | Semantic + filtered search. Returns ≤20 candidates. |
| `skill_registry.get` | `(id: str, version?: str) -> SkillManifest` | Full manifest retrieval for a specific skill. |
| `skill_registry.taxonomy` | `() -> TaxonomyTree` | Browse domains/sub-domains/tags to refine queries. |
| `skill.score` | `(skill_id: str, brief, talent) -> ScoreBreakdown` | Internal scoring (see §5) — callable so the agent can reason about trade-offs. |
| `skill.dependencies` | `(skill_id: str) -> SkillSummary[]` | Resolve transitive deps (Symbiose resolver, §9.3 of skill-format). |
| `registry.propose_import` | `(source_url, hint) -> PendingImport` | Hand off to the Skill-Importer Agent when a need is unmet. Only returns a pending handle — does not block. |

The agent runs in a loop: search → inspect → score → compose → justify. Max 12 tool calls per run (hard budget).

## 5. Scoring breakdown

The `skill.score` tool returns:

```jsonc
{
  "skill_id": "...",
  "subscores": {
    "domain_fit":        0.85,  // cosine(brief.domains, skill.taxonomy.domains)
    "phase_fit":         1.00,  // phase_hints ∩ mission_phases / |phase_hints|
    "deliverable_fit":   0.70,  // LLM-judged mapping skill.outputs → brief.deliverables
    "seniority_fit":     1.00,  // talent.seniority ∈ skill.seniority_target
    "language_fit":      1.00,  // brief.language ∈ skill.languages
    "quality_signal":    0.88,  // f(certification_level, avg_rating, disable_rate)
    "budget_fit":        0.95,  // 1 if cost ≤ budget, decays otherwise
    "talent_complement": 0.60   // bonus if skill covers a talent gap
  },
  "weighted_total": 0.86,
  "weights_used": { "domain_fit":0.2, "phase_fit":0.15, "deliverable_fit":0.25, "seniority_fit":0.05, "language_fit":0.05, "quality_signal":0.15, "budget_fit":0.1, "talent_complement":0.05 }
}
```

Weights are static at MVP (see ADR in `08-adr-stack.md`). Calibration per domain deferred to Phase 2.

## 6. System prompt (sketch)

> You are Symbiose's Matching Agent. Given a mission brief, a talent profile, and access to a skill registry, you produce a minimal, justified set of 3–7 skills that together cover the mission.
>
> Rules:
> 1. Every selected skill must have a clear, specific rationale in French.
> 2. Prefer **certified** skills. Use community / uncertified skills only when no certified alternative covers the need — and flag it.
> 3. Never exceed the talent's `budget_tokens` on `total_estimated_cost_tokens`.
> 4. Never select redundant skills (two skills covering the same deliverable without complementarity).
> 5. If a need is clearly unmet by the registry, surface it in `unmet_needs` and optionally call `registry.propose_import`.
> 6. Respect language: if brief is `fr`, prefer skills with `fr` in `taxonomy.languages`.
> 7. Output **only** the JSON defined in the contract. No prose outside it.

## 7. Evaluation harness

MVP eval: 20 handcrafted `(brief, talent)` fixtures with expected skill sets. Metrics:

- **Recall@k**: does the expected skill set appear in top-k? Target ≥ 0.85 at k=7.
- **Rationale quality**: human-rated on 5-point scale, sample ≥ 50. Target avg ≥ 4.0.
- **Budget compliance**: 100 % (hard rule).
- **No-redundancy**: 100 %.
- **Latency p95**: ≤ 15s.

Eval fixtures live in `backend/tests/fixtures/matching/`.

## 8. Failure modes & fallbacks

| Failure | Response |
|---------|----------|
| Empty registry match | Return `selected_skills: []` + populate `unmet_needs` with import suggestions. |
| Budget too tight | Return partial set + `explanation_fr` stating which phase was dropped. |
| Conflict in skill deps | Raise `RESOLUTION_CONFLICT`; Matching Agent arbitrates via second pass or defers to talent. |
| LLM refuses / safety trigger | Abort mission matching; surface incident to Safety-Review Agent. |

## 9. Interactions with other agents

- **Upstream**: consumes `MissionBrief` from Brief-Parser Agent (`04-brief-parser-agent.md`).
- **Sideways**: may call `registry.propose_import` which enqueues work for the Skill-Importer Agent.
- **Downstream**: emits `MissionPlan` consumed by the Mission Copilot Agent (`05-mission-copilot-agent.md`) at mission runtime.

## 10. Open items (post-MVP)

- Per-domain weight calibration from real data.
- Active learning: retrain the LLM-judge for `deliverable_fit` on labelled outcomes.
- "What-if" mode: let the talent ask the agent for alternatives ("cheaper option ?", "no external API ?").
