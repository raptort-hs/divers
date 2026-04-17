# 08 — Environnement prestataire (cœur produit Symbiose)

**Statut : v1 — premier jet à itérer avec l'utilisateur.**
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

Quand un prestataire accepte une mission, **Symbiose constitue automatiquement son environnement de travail augmenté** :

- 🎯 **Adapté à la mission** : la plateforme lit le brief, les livrables, l'échéance, le secteur.
- 🧠 **Complémentaire au profil** : Symbiose analyse les compétences déclarées + historique + valeurs du prestataire, identifie les **gaps** par rapport à la mission, et configure une IA qui **comble exactement ce qui lui manque**.
- 🧰 **Avec les bons outils** : skills IA spécialisés, templates, documentation, intégrations (code, design, doc, recherche...) selon le domaine.
- 📋 **Avec un plan d'action auto-généré** : découpage de la mission en étapes, jalons, checklists, livrables intermédiaires.
- 🪴 **Qui évolue** : à mesure que la mission avance, l'environnement s'ajuste (nouveaux skills débloqués, plan mis à jour).

**En une phrase** : *« Quand tu ouvres une mission Symbiose, tu ouvres un cockpit déjà configuré pour te rendre meilleur sur cette mission précise. »*

## 3. Composants de l'environnement

### 3.1 Le copilote IA mission-aware

IA conversationnelle spécialisée, avec :
- **Contexte mission pré-chargé** : brief, client, livrables, contraintes.
- **Contexte profil pré-chargé** : ton style, tes forces, tes faiblesses (pas visible au talent, mais guide les suggestions).
- **Mémoire long terme** sur cette mission (tout ce qui a été dit, fait, décidé).
- **Persona IA ajustée** : ton formel / informel, rôle (pair / mentor / exécutant) selon le talent.

### 3.2 Le skill set activé

Skills (outils / prompts / workflows) activés uniquement si pertinents :
- **Skills de domaine** : dev (review code, debug, génération tests), design (wireframes, user flows, conversions Figma), marketing (SEO, personas, campagnes), juridique (rédaction contrat, veille réglementaire)...
- **Skills transverses** : rédaction client, estimation chiffrage, planning, synthèse réunion, génération livrables.
- **Skills complémentaires** : activés spécifiquement pour combler un gap détecté (ex : Léa junior UX → skill « expertise architecture information » activé ; Marc senior dev → pas besoin).

### 3.3 L'espace de travail (workspace)

- **Canvas mission** : timeline visuelle des jalons + livrables + statut.
- **Bibliothèque** : documents du brief, références, livrables en cours, historique messages client.
- **Chat client intégré** (dans l'espace mission, partagé avec le client).
- **Zone privée prestataire** : notes, brouillons, expérimentations (non partagées avec le client).
- **Intégrations au MVP** : upload fichiers + aperçu + versioning basique. Phase 2 : GitHub, Figma, Notion, Gmail.

### 3.4 Le plan d'action auto-généré

- **Dès acceptation de la mission** : Symbiose génère un plan (3-7 étapes typiques) à partir du brief.
- **Affiché, modifiable** : le prestataire peut réordonner, ajouter, supprimer.
- **Approbation client possible** (1 clic) : plan partageable au client pour validation.
- **Checklists par étape** : tâches concrètes (ex : étape 2 → « identifier 3 références », « esquisser 2 concepts », « demander feedback client »).
- **Ajustement dynamique** : si une étape dérape (délai), le copilote propose un ré-alignement.

## 4. Processus de constitution (flow)

```
[Acceptation de la mission]
        │
        ▼
[Lecture brief + livrables + budget + deadline]
        │
        ▼
[Analyse profil talent : compétences, niveau, valeurs, historique]
        │
        ▼
[Calcul gap compétences requises ↔ compétences talent]
        │
        ▼
[Sélection des skills IA à activer]
        ├── skills domaine (dev/design/marketing...)
        ├── skills transverses (rédaction/chiffrage...)
        └── skills complémentaires (ce qui comble le gap)
        │
        ▼
[Génération du plan d'action à partir du brief]
        │
        ▼
[Instanciation du workspace mission]
        ├── canvas + timeline
        ├── bibliothèque pré-remplie
        └── copilote chargé avec contexte
        │
        ▼
[Prestataire entre dans son environnement : tout est prêt]
```

**Durée cible** : < 30 secondes entre l'acceptation et l'accès à l'environnement prêt.

## 5. Exemples concrets (par persona × mission)

### Ex. 1 — Léa (T1, junior UX) sur une mission refonte site PME

- **Gap détecté** : peu d'expérience en audit UX quanti.
- **Skills activés** : « Audit UX express », « Atelier persona », « Wireframing », **« Analyse data Google Analytics » (complémentaire)**.
- **Plan auto** : 1) Découverte & audit, 2) Personas & scénarios, 3) Wireframes, 4) Prototype Figma, 5) Livraison + guide dev.
- **Copilote** : rôle pair-mentor, ton pédagogique, suggère des questions à poser au client pour bien cadrer.

### Ex. 2 — Marc (T2, senior dev full-stack) sur une mission intégration API

