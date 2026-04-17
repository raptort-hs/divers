# 02 — Skill Manifest v1

**Status: v1 — first draft to iterate on.**
**Language: English (project rule for `docs/tech/`).**

This document defines the **Skill Manifest** — the contract every skill must satisfy to live in the Symbiose registry. It is the foundation on top of which the Matching Agent, the Mission Copilot Agent, the Skill-Importer Agent, and the Safety-Review Agent all operate.

Sibling docs: `docs/08-environnement-prestataire.md` (FR, product) · `docs/tech/01-agent-architecture.md` (EN, agent architecture).

---

## 1. Purpose

A Symbiose skill is a **packaged, invokable capability** that augments a talent on a mission. A skill may be:

- **Native**: authored by Symbiose (ex: *audit-ux-express*, *quantitative-analytics-reader*).
- **Community**: authored by a talent and published to the registry (ex: *b2b-cold-email-senior*).
- **External (imported)**: adapted from a third-party source (Anthropic Claude Skill, MCP server, GitHub repo) and normalized to the manifest.

Whatever its origin, a skill is represented **uniformly** by one manifest + assets bundle.

## 2. Design principles

1. **Uniform contract**: native, community, and imported skills share the same manifest.
2. **Machine-matchable**: the manifest is structured enough for the Matching Agent to search, score, and select skills without reading prose.
3. **Self-describing**: a skill declares what it does, to whom, under what conditions, with what side effects.
4. **Safety-first**: every skill carries a safety profile (PII, injection risk, sandbox level, data egress).
5. **Versioned & replaceable**: skills follow semver. Breaking changes ⇒ major bump. A mission pins a version.
6. **Composable**: skills can declare dependencies on other skills or MCP servers — no hidden coupling.
7. **Economically tagged**: each skill declares its creator and token split (author share %, Symbiose share %).
8. **Extensible**: manifest is forward-compatible via `x-*` custom fields and a `manifest_version` pin.

## 3. Manifest structure (YAML)

A skill lives as a directory:

```
my-skill/
├── skill.yaml            # the manifest — required
├── system_prompt.md      # the skill's "agent-ness" — required
├── examples/             # few-shot demos used by the Matching Agent and for eval
│   ├── 01-basic.yaml
│   └── 02-edge.yaml
├── tools/                # optional: MCP server refs, function schemas
│   └── tools.yaml
└── assets/               # optional: templates, prompts, checklists the skill uses
```

Only `skill.yaml` and `system_prompt.md` are mandatory. Everything else is optional.

### 3.1 Full annotated `skill.yaml`

