# Skills — Symbiose MVP

Bundles de skills conformes au manifest v1 (`docs/tech/02-skill-format.md`).

Arborescence :

```
skills/
├── native/                          # skills authored by Symbiose
│   ├── audit-ux-express/
│   ├── executive-summary-generator/
│   ├── meeting-notes-to-actions/
│   ├── client-deck-builder/
│   └── technical-spec-writer/
├── community/                       # @handle/slug (populé par les talents)
└── external/                        # @source-handle/slug (populé par le Skill-Importer Agent)
```

Chaque bundle a :

```
<id>/
├── skill.yaml               # manifest v1
├── system_prompt.md         # le cœur agent
└── examples/
    └── 01-basic.yaml        # exemple canonique
```

## Skills natifs MVP (5)

| id | Certif | Domaine | Phases | Tokens |
|----|--------|---------|--------|--------|
| `audit-ux-express` | silver | design / ux | discovery, audit | 50 |
| `executive-summary-generator` | gold | consulting / writing | handover, review | 15 |
| `meeting-notes-to-actions` | gold | project-management | discovery, review, handover | 5 |
| `client-deck-builder` | bronze | communication / consulting | handover, review | 25 |
| `technical-spec-writer` | bronze | engineering / software | design, build | 30 |

## Validation

Chaque `skill.yaml` est validé contre `docs/tech/schemas/skill.schema.json` via le Safety-Review Agent à la publication et au démarrage du backend (`backend/symbiose/skills/registry.py`).
