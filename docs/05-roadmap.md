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

## Prochaine action

**Orientation architecturale v3 (2026-04-16) : Symbiose est AI-native et agent-native.**
Le matching profil × mission × skills est opéré par un **agent spécialisé** (Matching Agent), pas par un algorithme classique. La plateforme est une orchestration d'agents spécialisés (Brief-Parser, Matching, Plan-Builder, Mission Copilot, Skill-Importer, Safety-Review).

Doc `docs/tech/01-agent-architecture.md` créé (EN) avec :
- Catalogue des 6 agents MVP.
- Deep-dive sur le Matching Agent (inputs, tools, output contract, system prompt sketch, metrics).
- Proposition Claude Agent SDK comme orchestrateur.
- 8 questions ouvertes technique.

Doc `08-environnement-prestataire.md` mise à jour (§3, §8, §9) pour refléter l'approche agent-native.

Prochains sous-chantiers prioritaires :
1. Valider le choix Claude Agent SDK vs alternatives.
2. **Skill manifest v1** → `docs/tech/02-skill-format.md`.
3. **Matching Agent spec complète** → `docs/tech/03-matching-agent.md`.
4. Prototype end-to-end thin slice (1 skill + 3 agents) pour valider la faisabilité.
5. Prioriser les 5-10 skills natifs MVP.

Ensuite : onboarding talent, KPIs MVP, architecture globale.