```yaml
manifest_version: "1.0"                  # skill manifest schema version

# -- 1. Identity ---------------------------------------------------------
id: audit-ux-express                     # globally unique slug, kebab-case
name: "Audit UX Express"                 # human-readable, i18n-aware
version: "1.2.0"                         # semver
created_at: "2026-04-10T09:00:00Z"
updated_at: "2026-04-16T14:00:00Z"

# -- 2. Authorship & provenance ------------------------------------------
author:
  type: "native"                         # native | community | external
  id: "symbiose"                         # Symbiose team, or talent_id, or "external:anthropic"
  display_name: "Symbiose Core Team"
source:
  kind: "native"                         # native | community | claude-skill | mcp-server | github | web
  origin_url: null                       # non-null for imported skills
  adapter: null                          # adapter used if imported (see §6)
  license: "MIT"                         # or "proprietary", "CC-BY-SA", etc.

# -- 3. Description -------------------------------------------------------
description:
  short: "Audit express UX d'un parcours web en 4h, rapport synthétique livrable."
  long: |
    This skill guides the talent through a structured 4-hour UX audit:
    heuristic scan, 3 representative user flows, quick-win table, executive
    summary. Output is a ready-to-send PDF + editable deck.
  intended_for: |
    A UX-competent talent (junior to confirmed) who needs to produce a
    credible audit on a tight deadline without building the framework
    from scratch.
  non_goals: |
    Not a substitute for an in-depth UX research study (usability testing,
    interviews). Not for native mobile apps (web only in v1).

# -- 4. Taxonomy (what the Matching Agent searches on) -------------------
taxonomy:
  domains: ["design", "ux", "product"]
  sub_domains: ["audit", "heuristic-evaluation", "conversion"]
  tags: ["express", "deliverable-ready", "client-facing", "web-only"]
  seniority_target: ["junior", "confirmed"]   # junior | confirmed | senior | expert
  mission_phases: ["discovery", "audit"]       # discovery | audit | design | build | review | handover
  languages: ["fr", "en"]                      # languages the skill operates in

# -- 5. Interface contract ------------------------------------------------
interface:
  inputs:                                      # what the skill consumes
    - name: "target_url"
      type: "string"
      required: true
      description: "URL to the web experience to audit"
    - name: "business_goal"
      type: "string"
      required: true
      description: "Primary conversion goal stated by the client"
    - name: "personas"
      type: "array<string>"
      required: false
      description: "Named user personas to evaluate against"
  outputs:                                     # what the skill produces
    - name: "audit_report_pdf"
      type: "file:pdf"
      description: "Client-ready audit report"
    - name: "quick_wins_table"
      type: "structured:table"
      description: "Prioritized quick-wins (impact × effort)"
  preconditions:
    - "Target URL must be publicly accessible"
    - "Client has validated the business_goal statement"
  side_effects:
    - "Accesses target URL via headless browser (read-only)"
    - "May take screenshots stored in mission workspace"

# -- 6. Tools & dependencies ---------------------------------------------
tools:
  mcp_servers:                                 # MCP servers required at runtime
    - id: "playwright-mcp"
      version: ">=0.8.0"
      scope: ["read-web"]
  function_tools:                              # function-tool specs (JSON Schema)
    - $ref: "tools/tools.yaml#/take_screenshot"
  web_access: true                             # does the skill need internet?
  file_access:
    read: ["mission_workspace/*"]
    write: ["mission_workspace/audits/*"]
  depends_on_skills:                           # other skills this one chains / consumes
    - id: "heuristic-framework-nielsen"
      version: "^1.0.0"

# -- 7. Runtime compatibility --------------------------------------------
runtime:
  llm:
    preferred: "claude-opus-4-7"
    tested: ["claude-opus-4-7", "claude-sonnet-4-6"]
    min_context_tokens: 60000
  estimated_cost_per_run: "€0.80"              # indicative, measured over 10 runs
  estimated_latency_p50: "180s"
  estimated_latency_p95: "420s"

# -- 8. Safety profile ---------------------------------------------------
safety:
  pii_handling: "processes-pii"                # none | processes-pii | stores-pii
  data_egress: "workspace-only"                # none | workspace-only | external-api | internet
  injection_risk: "low"                        # low | medium | high (auto-scored + human-reviewed)
  sandbox_level: "strict"                      # strict | moderate | trusted
  review_status: "certified-v1"                # unreviewed | community-reviewed | certified-v1 | deprecated
  reviewed_by: ["symbiose-safety-review-agent", "human:@ad-qualite"]
  reviewed_at: "2026-04-15T10:00:00Z"
  human_oversight_required: false              # true = talent must validate each output
  content_warnings: []

# -- 9. Governance & usage -----------------------------------------------
governance:
  certified: true                              # certification badge (reviewed + quality threshold)
  certification_level: "gold"                  # bronze | silver | gold
  usage_count: 142
  success_rate: 0.91                           # downstream mission NPS ≥ 4/5
  avg_rating: 4.6
  disable_rate: 0.08                           # % of missions where talent disabled this skill
  deprecated: false
  deprecated_reason: null
  replaced_by: null

# -- 10. Economics -------------------------------------------------------
economics:
  price_model: "per-run"                       # per-run | per-mission | flat | free
  price_tokens: 50                             # Symbiose tokens (see business model)
  author_share_pct: 70                         # % going to the author
  platform_share_pct: 30

# -- 11. Lifecycle -------------------------------------------------------
lifecycle:
  status: "active"                             # draft | beta | active | deprecated | archived
  published_at: "2026-04-10T09:00:00Z"
  archived_at: null

# -- 12. Extension fields (forward-compat) -------------------------------
x-symbiose-internal:
  onboarded_by: "team:product"
  notes: "Used as reference skill for Matching Agent evals."
```

## 4. Field reference (normative)

### 4.1 Required top-level keys

| Key | Purpose |
|-----|---------|
| `manifest_version` | Pins the manifest schema. Enables migrations. |
| `id`, `name`, `version` | Identity triple. `version` is **semver**. |
| `author`, `source` | Authorship + provenance (critical for imported skills). |
| `description.short`, `description.long` | Prose used by the Matching Agent (`short` feeds vectorization; `long` feeds rationale generation). |
| `taxonomy` | The Matching Agent's primary filtering surface. |
| `interface.inputs`, `interface.outputs` | Machine-readable I/O contract. |
| `safety` | Mandatory. No skill ships without a safety profile. |

