# 05 — Mission Copilot Agent (spec)

**Status: v1 — MVP spec.** **Language: English.**

The **Mission Copilot Agent** lives inside the talent's mission workspace once a mission is activated. It knows the mission, the talent profile, the activated skills, and the plan. It guides, executes skills on demand, and maintains state across the mission.

---

## 1. Purpose

Once the Matching Agent has proposed a skill set and the talent has accepted, the Copilot takes over runtime. It is the talent's **mission-aware assistant**:

- Executes skills (kicks off `audit-ux-express`, gathers inputs, delivers outputs into the workspace).
- Keeps a short-horizon plan (next 3 steps) visible.
- Answers "what do I do next?" in one sentence.
- Flags quality issues before the talent sends deliverables to the client.
- Logs everything to the mission ledger for governance + certification metrics.

## 2. Context it carries

At every turn, the Copilot has access to:

- `mission` (full object from `06-data-model.md`): brief, plan, deliverables so far, budget, deadline.
- `talent`: profile, activated skills, historical metrics.
- `skill_registry.local_cache`: the N skills pinned to this mission (full manifests + prompts + examples).
- `workspace`: file tree of the mission (read/write), conversation log with the client.
- `ledger`: cost-to-date in tokens, API calls, skill runs.

## 3. Output surfaces

The Copilot does not emit a single JSON — it's a **long-running conversational agent** driving a UI. Its behavior is defined by the following events it can produce:

| Event | Payload | UI reaction |
|-------|---------|-------------|
| `assistant_message` | `{text, attachments?}` | Render bubble in chat. |
| `skill_run_start`   | `{skill_id, version, inputs}` | Show run spinner + inputs summary. |
| `skill_run_result`  | `{skill_id, run_id, outputs, duration_ms, cost_tokens}` | Render outputs (file preview, table, etc.) + ledger update. |
| `plan_update`       | `{plan: PlanStep[]}` | Refresh the "Next 3 steps" panel. |
| `quality_warning`   | `{severity, message, deliverable_id}` | Inline warning on the deliverable. |
| `client_message_draft` | `{text}` | Drops a draft reply in the client-facing thread (talent reviews before send). |
| `request_human`     | `{reason}` | Alerts the talent: needs your call. |

## 4. Tools

| Tool | Purpose |
|------|---------|
| `skill.run` | Executes a pinned skill with inputs; streams outputs back. |
| `workspace.read` / `workspace.write` | Read/write files in the mission workspace (path-scoped). |
| `workspace.list` | List workspace contents. |
| `mission.update_plan` | Replace the current plan (stores history). |
| `mission.log_event` | Append to the mission ledger. |
| `client.send_draft` | Send a drafted message to the client (requires talent approval at MVP). |
| `registry.lookup` | Look up skill info (not used to add new skills — activation is frozen at mission start). |

Skill activation is **frozen** at mission start — the Copilot cannot add new skills mid-mission without going back through the Matching Agent.

## 5. System prompt (sketch)

> You are the Mission Copilot. You are assigned to exactly ONE mission. You know the brief, the plan, the activated skills, and the talent's profile. Your job is to help the talent execute the mission with minimum friction and maximum quality.
>
> Rules:
> 1. Every answer is **mission-grounded** — reference the brief, the plan, or a specific deliverable.
> 2. When the talent asks "what's next?", answer with the single highest-value next step.
> 3. When you run a skill, show the talent the inputs you used before execution (unless the talent has granted auto-run).
> 4. Quality-check deliverables before they leave the workspace. If something looks off (missing section, factual inconsistency, tone mismatch), emit `quality_warning`.
> 5. Stay in the mission's language (fr / en) unless the talent switches.
> 6. Never surprise the talent with irreversible actions (sending to client, deleting files) — always draft + confirm.
> 7. When stuck, emit `request_human` rather than guessing.

## 6. Autonomy levels

The talent sets an autonomy dial (UI) at mission start:

| Level | Behavior |
|-------|----------|
| `manual`  | Copilot suggests only. Talent triggers every skill run. |
| `guided`  | Copilot drafts + asks confirmation before each run. (Default.) |
| `auto`    | Copilot runs skills and drafts client messages autonomously; talent reviews at checkpoints. |

## 7. Eval

Offline eval runs 10 canned missions end-to-end. Metrics:
- **Plan drift**: number of plan updates per mission. Baseline < 5.
- **Skill run success rate**: ≥ 0.90.
- **Quality warnings precision**: ≥ 0.80 (don't cry wolf).
- **Talent intervention rate** (requests for human): should drop over time as skills mature.

## 8. Interactions

- **Upstream**: activated by mission acceptance event from the Matching Agent output.
- **Sideways**: Safety-Review Agent can intervene at runtime on `quality_warning` severity = high.
- **Downstream**: writes to the governance ledger → feeds certification metrics of skills used.
