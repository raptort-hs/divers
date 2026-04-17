# 08 — Environnement prestataire (cœur produit Symbiose)

**Statut : v2 — orientation stratégique écosystème ouvert (2026-04-16).**
**Priorité : MAJEURE.** C'est ici que se joue la promesse « travail augmenté par IA » et la différenciation vs Malt / Upwork / Fiverr.

---

## 1. Le problème résolu

Un freelance qui prend une mission aujourd'hui démarre **toujours de zéro** :
- Il ré-assemble ses outils à chaque mission (IDE, notion, figma, IA du moment, prompts...).
- Il doit structurer seul sa méthode d'approche (brief → plan → exécution).
- Il identifie seul ses **zones faibles** par rapport à la mission.
- Il perd du temps à caler, aligner, documenter.

**Conséquence** : temps perdu, qualité inégale, sentiment d'isolement, plafond de verre sur la complexité des missions qu'il peut prendre.

## 2. La promesse Symbiose

Quand un prestataire accepte une mission, **Symbiose constitue automatiquement un environnement de travail augmenté à partir d'un écosystème ouvert de skills** :

- 🎯 **Adapté à la mission** : la plateforme lit le brief, les livrables, l'échéance, le secteur.
- 🧠 **Complémentaire au profil** : Symbiose analyse les compétences + historique + valeurs du prestataire, identifie les **gaps** par rapport à la mission, et **compose une boîte à outils qui comble exactement ce qui lui manque**.
- 🧰 **Puisée dans un écosystème ouvert** : skills créés par Symbiose, par les talents eux-mêmes, ou **importés depuis internet** (sources externes, open source, communautés).
- 📋 **Avec un plan d'action auto-généré** : découpage de la mission en étapes, jalons, checklists.
- 🪴 **Qui évolue** : à mesure que la mission avance, skills et plan s'ajustent.

**En une phrase** : *« Chaque mission ouvre un cockpit composé spécifiquement pour toi, à partir de tout ce que l'écosystème mondial a de meilleur. »*

## 3. La force différenciante : un agent spécialisé fait le matching

C'est **LE cœur technique et stratégique** de Symbiose.
**Décision architecturale (2026-04-16)** : le matching n'est pas un algorithme classique (embeddings + règles + re-ranking). C'est un **agent IA spécialisé** — autonome, capable de raisonner sur le contexte, d'utiliser des outils (lecture registry skills, profil, mission), et de composer dynamiquement l'environnement.

```
   Profil talent           Brief mission          Registry skills
 (profil vectorisé +      (structuré par         (natifs + communautaires
  historique narré)        un agent parseur)       + externes importés)
        \                       |                        /
         \                      |                       /
          \                     ▼                      /
           \           ┌────────────────────┐         /
            ──────────▶│  Matching Agent    │◀───────
                       │  (spécialisé,      │
                       │   outillé, avec    │
                       │   mémoire)         │
                       └──────────┬─────────┘
                                  ▼
                  Environnement composé :
                  - Skills activés (forces + compléments)
                  - Plan d'action généré
                  - Persona copilote adaptée
                  - Justifications transparentes au talent
```

**Pourquoi un agent plutôt qu'un algo** :
- **Contexte riche** : un agent peut intégrer des signaux faibles (valeurs du talent, historique de feedback client, saisonnalité) qu'un scoring fixe ne capture pas.
- **Raisonnement** : il peut expliquer pourquoi il active tel skill — transparence.
- **Adaptabilité** : il s'améliore avec de nouveaux skills / nouveaux domaines sans réécrire de règles.
- **Extensibilité** : l'agent peut solliciter d'autres agents (ex : agent « Analyse de brief » si le brief est ambigu).

**La plateforme entière est pensée AI-native, agent-native** — Symbiose = **orchestration d'agents spécialisés** (matching, parsing brief, génération plan, copilote de mission, import skill, review sécurité...), pas une appli web qui appelle ponctuellement de l'IA.

## 4. Composants de l'environnement

### 4.1 Le copilote IA mission-aware

