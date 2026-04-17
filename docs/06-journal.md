# 06 — Journal

Historique daté de toutes les avancées, décisions, changements d'orientation.
Les entrées les plus récentes en haut.

---

## 2026-04-16 — Orientation AI-native, agent-native : Matching Agent

**Fait**
- Décision architecturale majeure validée : **Symbiose est AI-native et agent-native**. Le matching est fait par un **agent spécialisé** (Matching Agent), pas un algorithme classique (embeddings + règles).
- Mise à jour `docs/08-environnement-prestataire.md` :
  - §3 (différenciation) réécrit autour du Matching Agent : raisonnement contextuel, justifications transparentes, sollicitation d'autres agents, extensibilité.
  - §8 principes enrichis : ajout du principe n°1 « AI-native, agent-native ».
  - §9 pile technique alignée : plateforme = orchestration d'agents spécialisés.
- Création de `docs/tech/` (sous-dossier technique en anglais) et première doc `01-agent-architecture.md` :
  - Philosophie agent-native.
  - Catalogue des 6 agents MVP (Brief-Parser, Matching, Plan-Builder, Mission Copilot, Skill-Importer, Safety-Review).
  - Deep-dive Matching Agent : inputs, tools exposés, output contract JSON, system prompt esquissé, 6 métriques.
  - Proposition orchestration = **Claude Agent SDK** (alternative LangGraph / custom).
  - Data flow de constitution d'une mission.
  - 8 questions ouvertes techniques.
- Mise à jour `README.md`, `CLAUDE.md` (arborescence avec `docs/tech/`), roadmap.

**Décisions prises**
- Plateforme = **orchestration d'agents spécialisés** (pas une app avec de l'IA ponctuelle).
- Le matching n'est pas un algo : c'est un **agent autonome** outillé.
- Reco stack orchestration : **Claude Agent SDK** (à valider).

**Reste à faire**
- Validation du choix Claude Agent SDK.
- Skill manifest format v1 (`docs/tech/02-skill-format.md`).
- Matching Agent spec complète (`docs/tech/03-matching-agent.md`).
- Prototype thin slice (1 skill + 3 agents).
- Trancher les 8 questions ouvertes tech + les 10 de doc 08.

**Prochaine action**
Demander à l'utilisateur quel sous-chantier attaquer : validation Claude Agent SDK, skill manifest, ou spec Matching Agent complète.

---

## 2026-04-16 — Environnement prestataire v2 : écosystème ouvert de skills

**Fait**
- Révision majeure de `docs/08-environnement-prestataire.md` (v1 → v2) suite à l'orientation stratégique utilisateur : **écosystème ouvert de skills**.
- Nouvelles sections clés :
  - **§3 Matching triadique** (profil × mission × skills) posé comme cœur technique/stratégique.
  - **§5 Écosystème skills** : définition format standard (YAML manifest), 3 sources (natifs / communautaires / externes), création/partage, import depuis internet (Claude Skills, MCP, GitHub), gouvernance par l'usage, monétisation créateurs en tokens.
  - Principes enrichis : écosystème ouvert par défaut, gouvernance par usage, incentivisé, safe by default.
  - Plan par phases retravaillé : format standard + moteur matching dès MVP ; éditeur skills + marketplace + import MCP/Claude Skills en Phase 2 ; API publique + skills sectoriels en Phase 3.
- 10 questions ouvertes (vs 8 précédemment), dont nouvelles : format standard à adopter, monétisation créateurs, sécurité skills externes, skill-as-code vs prompt, qui décide des skills activés.
- Mise à jour `05-roadmap.md` avec les 5 sous-chantiers prioritaires.

**Décisions prises**
- **Orientation stratégique** : Symbiose ne maintient pas un catalogue fermé de skills. C'est un écosystème ouvert composé à la volée pour chaque mission.
- **Différenciateur** = qualité du matching triadique, pas la taille du catalogue.
- **Monétisation** : les créateurs de skills communautaires gagnent des tokens à chaque usage réussi (aligne incentives qualité).

**Reste à faire**
- Formaliser le format standard skill (doc technique en anglais).
- Spécifier le moteur de matching.
- Prioriser les skills natifs MVP (5-10).
- Spécifier un skill pilote bout-en-bout.
- Trancher les 10 questions ouvertes.

**Prochaine action**
Demander à l'utilisateur par où on attaque : formaliser le format skill, spécifier le moteur de matching, prioriser les skills MVP, ou trancher quelques questions ouvertes en amont.

---

## 2026-04-16 — Environnement prestataire (cœur produit) — v1