- **Gap détecté** : aucun (profil très complet).
- **Skills activés** : « Review code », « Génération tests », « Doc technique », **pas de skills complémentaires**.
- **Plan auto** : 1) Audit archi actuelle, 2) Spec intégration, 3) Implémentation, 4) Tests, 5) Livraison doc.
- **Copilote** : rôle exécutant (pas pédagogique), répond uniquement quand sollicité, générations concises.

### Ex. 3 — Amine (T3, étudiant, mission landing page)

- **Gap détecté** : cadrage client + livraison pro.
- **Skills activés** : « HTML/CSS/JS », « Copywriting landing », **« Cadrage besoin client » (complémentaire)**, **« Livraison & passation » (complémentaire)**.
- **Plan auto** : 1) Cadrage avec client, 2) Wireframe, 3) Design + dev, 4) Intégration contenus, 5) Livraison + passation.
- **Copilote** : rôle mentor fort, checkpoints pédagogiques à chaque étape.

## 6. Principes de conception

1. **Profile-first, mission-second** : on adapte l'IA au talent, pas l'inverse. Le talent reste au centre.
2. **Complémentarité, pas substitution** : l'IA remplit les gaps, elle ne fait pas le travail à la place.
3. **Transparence** : le talent voit **quels skills** sont activés et pourquoi. Il peut en désactiver.
4. **Évolutif** : les skills utilisés / ignorés nourrissent l'apprentissage — la plateforme apprend pour les missions suivantes.
5. **Ownership** : le livrable reste celui du talent. L'IA laisse toujours la décision finale.
6. **Modulaire** : un skill est un bloc autonome (comme un plug-in) — permet d'en ajouter sans refonte.
7. **Mesurable** : chaque skill mesure sa contribution (temps gagné, itérations réduites, NPS talent).

## 7. Pile technique pressentie (à formaliser en `docs/tech/`)

- **Moteur IA** : LLM généraliste (Claude / GPT / Mistral) orchestré via un layer d'agents.
- **Skills = agents spécialisés** (ou « prompts packagés »), chacun avec son prompt système, ses outils, sa mémoire.
- **Profil talent vectorisé** : embeddings compétences + historique pour match rapide avec les skills requis.
- **Mission parsée** : extraction structurée du brief (domaine, livrables, deadline, budget, tags) pour alimenter le matching skills + plan auto.
- **Workspace** : frontend SPA (probablement React/Next), espace temps réel (WebSockets) pour chat & collab.
- **Sécurité & confidentialité** : isolation stricte par mission, chiffrement données client, options « pas d'entraînement sur mes données ».

## 8. Plan par phases

### Phase MVP — L'essentiel du cockpit

- Analyse brief → plan d'action auto-généré (3-5 skills domaine de base).
- Copilote IA mission-aware (contexte brief + profil basique).
- Workspace minimal : canvas timeline + bibliothèque + chat client.
- 3-5 skills domaine lancés au départ (tech, design, marketing, rédaction, juridique — à prioriser).
- Persona IA basique (2 modes : pair vs exécutant).

### Phase 2 — La complémentarité profonde

- Détection automatique des gaps compétences.
- Skills complémentaires auto-activés.
- Persona IA ajustée finement (formel/informel, rôle adaptatif).
- Apprentissage plateforme (les usages nourrissent la sélection de skills).
- Intégrations externes (GitHub, Figma, Notion).

### Phase 3 — L'écosystème

- Marketplace interne de skills (créés par la communauté de talents seniors + validés Symbiose).
- Skills spécialisés sectoriels (santé, legal tech, green tech...).
- Benchmarks de performance par skill (le talent voit l'impact réel sur ses missions).
- API publique skills : intégration d'outils externes.

## 9. Questions ouvertes à trancher

1. **Granularité des skills** : un skill fait une chose (ex: « génération de persona ») ou couvre un mini-workflow (ex: « kick-off mission » = brief + questions + structure) ?
2. **Choix LLM** : un LLM unique (Claude, par ex) ou multi-LLM orchestré selon la tâche (GPT pour créativité, Claude pour raisonnement, Mistral pour FR...) ?
3. **Skills créés par qui ?** : équipe Symbiose uniquement au MVP, ou ouverts aux talents seniors dès Phase 2 ? Gouvernance qualité ?
4. **Confidentialité client** : comment isoler le contexte d'une mission du reste ? Stockage, logs, opt-out entraînement — à formaliser dès MVP.
5. **Facturation IA** : consommation tokens IA incluse dans la commission 10 % ou facturée à part ? Impact sur la marge.
6. **Interface** : web uniquement au MVP, ou extension VSCode / Figma / Notion pour les talents tech/design déjà sur ces outils ?
7. **Plan d'action auto** : visible/modifiable par le client dès le début, ou seulement après approbation du talent ?
8. **Fallback** : que se passe-t-il si un skill est défectueux ou indisponible ? UX de gestion d'erreur IA.

## 10. Prochaines actions (ce chantier)

1. Prioriser les **5-10 premiers skills** à construire pour le MVP (tableau skill × domaine × persona).
2. Spécifier **un skill pilote de bout en bout** (input, prompt système, outils, output attendu, mesures).
3. Maquetter le **flow de constitution** (wireframes : écran d'acceptation mission → loader → cockpit prêt).
4. Décider la **stack LLM** et le coût cible par mission.
5. Itérer le plan d'action auto sur 3-5 missions fictives pour valider le format.