IA conversationnelle spécialisée, avec :
- **Contexte mission pré-chargé** : brief, client, livrables, contraintes.
- **Contexte profil pré-chargé** : forces, faiblesses (invisibles au talent mais guident les suggestions).
- **Mémoire long terme** sur cette mission.
- **Persona IA ajustée** : pair / mentor / exécutant selon le talent.

### 4.2 Le skill set activé (composé depuis l'écosystème)

La plateforme compose une sélection, jamais un catalogue fermé :
- **Skills forces** : confortent ce que le talent fait déjà bien (accélération).
- **Skills complémentaires** : comblent les gaps identifiés par le matching.
- **Skills transverses** : rédaction client, chiffrage, planning, synthèse.

Sources des skills (voir section 5) :
- **Skills natifs Symbiose** (équipe).
- **Skills communautaires** (créés par d'autres talents de la plateforme).
- **Skills externes** (importés depuis internet : Claude Skills, MCP, GitHub, marketplaces).

### 4.3 L'espace de travail (workspace)

- Canvas mission (timeline + livrables + statut).
- Bibliothèque (brief, références, livrables, historique).
- Chat client intégré.
- Zone privée prestataire (notes, brouillons).
- MVP : upload + preview + versioning basique. Phase 2 : GitHub / Figma / Notion / Gmail.

### 4.4 Le plan d'action auto-généré

- Généré dès acceptation mission (3-7 étapes).
- Modifiable par le prestataire.
- Partageable au client (1 clic).
- Checklists par étape.
- Ajusté dynamiquement (délai, changement scope).

## 5. L'écosystème skills — ouverture et gouvernance

### 5.1 Un skill : définition

Un **skill** est une unité autonome, packagée, réutilisable. Format standard (à formaliser en `docs/tech/`) :

```yaml
id: audit-ux-express
name: Audit UX express
version: 1.2.0
author: symbiose | talent_id | external
domains: [design, ux]
level: [junior, mid]
required_tools: [web_browser, figma_reader]
input_schema: { mission_brief, target_audience, current_site_url }
output_schema: { audit_report, priorities, quick_wins }
prompt_system: "Tu es un expert UX senior..."
metrics: { time_saved_minutes, satisfaction_score }
cost_estimate_tokens: 8000
```

### 5.2 Sources

**Trois sources cohabitent** :

1. **Skills natifs Symbiose** : créés et maintenus par l'équipe, qualité garantie, gratuits pour les talents.
2. **Skills communautaires** : créés par les talents de la plateforme. Validation (voir 5.3), versioning, notation.
3. **Skills externes importés** : depuis GitHub, Claude Skills, MCP servers, ou toute source publique respectant le format Symbiose (ou un adaptateur).

### 5.3 Création & partage

- **Éditeur de skill intégré** : un talent senior peut créer un skill en décrivant un workflow qu'il maîtrise. Assistant IA qui l'aide à formaliser le prompt, les inputs/outputs, les cas d'usage.
- **Partage** : le créateur publie sur la marketplace Symbiose.
- **Monétisation** (à trancher) : les skills communautaires peuvent rapporter **des tokens** au créateur à chaque usage réussi. Aligne incentives qualité.
- **Versioning** : chaque skill a ses versions, notes de mise à jour, auteur responsable.

### 5.4 Import depuis internet

- **Formats natifs supportés** (cible phase 2) : Claude Skills, MCP (Model Context Protocol), npm-like packages IA.
- **Adaptateurs** : pour les formats non standards, Symbiose propose un wrapper (config YAML + mapping I/O).
- **Registry** : catalogue central indexé par domaine, niveau, popularité.
- **Safety** : skills externes sandboxés, review automatique du prompt (détection prompt injection, PII leakage, biais).

### 5.5 Gouvernance qualité

- **Notation des skills** : par les talents qui les utilisent (efficacité, pertinence).
- **Monitoring runtime** : taux d'échec, coût moyen, satisfaction (captés automatiquement).
- **Badges qualité** : « Certifié Symbiose », « Communauté +100 usages », « Expérimental ».
- **Retraits** : skills défaillants automatiquement dépréciés, remplacés dans les missions en cours.

## 6. Processus de constitution (flow)

```
[Acceptation de la mission]
        │
        ▼
[Parse mission : brief + livrables + budget + deadline + domaine]
        │
        ▼
[Analyse profil talent : compétences, niveau, valeurs, historique]
        │
        ▼
[Calcul gap compétences requises ↔ compétences talent]
        │
        ▼
[Requête au registry skills : scoring + ranking]
        ├── skills natifs Symbiose
        ├── skills communautaires
        └── skills externes importés
        │
        ▼
[Composition de l'environnement]
        ├── sélection top-N skills (avec skills compléments prioritaires)
        ├── génération plan d'action
        └── instanciation workspace
        │
        ▼
[Prestataire entre : environnement prêt, skills activés, plan affiché]
```

**Durée cible** : < 30 s entre acceptation et accès.

## 7. Exemples concrets (par persona × mission)

### Ex. 1 — Léa (T1, junior UX) sur une refonte site PME

- **Gap détecté** : peu d'expérience en audit UX quanti.
- **Skills activés** :
  - Natif Symbiose : `audit-ux-express`, `atelier-persona`, `wireframing-basics`.
  - **Communautaire** (d'un autre UX senior) : `workshop-discovery-pme`.
  - **Externe** importé : `google-analytics-reader` (MCP, compensateur de gap).
- **Plan auto** : Découverte → Personas → Wireframes → Prototype → Livraison.
- **Copilote** : rôle pair-mentor, ton pédagogique.

### Ex. 2 — Marc (T2, senior dev) sur une intégration API

- **Gap détecté** : aucun.
- **Skills activés** :
  - Natifs : `code-review`, `test-generation`, `tech-doc`.
  - Aucun compensateur (profil complet).
  - **Externe** : MCP GitHub pour accès repo.
- **Plan auto** : Audit → Spec → Implémentation → Tests → Livraison.
- **Copilote** : rôle exécutant.

### Ex. 3 — Amine (T3, étudiant, mission landing page)

- **Gap détecté** : cadrage client + livraison pro.
- **Skills activés** :
  - Natifs : `html-css-js`, `copywriting-landing`.
  - **Communautaires** : `cadrage-besoin-client-pme` (gros compensateur), `passation-livraison-pro`.
- **Plan auto** : Cadrage → Wireframe → Design+dev → Intégration → Livraison.
- **Copilote** : rôle mentor fort.

## 8. Principes de conception

1. **AI-native, agent-native** : la plateforme est **une orchestration d'agents spécialisés**, pas une app qui appelle ponctuellement une IA. Chaque fonction centrale (matching, parsing brief, plan d'action, review, copilote) est un agent.
2. **Écosystème ouvert par défaut** : tout skill doit pouvoir être créé, partagé, importé. Format standard documenté.
3. **Profile-first, mission-second** : on adapte l'écosystème au talent, pas l'inverse.
4. **Complémentarité, pas substitution** : l'IA comble les gaps, le talent reste aux commandes.
5. **Transparence** : le talent voit quels skills sont activés, **pourquoi l'agent les a choisis**, et peut en désactiver/remplacer.
6. **Gouvernance par l'usage** : la qualité émerge de la notation + monitoring runtime, pas d'un comité fermé.
7. **Ownership** : le livrable reste celui du talent.
8. **Modulaire & versionné** : skills atomiques, versionnés, remplaçables sans casser la mission.
9. **Incentivisé** : créer un skill utilisé par d'autres rapporte des tokens au créateur.
10. **Safe by default** : sandboxing, review prompt, no-data-leak, no-training-on-client-data.

## 9. Pile technique pressentie (formalisée en `docs/tech/`)

- **Plateforme = orchestration d'agents spécialisés** (cf. `docs/tech/01-agent-architecture.md`).
- **Agents clés** (MVP) : Brief-Parser Agent, Matching Agent, Plan-Builder Agent, Mission Copilot Agent, Skill-Importer Agent, Safety-Review Agent.
- **Moteur IA** : Claude (Anthropic) en priorité (raisonnement + tool use + longs contextes). Multi-LLM possible en Phase 2 si coût/usage le justifie.
- **Skills** : manifest YAML + prompt système + outils MCP + mémoire. Chaque skill peut être invoqué par n'importe quel agent.
- **Registry skills** : base de données + index vectoriel (pg + pgvector ou équivalent) pour la recherche sémantique rapide par le Matching Agent.
- **Workspace** : SPA React/Next, realtime via WebSockets, streaming UI pour visualiser le raisonnement des agents.
- **Sécurité** : isolation par mission, chiffrement, opt-out entraînement, sandboxing des skills externes.

## 10. Plan par phases

### Phase MVP

- **Moteur matching** basique : profil + mission → sélection parmi 10-20 skills natifs.
- **Format standard skill** défini et documenté.
- **5-10 skills natifs Symbiose** couvrant les domaines prioritaires PME (tech, design, marketing, copywriting, juridique basique).
- **Copilote IA mission-aware** (contexte brief + profil basique).
- **Workspace minimal**.
- **Plan d'action auto** (3-5 étapes).
- **Pas encore** : création par les talents, import externe, marketplace skills.

### Phase 2

- **Éditeur de skill intégré** : les talents seniors peuvent créer et partager.
- **Marketplace skills** : visible dans la plateforme, notation, versioning.
- **Import MCP / Claude Skills** : adaptateurs pour sources externes.
- **Matching avancé** : détection fine des gaps, recommandation de compensateurs.
- **Monétisation créateurs** : tokens sur usages réussis.

### Phase 3

- **Gouvernance communautaire** : comité de qualité, modération communautaire.
- **Skills sectoriels** (santé, legal tech, green tech).
- **API publique skills** : outils externes consomment l'écosystème.
- **Apprentissage plateforme** : le matching s'améliore continuellement à partir des usages.

## 11. Questions ouvertes à trancher

1. **Format standard skill** : adopter le format Claude Skills ? MCP ? Créer un format Symbiose compatible avec les deux via adaptateur ?
2. **Monétisation créateurs** : tokens uniquement, ou % revenus de la commission Symbiose ? Barème ?
3. **Granularité skill** : atomique (1 skill = 1 tâche) ou composé (1 skill = mini-workflow) ? Probablement les deux, avec composition possible.
4. **Choix LLM** : mono-LLM (Claude) ou multi-LLM orchestré ? Estimation coût par mission.
5. **Confidentialité client** : comment isoler strictement le contexte mission du reste de la plateforme ? Opt-out entraînement dès MVP.
6. **Sécurité skills externes** : review manuelle au MVP, automatisée en phase 2 ?
7. **Facturation IA** : inclus dans la commission 10 % ou facturé à part au client / au talent ?
8. **Interface** : web only au MVP, extensions VSCode / Figma / Notion en phase 2 ?
9. **Qui décide quels skills sont activés** : 100 % plateforme (magique) ? Ou proposition + acceptation talent (transparence) ? Hybride ?
10. **Skill comme contenu vs code** : un skill est-il juste un prompt + manifest (léger), ou peut-il exécuter du code (plus puissant mais plus risqué) ?

## 12. Prochaines actions (ce chantier)

1. **Formaliser le format standard skill** (manifest, I/O, sécurité) — proposer v1 technique en anglais dans `docs/tech/02-skill-format.md`.
2. **Spécifier le moteur de matching** : inputs, sorties, règles, scoring — `docs/tech/03-matching-engine.md`.
3. **Prioriser les 5-10 skills natifs MVP** : tableau par domaine × persona × priorité.
4. **Spécifier un skill pilote** bout-en-bout (candidat : `cadrage-besoin-client-pme` ou `audit-ux-express`).
5. **Décider la stack LLM** + estimation coût / mission.
6. **Trancher les 10 questions ouvertes** ci-dessus.
