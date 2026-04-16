# Contrat mémoire — projet Symbiose

Ce fichier est la **règle du jeu** pour toute session de travail sur ce repo. Il garantit que la mémoire du projet persiste dans les `.md` et reste à jour en permanence.

## 1. Avant toute action (début de session)

1. Lire `docs/06-journal.md` — dernières entrées (au moins les 5 dernières).
2. Lire `docs/05-roadmap.md` — phase en cours + prochaine action identifiée.
3. Lire les docs thématiques concernées par la demande de l'utilisateur.

## 2. Pendant la session

- Dès qu'une **décision** est prise, ou qu'une **info produit** émerge : mettre à jour le `.md` thématique concerné **immédiatement**, pas à la fin.
- Toute reformulation majeure du pitch, de la vision, du modèle économique : tracer dans `06-journal.md` avec la version précédente résumée.
- Si l'utilisateur change d'avis : documenter **le changement** dans le journal (pas juste écraser).

## 3. Fin de session (obligatoire)

Ajouter une entrée dans `docs/06-journal.md` au format :

```
## YYYY-MM-DD — Titre court

**Fait**
- Bullet 1
- Bullet 2

**Décisions prises**
- Décision 1 (si applicable)

**Reste à faire**
- Bullet

**Prochaine action**
Décrire en 1 ligne la toute prochaine action.
```

## 4. Fichiers et langues

- Docs produit / vision / business / journal / personas → **français**.
- Docs techniques (`docs/tech/`, futurs schémas, API, architecture) → **anglais**.
- `README.md` et `CLAUDE.md` → français.

## 5. Git

- Branche de travail : `claude/review-shared-link-wubTi` (sauf indication contraire).
- Un commit par étape cohérente (pas de commit fourre-tout).
- Message de commit court, descriptif, en français : `docs: ajoute personas v1`, `update: ajuste roadmap phase 1`, etc.
- Toujours pousser avec `-u origin <branche>`.
- Ne jamais créer de PR sans demande explicite.

## 6. Ce qu'il ne faut PAS faire

- Reformuler ou "lisser" le pitch sans autorisation explicite.
- Prendre des décisions produit à la place de l'utilisateur — proposer, oui ; décider, non.
- Créer des `.md` hors de la structure validée sans en parler d'abord.
- Marquer une étape comme terminée si le `.md` thématique + journal n'ont pas été mis à jour.

## 7. Structure de référence

```
/
├── README.md
├── CLAUDE.md
└── docs/
    ├── 01-vision.md
    ├── 02-proposition-valeur.md
    ├── 03-produit.md
    ├── 04-business-model.md
    ├── 05-roadmap.md
    ├── 06-journal.md
    ├── 07-personas.md
    ├── 08-pitch-investisseurs.md   (à venir)
    └── tech/                        (à venir, en anglais)
```