### 4.2 Semver policy

- **MAJOR**: breaking change to `interface.inputs` / `interface.outputs`, or safety regression.
- **MINOR**: new optional input, new output, improved prompt, unchanged I/O contract.
- **PATCH**: bug fix, typo, rewording, no behavior change.
- Missions pin the exact version used at activation time. Upgrades require explicit Matching Agent re-run.

### 4.3 `source.kind` allowed values

| Value | Meaning |
|-------|---------|
| `native` | Authored by Symbiose team. |
| `community` | Authored by a talent on the platform. |
| `claude-skill` | Imported from an Anthropic Claude Skill (via adapter). |
| `mcp-server` | Wraps an MCP server as a Symbiose skill. |
| `github` | Imported from a GitHub repo following a convention. |
| `web` | Fetched from a URL (static prompt / guide). |

### 4.4 `safety` — mandatory fields and their meaning

Any skill with `injection_risk: high` or `data_egress: internet` MUST set `sandbox_level: strict` and `human_oversight_required: true`. The Safety-Review Agent enforces this at publication time.

## 5. Safety & governance lifecycle

```
       ┌────────────┐   submit      ┌──────────────────────┐
       │  author    │ ────────────▶ │  Safety-Review Agent │
       └────────────┘               │   - prompt injection │
                                    │   - PII leakage      │
                                    │   - bias / misuse    │
                                    │   - dependency audit │
                                    └──────────┬───────────┘
                                               │
                      ┌────────────────────────┴────────────────────────┐
                      │                                                  │
                      ▼                                                  ▼
           review_status: community-reviewed               review_status: blocked
           (visible, badge: community)                      (not published, feedback to author)
                      │
                      │  usage_count ≥ N AND success_rate ≥ T
                      ▼
           review_status: certified-v1
           governance.certified: true
           certification_level: bronze|silver|gold (by metrics tier)
```

Runtime monitoring continuously updates `governance.*` metrics. If `success_rate` drops below a threshold (TBD), the skill is flagged `deprecated: true` and the Matching Agent stops selecting it.

## 6. Importing external skills (adapters)

The **Skill-Importer Agent** (cf. `01-agent-architecture.md` §2) uses adapters to normalize external sources into a Symbiose manifest.

### 6.1 Adapter contract

An adapter is a function:

```
adapter(source_ref: URI, hints: dict) -> SkillBundle
```

where `SkillBundle = (skill.yaml, system_prompt.md, tools/*, assets/*)` conforming to §3.

### 6.2 Adapters shipping in v1

| Adapter | Input | Mapping strategy |
|---------|-------|------------------|
| `claude-skill-adapter` | Anthropic Claude Skill package | Direct: Claude Skills are already manifest + prompt + tools. Map fields 1:1, generate safety profile via Safety-Review Agent. |
| `mcp-adapter` | MCP server URL | Wrap as a skill exposing the server's tools. Generate a minimal `system_prompt.md` from the server's declared capabilities. Author = `external:<domain>`. |
| `github-adapter` | GitHub repo URL | Look for `/symbiose-skill/skill.yaml` at repo root; if absent, scan for README + prompt files and propose a draft manifest (human review required). |
| `web-adapter` | Static URL (prompt / guide) | Wrap content as a read-only reference skill. Very limited; `sandbox_level: strict`. |

### 6.3 Imported skill rules

- **Provenance preserved**: `source.origin_url` must be non-null and point to the exact source revision.
- **No auto-certification**: imported skills start at `review_status: community-reviewed` at best.
- **License compatibility**: adapter fails if the source license is incompatible with Symbiose terms.
- **Author attribution**: `author.display_name` reflects the original author; token splits go to Symbiose by default until the author claims the skill.

## 7. Worked examples

### 7.1 Native skill (excerpt)

```yaml
id: executive-summary-generator
name: "Executive Summary Generator"
version: "2.0.1"
author: { type: native, id: symbiose, display_name: "Symbiose Core Team" }
source: { kind: native, origin_url: null }
taxonomy:
  domains: ["consulting", "writing"]
  seniority_target: ["junior", "confirmed", "senior"]
  mission_phases: ["handover", "review"]
safety: { pii_handling: none, data_egress: none, injection_risk: low, sandbox_level: moderate, review_status: certified-v1 }
```

