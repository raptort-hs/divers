# 05 — Roadmap

## Phase 0 — Setup ✅

- [x] Structure documentaire initiale (`README.md`, `CLAUDE.md`, `docs/01` à `docs/07`).
- [x] Import du pitch v1.
- [x] Personas & parcours utilisateurs v1 (3 talents + 3 clients).
- [x] Périmètre MVP cadré (5 questions tranchées).

## Phase 1 — MVP

### Cadrage verrouillé (2026-04-16)

- **Client MVP** : C1 — Sophie, dirigeante de PME 20-50 pers.
- **Talents MVP** : mix juniors + seniors (T1, T2, T3) activés dès le lancement.
- **Missions à impact** : ❌ pas au MVP → Phase 2.
- **Tokens** : MVP minimal (compteur interne off-chain, attribution post-mission, pas de gouvernance on-chain).
- **Géographie** : France seule.

### Scope modules — validé 2026-04-16

| # | Module | MVP ? | Périmètre MVP proposé |
|---|--------|-------|------------------------|
| 1 | Profil augmenté | ✅ | CV dynamique, compétences, dispo, valeurs. Badges basiques. Pas de niveaux gamifiés. |
| 2 | Matching intelligent | ✅ | Reco de missions pour talents + reco de profils pour PME. Algo simple (mots-clés + valeurs + budget) au début, IA en itération. |
| 3 | Marketplace missions | ✅ | Missions rémunérées uniquement (pas de missions tokens/impact). Filtres : domaine, durée, budget. |
| 4 | Espace mission collaboratif | ✅ partiel | Timeline + checklists + chat humain. **Copilote IA basique** (rédaction brief, aide candidature, synthèse livrables). Pas de génération code/contenu avancée. |
| 5 | Feedback & progression | ✅ partiel | Évaluations croisées talent ↔ client. **Pas** de badges/XP/micro-formations au MVP (Phase 2). |
| 6 | Tokens & gouvernance | ✅ minimal | Compteur tokens off-chain attribués après mission réussie. Affichage dans profil. **Pas** de gouvernance, pas de votes, pas d'échange. |

### Modules / fonctions transverses MVP

- Inscription + KYC simplifié (FR).
- Paiement sécurisé (escrow via prestataire type Stripe Connect / Lemonway).
- Facturation automatisée talent ↔ PME.
- Contractualisation simple (template contrat freelance, signature électronique).
- Dashboard PME (missions en cours, historique).
- Dashboard talent (missions, revenus, tokens, feedbacks).

### Indicateurs de succès MVP (à discuter)

- **Activation client** : X PME inscrites et ayant déposé ≥ 1 besoin dans les 3 premiers mois.
- **Matching efficace** : > 60 % des besoins reçoivent ≥ 3 candidatures qualifiées en < 72h.
- **Première mission** : > 40 % des besoins aboutissent à une mission signée.
- **NPS** : NPS client > 40, NPS talent > 30.
- **GMV** : X € de volume de transactions sur 6 mois post-lancement.

*Chiffres précis à caler après discussion.*

## Phase 2 — Extension

- Copilote IA profond (génération code / contenu / plans, intégrations IDE).
- Gamification complète (badges, niveaux, XP, micro-formations).
- Missions à impact + clients C2 (grands groupes) + C3 (ONG).
- Tokens on-chain + gouvernance (votes, redistribution).
- Abonnements premium (talents & entreprises).

## Phase 3 — Scale

- Internationalisation : BE, CH, puis Europe.
- Projets sponsorisés RSE à grande échelle.
- Pools freelances pour grands comptes.

## Backlog (idées parking)

- Système d'apprentissage par pairs (mentoring entre freelances).
- Marketplace de templates de mission.
- Insights sectoriels (benchmarks tarifs, tendances compétences).

## Squelette MVP livré — 2026-04-17

L'utilisateur a demandé une livraison bout-en-bout en autonomie. Squelette fonctionnel posé :

1. ✅ **Skill manifest v1 figé** — `docs/tech/02-skill-format.md` (10/10 décisions actées).
2. ✅ **Specs agents** — Matching (03), Brief-Parser (04), Mission Copilot (05).
3. ✅ **Data model** (06), **API spec** (07), **ADR stack** (08), **JSON-Schema** (`schemas/skill.schema.json`).
4. ✅ **5 skills natifs** — `skills/native/` : audit-ux-express, executive-summary-generator, meeting-notes-to-actions, client-deck-builder, technical-spec-writer.
5. ✅ **Backend Python** — `backend/` : FastAPI + registre skills + 3 agents (Brief-Parser, Matching, Mission Copilot) + CLI (`symbiose demo`, `symbiose serve`, `symbiose skills list/validate`).
6. ✅ **Frontend minimal** — Jinja + HTMX + Tailwind CDN : landing, onboarding PME, page mission, page live (SSE Copilot), registre skills.
7. ✅ **12 tests unitaires** verts couvrant validation schema, registre, Brief-Parser, Matching Agent.

### Ce qui tourne déjà

```bash
make install && make demo-run          # démo bout-en-bout en CLI
make serve                             # FastAPI sur http://127.0.0.1:8000
make test                              # 12/12
```

### Prochains chantiers (post-squelette)

1. **Persistence** — migrer de l'in-memory vers SQLite (schéma prêt dans `docs/tech/06-data-model.md`).
2. **Auth** — sessions cookies + argon2id (ADR-05).
3. **Adapters externes** — implémenter `claude-skill-adapter`, `mcp-adapter`, `github-adapter`.
4. **LLM mode live** — fixtures enregistrées pour tests + chaîne Anthropic testée en CI.
5. **Onboarding talent** (le MVP ne couvre que l'onboarding PME + proposition mission).
6. **Chiffrage KPIs** (tableau §Indicateurs ci-dessus).
7. **Pitch investisseurs** — `docs/09-pitch-investisseurs.md`.
