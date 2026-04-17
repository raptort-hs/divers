# Symbiose backend — MVP

Python 3.11+ · FastAPI · Skill registry · 3 agents (Brief-Parser, Matching, Mission Copilot) · CLI.

## Installation

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate    # optionnel
pip install -e .
```

Optionnel : tests et LLM réel.

```bash
pip install -e '.[dev,llm]'
```

## Démo CLI — bout-en-bout

Exécute **parsing + matching** sur un brief de démo FR :

```bash
symbiose demo
```

Exécute **aussi** le plan par le Mission Copilot (sortie simulée si pas d'API key) :

```bash
symbiose demo --execute
```

Lance avec ton propre brief :

```bash
symbiose demo "Audit UX boutique Shopify, budget 5000€, délai 10 jours, rapport + plan d'action"
```

## Autres commandes CLI

```bash
symbiose skills list            # inventaire du registre
symbiose skills validate        # valide tous les skill.yaml contre le JSON-Schema
symbiose serve                  # FastAPI sur http://127.0.0.1:8000
```

## Serveur web — parcours onboarding

```bash
symbiose serve
# puis ouvrir http://127.0.0.1:8000
```

Routes web :

| Route | Description |
|-------|-------------|
| `/` | Landing |
| `/onboarding` | Formulaire brief libre (PME) |
| `/mission/{id}` | Mission proposée par le Matching Agent |
| `/mission/{id}/live` | Flux SSE du Mission Copilot |
| `/skills` | Registre |
| `/api/v1/health` · `/api/v1/skills` · `/api/v1/skills/{id}` · `/api/v1/missions/{id}` | API JSON |
| `/docs` | Swagger UI (OpenAPI 3.1) |

## LLM : mode fixture vs Anthropic

Par défaut (`SYMBIOSE_LLM_MODE=fixture`), aucun appel LLM réel n'est fait :
- le Brief-Parser utilise un parser heuristique FR suffisant pour les briefs typiques ;
- le Matching Agent est **déterministe** (scoring par taxonomie / gouvernance / budget) ;
- le Mission Copilot retourne des outputs simulés qui respectent le schéma de chaque skill.

Pour activer l'appel LLM réel :

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export SYMBIOSE_LLM_MODE=anthropic
export SYMBIOSE_MODEL=claude-opus-4-7    # ou claude-sonnet-4-6
pip install -e '.[llm]'
symbiose demo --execute
```

## Tests

```bash
python -m pytest tests/ -v
```

12 tests couvrent :
- validation JSON-Schema des 5 skills natifs ;
- chargement registre + filtres (domain, phase) ;
- Brief-Parser : extraction budget / deadline / missing_info / red_flags ;
- Matching Agent : sélection pertinente, respect budget, plan phase-ordonné, rationale non vide.

## Arborescence

```
backend/
├── pyproject.toml
├── symbiose/
│   ├── config.py              # runtime config (env vars)
│   ├── cli.py                 # Typer CLI
│   ├── main.py                # FastAPI app (web + API)
│   ├── models/                # Pydantic : Brief, Mission, Skill, Talent
│   ├── skills/                # registry + JSON-Schema validator
│   ├── llm/                   # abstraction (Fixture | Anthropic)
│   ├── agents/                # brief_parser, matching, mission_copilot
│   └── web/                   # Jinja + HTMX templates + static
└── tests/
```

## Décisions de stack

Voir [`../docs/tech/08-adr-stack.md`](../docs/tech/08-adr-stack.md).

## Limites connues du MVP

- Pas de base de données — état en mémoire uniquement (redémarrage = reset).
- Pas d'auth.
- Pas d'adapters externes implémentés (MCP, Claude Skills, GitHub) — specs rédigées.
- Mission Copilot simulé en mode fixture.
