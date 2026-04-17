# Symbiose

**La première plateforme de travail augmenté par IA.**

Symbiose réinvente le freelancing autour de trois principes : matching intelligent, copilote IA intégré, et redistribution équitable via un système de tokens de gouvernance. L'anti-Uber du travail indépendant — un modèle où la technologie augmente les humains au lieu de les précariser.

## État d'avancement (avril 2026)

- **Phase 0 — Cadrage** : clos.
- **Phase 1 — MVP** : **squelette bout-en-bout livré**. Skill manifest v1 figé, 5 skills natifs, 3 agents (Brief-Parser, Matching, Mission Copilot), backend FastAPI, CLI de démo, frontend minimal FastAPI+Jinja+HTMX. 12 tests unitaires verts.

## Démo en 30 secondes

```bash
cd backend
pip install -e .
symbiose demo --execute
# ou
symbiose serve   # FastAPI sur http://127.0.0.1:8000
```

Détails complets dans [`backend/README.md`](backend/README.md).

## Arborescence

```
divers/
├── README.md / CLAUDE.md              # règles de vie du projet
├── docs/                              # mémoire produit (FR) + technique (EN)
│   ├── 01-vision.md ... 08-environnement-prestataire.md
│   ├── flows/onboarding-pme.md
│   └── tech/                          # specs techniques + ADR + JSON-Schema
├── skills/native/                     # 5 skills natifs MVP (bundles YAML)
└── backend/                           # backend Python (FastAPI + agents + CLI)
```

## Documentation

### Produit (FR)

- [`docs/01-vision.md`](docs/01-vision.md) — Pourquoi Symbiose.
- [`docs/02-proposition-valeur.md`](docs/02-proposition-valeur.md) — Proposition & bénéfices clés.
- [`docs/03-produit.md`](docs/03-produit.md) — Les 6 modules produit.
- [`docs/04-business-model.md`](docs/04-business-model.md) — Commission, abonnements, tokens.
- [`docs/05-roadmap.md`](docs/05-roadmap.md) — Phases & priorités.
- [`docs/06-journal.md`](docs/06-journal.md) — Historique daté des décisions et avancées.
- [`docs/07-personas.md`](docs/07-personas.md) — Personas & parcours.
- [`docs/08-environnement-prestataire.md`](docs/08-environnement-prestataire.md) — **Cœur produit** : écosystème de skills, matching agent-native.
- [`docs/flows/onboarding-pme.md`](docs/flows/onboarding-pme.md) — Tunnel onboarding PME.

### Technique (EN)

- [`docs/tech/01-agent-architecture.md`](docs/tech/01-agent-architecture.md) — Agent-native orchestration + catalogue agents.
- [`docs/tech/02-skill-format.md`](docs/tech/02-skill-format.md) — **Skill manifest v1 figé**.
- [`docs/tech/03-matching-agent.md`](docs/tech/03-matching-agent.md) — Matching Agent spec.
- [`docs/tech/04-brief-parser-agent.md`](docs/tech/04-brief-parser-agent.md) — Brief-Parser Agent spec.
- [`docs/tech/05-mission-copilot-agent.md`](docs/tech/05-mission-copilot-agent.md) — Mission Copilot Agent spec.
- [`docs/tech/06-data-model.md`](docs/tech/06-data-model.md) — Entities, tables, invariants.
- [`docs/tech/07-api-spec.md`](docs/tech/07-api-spec.md) — REST + SSE.
- [`docs/tech/08-adr-stack.md`](docs/tech/08-adr-stack.md) — Décisions de stack.
- [`docs/tech/schemas/skill.schema.json`](docs/tech/schemas/skill.schema.json) — JSON-Schema manifest.

## Règle d'or

Chaque session met à jour `docs/06-journal.md` et les docs thématiques concernées. Voir [`CLAUDE.md`](CLAUDE.md) pour le contrat mémoire.