**Fait**
- 5 questions ouvertes de l'onboarding PME tranchées : pas de captcha, pas de modération, copilote FR+EN, Stripe Connect (sans intégration immédiate), anti-bypass en Phase 2.
- Création de `docs/08-environnement-prestataire.md` : doc majeure couvrant le cœur produit Symbiose.
  - Problème résolu (freelance part de zéro à chaque mission).
  - Promesse : environnement auto-constitué, adapté mission + complémentaire au profil.
  - 4 composants : copilote IA mission-aware, skill set activé, workspace, plan d'action auto.
  - Processus de constitution (flow schématisé).
  - 3 exemples concrets par persona (Léa junior UX, Marc senior dev, Amine étudiant).
  - 7 principes de conception (profile-first, complémentarité, transparence, évolutif, ownership, modulaire, mesurable).
  - Pile technique pressentie (LLM + agents skills + vectorisation profil + workspace SPA).
  - Plan par phases (MVP cockpit essentiel → P2 complémentarité profonde → P3 marketplace skills).
  - 8 questions ouvertes (granularité skills, LLM mono/multi, gouvernance, confidentialité, facturation IA, interface, plan d'action partagé client, fallback).
  - 5 prochaines actions opérationnelles.
- Renumérotation : pitch investisseurs passe de 08 à 09 (placeholder seulement, rien d'écrit).
- Mise à jour README, CLAUDE.md, roadmap avec ce nouveau chantier prioritaire.

**Décisions prises**
- Ce chantier est désigné **majeur** par l'utilisateur : c'est LE cœur produit de Symbiose.
- Structure : un doc dédié numéroté 08 (plutôt que dilué dans module 4 ou un flow).
- Les 5 réponses onboarding PME : captcha inutile au MVP, pas de modération, copilote FR+EN, Stripe Connect validé mais intégré plus tard, anti-bypass Phase 2.

**Reste à faire**
- Trancher les 8 questions ouvertes de `08-environnement-prestataire.md`.
- Prioriser les 5-10 premiers skills MVP.
- Spécifier un skill pilote de bout en bout.
- Décider la stack LLM.
- Itérer le plan auto sur missions fictives.

**Prochaine action**
Demander à l'utilisateur sur quel axe attaquer en premier (questions ouvertes, priorisation skills, skill pilote, ou choix LLM).

---

## 2026-04-16 — Onboarding PME v1 (flow détaillé)

**Fait**
- Création du sous-dossier `docs/flows/` pour accueillir les parcours détaillés.
- Rédaction `docs/flows/onboarding-pme.md` : tunnel step-by-step (Landing → Signup → Qualif besoin → Profil express → Matching → Espace mission → KYC).
- Principes directeurs : friction minimale jusqu'au matching, copilote IA à chaque étape de rédaction, progressive disclosure, transparence commission 10 %.
- Cible d'activation : **time-to-matching < 15 min**.
- Vue données minimale (User, Company, Need, MatchingProposal, MissionSpace) — à formaliser proprement en `docs/tech/` plus tard.
- 5 questions ouvertes identifiées : captcha, modération PME, langue copilote, prestataire paiement, stratégie anti-bypass.
- Mise à jour `README.md` et `CLAUDE.md` : ajout de l'arborescence `flows/`.

**Décisions prises**
- Architecture docs : dossier `flows/` pour chaque parcours métier (plutôt que d'alourdir les docs numérotées).
- Flow onboarding PME : 6 étapes, ~15 min total, KYC repoussé au moment du 1er paiement (pas bloquant à l'onboarding).

**Reste à faire**
- Validation du flow PME + trancher ses 5 questions ouvertes.
- Définir les autres flows : onboarding talent, exécution mission, feedback.
- Chiffrer KPIs MVP.
- Attaquer l'architecture technique.

**Prochaine action**
Recueillir le feedback utilisateur sur `docs/flows/onboarding-pme.md` + trancher les 5 questions ouvertes.

---

## 2026-04-16 — Scope modules MVP validé (6/6)

**Fait**
- Validation du scope modules MVP par l'utilisateur : les 6 modules sont actés au MVP (incluant module 6 Tokens en version minimal off-chain).
- Tableau scope marqué « validé » dans `05-roadmap.md`.

**Décisions prises**
- Aucun module retiré du MVP. On conserve Profil, Matching, Marketplace, Espace mission+copilote, Feedback, Tokens — chacun au périmètre défini dans le tableau.

**Reste à faire**
- Tunnel onboarding PME (parcours step-by-step).
- Chiffrage indicateurs de succès MVP.
- Démarrer étape 3 : architecture technique (`docs/tech/01-architecture.md`, anglais).

**Prochaine action**
Demander à l'utilisateur sur quoi enchaîner : onboarding PME, chiffrage KPIs, ou architecture technique.

---

## 2026-04-16 — Cadrage MVP verrouillé + scope modules proposé

**Fait**
- 4 décisions tranchées verrouillant le périmètre MVP :
  - Talents MVP : **mix juniors + seniors** (T1/T2/T3 dès le lancement).
  - Missions à impact : **Phase 2** (pas au MVP).
  - Tokens : **MVP minimal** (compteur off-chain, sans gouvernance on-chain).
  - Géographie : **France seule**.
- Questions ouvertes toutes barrées dans `07-personas.md`.
- `05-roadmap.md` réécrit : Phase 0 close, Phase 1 détaillée avec tableau scope modules (6 modules mappés MVP / partiel / minimal), modules transverses listés, indicateurs de succès ébauchés.
- Phase 2 enrichie (copilote profond, gamification, missions impact, tokens on-chain, abonnements premium).

**Décisions prises**
- Scope modules MVP proposé (à valider) : modules 1-2-3 complets, module 4 partiel (copilote IA basique), module 5 partiel (évaluations sans gamification), module 6 minimal (compteur tokens).
- Modules transverses MVP : KYC, paiement escrow, facturation, contrat, dashboards.

**Reste à faire**
- Validation du tableau scope modules par l'utilisateur.
- Chiffrer les indicateurs de succès (PME cibles, GMV, NPS).
- Définir le tunnel onboarding PME.
- Attaquer ensuite l'étape 3 : architecture technique (`docs/tech/01-architecture.md`, en anglais).

**Prochaine action**
Présenter le scope modules MVP à l'utilisateur pour validation/ajustements.

---

## 2026-04-16 — Décision : PME = cible client MVP

**Fait**
- Validation de C1 (Sophie / dirigeante de PME 20-50 pers.) comme cible client prioritaire pour le MVP.
- Marquage « CIBLE MVP » dans `07-personas.md`, question 2 des questions ouvertes tranchée.
- Roadmap Phase 1 mise à jour : cible client actée, 4 questions restantes à trancher.

**Décisions prises**
- **Cible MVP = PME (C1)**. Les grand groupes (C2) et ONG (C3) restent en Phase 2+.

**Reste à faire**
- Trancher les 4 questions restantes : priorité talent, missions impact, tokens, géographie.

**Prochaine action**
Poser les 4 questions restantes à l'utilisateur pour verrouiller le périmètre MVP.

---

## 2026-04-16 — Personas & parcours v1

**Fait**
- Création de `docs/07-personas.md` : 3 personas talents (Léa junior, Marc senior, Amine étudiant) + 3 personas clients (Sophie PME, Julien grand groupe, Fatou ONG).
- Parcours type (user journey) talent + client détaillés.
- 5 questions ouvertes identifiées pour trancher avant définition MVP (priorité juniors/seniors, cible client MVP, missions impact, tokens, géographie).
- Mise à jour `05-roadmap.md` : Phase 0 presque close, prochaine action = validation personas + trancher les 5 questions.

**Décisions prises**
- Structure personas : 3 talents + 3 clients couvrant le spectre (junior/senior/étudiant × PME/grand compte/ONG).

**Reste à faire**
- Validation/amendement des personas par l'utilisateur.
- Trancher les 5 questions ouvertes → passage à l'étape 2 (MVP).

**Prochaine action**
Attendre le retour de l'utilisateur sur les personas : quels profils garder/retirer/ajouter, et réponses aux 5 questions ouvertes.

---

## 2026-04-16 — Initialisation du projet Symbiose

**Fait**
- Création de la structure documentaire : `README.md`, `CLAUDE.md`, `docs/01-vision.md` à `docs/06-journal.md`.
- Import du pitch v1 fourni par l'utilisateur, réparti dans 4 docs thématiques (vision, proposition de valeur, produit, business model).
- Squelette de roadmap avec Phase 0 (setup) cochée et Phases 1-3 à définir.
- Contrat mémoire (`CLAUDE.md`) : règles de mise à jour continue des `.md`, stratégie linguistique mixte (français produit / anglais technique), règles de commit.

**Décisions prises**
- Structure `docs/` numérotée (01 à 08+), langues mixtes FR/EN.
- Séquence de travail : Personas → Roadmap/MVP → Architecture technique → Pitch investisseurs.
- Branche de travail : `claude/review-shared-link-wubTi`.

**Reste à faire**
- Rédiger `docs/07-personas.md` (premier jet).
- Affiner Phase 1 (MVP) sur la base des personas validés.

**Prochaine action**
Créer `docs/07-personas.md` avec 4-5 personas initiaux (talents + entreprises) et un user journey par persona, à valider avec l'utilisateur.
