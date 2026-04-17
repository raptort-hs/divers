# 06 — Data model v1

**Status: v1 — MVP.** **Language: English.**

Canonical entities for Symbiose MVP. SQLite at MVP (single-file, zero-config), PostgreSQL in production.

---

## 1. Entities (high level)

```
User ─┬─< TalentProfile >─ SkillActivation >─ Mission
      └─< CompanyAdmin >─ Company ─< Need ─< Mission >─< MissionPlanStep
                                                     >─< Deliverable
                                                     >─< SkillRun
                                                     >─< Feedback
                                                     >─< LedgerEntry
Skill ─< SkillVersion
User ─< TokenAccount ─< TokenTx
```

## 2. Table definitions (abbreviated)

```sql
-- core identity
CREATE TABLE user (
  id            TEXT PRIMARY KEY,             -- u_<ulid>
  email         TEXT UNIQUE NOT NULL,
  hashed_pw     TEXT NOT NULL,
  role          TEXT NOT NULL CHECK(role IN ('talent','company_admin','symbiose_staff')),
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_login_at TIMESTAMP
);

CREATE TABLE talent_profile (
  user_id         TEXT PRIMARY KEY REFERENCES user(id),
  display_name    TEXT NOT NULL,
  seniority       TEXT CHECK(seniority IN ('junior','confirmed','senior','expert')),
  domains         JSON NOT NULL,      -- ["design","ux"]
  strengths       JSON,
  gaps            JSON,
  languages       JSON,               -- ["fr","en"]
  bio_fr          TEXT,
  bio_en          TEXT,
  tokens_balance  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE company (
  id           TEXT PRIMARY KEY,        -- c_<ulid>
  name         TEXT NOT NULL,
  size_bucket  TEXT CHECK(size_bucket IN ('1-10','11-50','51-200','200+')),
  country      TEXT DEFAULT 'FR'
);

CREATE TABLE company_admin (
  user_id     TEXT REFERENCES user(id),
  company_id  TEXT REFERENCES company(id),
  role        TEXT,
  PRIMARY KEY (user_id, company_id)
);

-- mission funnel
CREATE TABLE need (
  id           TEXT PRIMARY KEY,        -- n_<ulid>
  company_id   TEXT NOT NULL REFERENCES company(id),
  raw_brief    TEXT NOT NULL,
  parsed_brief JSON,                    -- Brief-Parser Agent output
  status       TEXT CHECK(status IN ('draft','clarifying','ready','matched','archived')),
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mission (
  id             TEXT PRIMARY KEY,      -- m_<ulid>
  need_id        TEXT NOT NULL REFERENCES need(id),
  talent_id      TEXT REFERENCES user(id),
  status         TEXT CHECK(status IN ('proposed','accepted','running','review','closed','cancelled')),
  plan           JSON,                  -- from Matching Agent output
  budget_eur     INTEGER,
  deadline       DATE,
  workspace_path TEXT NOT NULL,
  autonomy_level TEXT CHECK(autonomy_level IN ('manual','guided','auto')) DEFAULT 'guided',
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skill_activation (
  id           TEXT PRIMARY KEY,        -- sa_<ulid>
  mission_id   TEXT NOT NULL REFERENCES mission(id),
  skill_id     TEXT NOT NULL,           -- matches skill.yaml:id
  skill_version TEXT NOT NULL,
  rationale_fr TEXT NOT NULL,
  activated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (mission_id, skill_id, skill_version)
);

-- runtime
CREATE TABLE skill_run (
  id             TEXT PRIMARY KEY,      -- sr_<ulid>
  mission_id     TEXT NOT NULL REFERENCES mission(id),
  skill_activation_id TEXT NOT NULL REFERENCES skill_activation(id),
  inputs         JSON NOT NULL,
  outputs        JSON,
  cost_tokens    INTEGER,
  duration_ms    INTEGER,
  status         TEXT CHECK(status IN ('started','succeeded','failed','cancelled')),
  started_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ended_at       TIMESTAMP,
  error          TEXT
);

CREATE TABLE deliverable (
  id           TEXT PRIMARY KEY,
  mission_id   TEXT NOT NULL REFERENCES mission(id),
  skill_run_id TEXT REFERENCES skill_run(id),
  kind         TEXT NOT NULL,           -- 'file:pdf' | 'structured:table' | 'markdown' ...
  path         TEXT NOT NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sent_to_client_at TIMESTAMP
);

CREATE TABLE feedback (
  id           TEXT PRIMARY KEY,
  mission_id   TEXT NOT NULL REFERENCES mission(id),
  author_user_id TEXT REFERENCES user(id),
  target       TEXT CHECK(target IN ('mission','talent','skill')),
  target_id    TEXT,                    -- skill_activation.id if target='skill'
  rating       INTEGER CHECK(rating BETWEEN 1 AND 5),
  comment      TEXT,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- governance ledger (append-only)
CREATE TABLE ledger_entry (
  id           TEXT PRIMARY KEY,
  mission_id   TEXT REFERENCES mission(id),
  event_type   TEXT NOT NULL,          -- 'skill.run','plan.update','deliverable.sent', ...
  payload      JSON NOT NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- tokens (off-chain MVP)
CREATE TABLE token_account (
  user_id       TEXT PRIMARY KEY REFERENCES user(id),
  balance       INTEGER NOT NULL DEFAULT 0,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE token_tx (
  id           TEXT PRIMARY KEY,
  user_id      TEXT NOT NULL REFERENCES user(id),
  delta        INTEGER NOT NULL,        -- positive = credit, negative = debit
  reason       TEXT NOT NULL,           -- 'skill.run','author.payout','signup.bonus', ...
  ref_id       TEXT,                    -- optional foreign ref (skill_run.id, etc.)
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- skill registry (local index; source of truth is skill bundles on disk or imported)
CREATE TABLE skill_registry (
  skill_id     TEXT NOT NULL,
  version      TEXT NOT NULL,
  manifest     JSON NOT NULL,          -- parsed skill.yaml
  system_prompt TEXT NOT NULL,
  governance   JSON,                   -- mirror of skill.yaml:governance, kept hot
  indexed_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (skill_id, version)
);
```

## 3. Key invariants

- `skill_activation` is immutable once set — mutation = new row, previous archived via `activated_at` timestamp comparison in application logic.
- `ledger_entry` is **append-only**. No updates, no deletes. Source of truth for certification metrics.
- `token_tx` sums must equal `token_account.balance` (application invariant; periodic reconciliation job).
- `mission.plan` snapshots the Matching Agent output at acceptance; subsequent plan changes are stored as `ledger_entry(event_type='plan.update')`.

## 4. ULID IDs

All IDs are prefixed ULIDs: `u_01HWX...`, `m_01HWY...`. Rationale: sortable by creation time, URL-safe, no collision.

## 5. Migrations

MVP: single init script `backend/symbiose/db/init.sql`. Schema evolution deferred to Alembic post-MVP.

## 6. Privacy & retention

- `user.hashed_pw` uses argon2id (see `08-adr-stack.md`).
- PII minimization: no phone, no address stored at MVP.
- Mission workspaces: retained 90 days post-closure, then anonymized (content hashed).
- Ledger entries: retained 2 years.

## 7. Seed data (dev)

`backend/symbiose/db/seed.sql` inserts: 2 companies, 3 talent profiles (Léa, Marc, Amine matching personas), 5 skill bundles loaded from `skills/native/*`. Used by `symbiose demo`.