### 7.2 Community skill (excerpt)

```yaml
id: b2b-cold-email-senior
name: "B2B Cold Email — Senior playbook"
version: "1.0.0"
author: { type: community, id: talent_7f3b2, display_name: "Élise M." }
source: { kind: community, origin_url: null, license: "CC-BY-SA" }
taxonomy:
  domains: ["marketing", "sales", "copywriting"]
  seniority_target: ["senior"]
safety: { pii_handling: processes-pii, data_egress: workspace-only, injection_risk: medium, sandbox_level: strict, review_status: community-reviewed }
economics: { price_model: per-run, price_tokens: 20, author_share_pct: 70, platform_share_pct: 30 }
```

### 7.3 Imported MCP skill (excerpt)

```yaml
id: google-analytics-reader
name: "Google Analytics 4 Reader"
version: "0.3.0"
author: { type: external, id: "external:google", display_name: "Google (via MCP)" }
source:
  kind: mcp-server
  origin_url: "https://github.com/example/ga4-mcp-server@v0.3.0"
  adapter: "mcp-adapter"
  license: "Apache-2.0"
tools:
  mcp_servers:
    - id: "ga4-mcp"
      version: "0.3.0"
      scope: ["read-analytics"]
safety: { pii_handling: processes-pii, data_egress: external-api, injection_risk: medium, sandbox_level: strict, review_status: community-reviewed, human_oversight_required: true }
```

## 8. What a skill is NOT

To keep the boundary clear:

- A skill is **not a full agent**. Agents (Brief-Parser, Matching, Copilot...) *consume* skills. A skill is closer to a "tool + prompt + recipe + metadata" bundle.
- A skill is **not a workflow**. Workflows (mission plans) are generated by the Plan-Builder Agent *using* skills.
- A skill is **not a document**. A guide or template without a prompt + I/O contract belongs in `assets/` of a skill, not as a skill on its own.

## 9. Open questions

1. **`id` namespacing**: flat slugs (`audit-ux-express`) vs namespaced (`symbiose/audit-ux-express`, `community/elise-m/b2b-cold-email`)? Namespacing prevents collisions once imports scale.
2. **Localization**: `description` is currently mono-text. Should it be `{fr: "...", en: "..."}`? Yes probably, but cost is higher authoring friction.
3. **Dependency resolution**: if two skills in a mission depend on different majors of the same sub-skill, what happens? (Symbiose-side resolver vs let the Matching Agent handle.)
4. **Offline-capable skills**: do we surface a `runtime.offline: true` flag for skills that work without web access (useful for regulated clients)?
5. **Token pricing**: static `price_tokens` in the manifest vs dynamic pricing by the Matching Agent (based on demand / scarcity)?
6. **Author revenue when the skill is imported**: default route is "Symbiose keeps 100% until claimed" — confirm or pick another default.
7. **Manifest validation**: what tool validates a skill before publication? JSON-Schema + custom rules + Safety-Review Agent. Do we ship a CLI (`symbiose skill lint`) at MVP?
8. **Skill vs MCP server granularity**: one MCP server with 10 tools = 1 Symbiose skill or 10? Proposal: **1 skill per coherent capability**, not per tool. An MCP server with both "read GA" and "send Slack message" would produce 2 skills.
9. **Certification thresholds**: bronze/silver/gold — which exact metrics and cut-offs? Draft:
   - Bronze: ≥ 10 runs, avg_rating ≥ 4.0, disable_rate ≤ 0.20.
   - Silver: ≥ 50 runs, avg_rating ≥ 4.3, disable_rate ≤ 0.12.
   - Gold: ≥ 200 runs, avg_rating ≥ 4.5, disable_rate ≤ 0.08, human review passed.
10. **Example format**: are example files used only by the Matching Agent (few-shot retrieval) or also by Copilot at runtime? Probably both — need to clarify the shape.

## 10. Next steps

1. Validate the 10 open questions (batch review with user).
2. Freeze the JSON-Schema derived from this document → `docs/tech/schemas/skill.schema.json`.
3. Write **Matching Agent spec v1** (`docs/tech/03-matching-agent.md`) grounded on this manifest.
4. Draft a `symbiose skill lint` CLI spec (post-MVP optional).
5. Define the **first 5 native skills** to build, using this manifest as the template.
