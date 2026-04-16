# Flow — Onboarding PME (cible MVP : C1 Sophie)

**Statut : v1 — à valider.**

Objectif produit : faire passer une dirigeante de PME de la landing à **un premier matching reçu en moins de 15 minutes**, avec une perception forte de qualité et de sécurité.

---

## Principes directeurs

1. **Friction minimale jusqu'au matching** : Sophie doit voir la valeur (3 profils qualifiés) avant qu'on lui demande quoi que ce soit d'administratif (SIRET, IBAN, etc.).
2. **Copilote IA partout** : à chaque étape où elle doit rédiger (brief, description entreprise), le copilote propose un brouillon.
3. **Transparence immédiate** : commission 10 % affichée dès la landing, RGPD clair, pas de surprise.
4. **Progressive disclosure** : on demande le strict nécessaire par étape, le reste est un nudge post-signup.
5. **Mobile-ready dès le MVP** : Sophie est souvent en déplacement.

---

## Parcours step-by-step

### Étape 0 — Landing

**Objectif** : clarifier la promesse + convertir en signup.

- Headline : *« Trouvez le freelance idéal pour votre PME, augmenté par IA. Commission 10 %. »*
- Sous-headline : *« Décrivez votre besoin, recevez 3 profils qualifiés en 15 min. »*
- CTA principal : « Déposer un besoin » → déclenche signup.
- Preuve sociale (à construire au lancement) : témoignages PME, logos, chiffres clés.

### Étape 1 — Signup (30 sec)

**Champs minimum**
- Email pro (validation format, anti-disposable).
- Mot de passe **ou** SSO Google / Microsoft.

**Pas demandés à cette étape** : nom, entreprise, téléphone.

**Transitions**
- Envoi email de vérification (lien 24h).
- Redirection immédiate vers étape 2 (pas de blocage sur vérif email).

### Étape 2 — Qualification du besoin (5-7 min)

**Questionnaire guidé, 6 questions max**, avec copilote IA en support.

1. **Domaine** (tech / design / marketing / RH / juridique / autre) — dropdown + champ libre.
2. **Description du besoin** — textarea. Le copilote IA propose un canevas si vide (« J'ai besoin de... pour... d'ici... ») et reformule le brouillon si l'utilisatrice clique « Améliorer ».
3. **Livrables attendus** — liste à cocher pré-remplie selon le domaine + champ libre.
4. **Durée / urgence** — dropdown (quelques jours / quelques semaines / plusieurs mois) + date souhaitée de démarrage.
5. **Budget** — fourchette TJM ou budget total (optionnel mais nudge si vide).
6. **Niveau souhaité** — junior / confirmé / senior / indifférent.

**Nudge valeurs** (optionnel, 1 clic) : tags « impact environnemental », « inclusion », « local », etc. Invisible au MVP si pas d'inventaire correspondant.

### Étape 3 — Profil entreprise express (1 min)

**Champs**
- Nom entreprise.
- Secteur (dropdown INSEE simplifié).
- Taille (1-10 / 11-50 / 51-250 / 250+).

**Pas demandés** : site web, adresse, logo, description (nudges post-matching).

### Étape 4 — Prévisualisation du matching (instantané)

**Écran clé de l'onboarding.**

- Affichage de **3 profils proposés** (même si base talent encore petite, on montre les plus pertinents avec transparence sur le score de matching).
- Chaque profil : photo, nom, niveau, compétences clés, TJM, note/feedback, extrait motivation généré par copilote IA.
- CTA par profil : « Contacter » (ouvre l'espace mission).
- CTA global : « Voir plus de profils » (ouvre la marketplace complète).

**Si aucun profil pertinent** : message honnête *« Notre pool grandit, on vous envoie une sélection par email sous 48h »* + option d'élargir les critères.

### Étape 5 — Création de l'espace mission (1 min)

Déclenchée au moment où Sophie clique « Contacter » sur un profil.

- Titre de la mission pré-rempli à partir du besoin.
- Invitation du talent automatique.
- Chat ouvert avec message d'accueil pré-rédigé par le copilote.
- Checklist mission initialisée (brief validé / devis / contrat / kick-off / livrable / feedback).

### Étape 6 — KYC + facturation (post-matching, avant 1er paiement)

**Uniquement demandé au moment où une mission est en passe d'être signée.**

- SIRET (validation API INSEE).
- IBAN (validation IBAN + future collecte escrow).
- Contact facturation (nom, email, adresse).
- Acceptation CGU + contrat cadre Symbiose.

Stripe Connect / Lemonway gère la conformité KYC de second niveau côté prestataire de paiement.

---

## Flow visuel (pseudo-diagramme)

```
Landing
  └─▶ [CTA "Déposer un besoin"]
        └─▶ Signup (email + pwd/SSO)
              └─▶ Qualification besoin (6 questions, copilote IA)
                    └─▶ Profil entreprise express (3 champs)
                          └─▶ ★ Matching ★ (3 profils affichés)
                                └─▶ [Clic "Contacter"]
                                      └─▶ Espace mission créé (chat + checklist)
                                            └─▶ (plus tard) KYC + facturation
                                                  └─▶ Mission active
```

---

## Données à capturer (vue minimale MVP)

| Entité | Champs |
|--------|--------|
| `User` | email, password_hash, role (pme), created_at, email_verified_at |
| `Company` | user_id, name, sector, size_bucket, siret (null jusqu'au KYC), iban (null), billing_contact (null) |
| `Need` (besoin) | company_id, domain, description, deliverables[], duration, urgency_date, budget_min, budget_max, seniority, values_tags[], created_at |
| `MatchingProposal` | need_id, talent_id, score, explanation, created_at |
| `MissionSpace` | need_id, talent_id, status, created_at |

*Schéma détaillé sera formalisé dans `docs/tech/` (en anglais) lors de l'étape Architecture technique.*

---

## Métriques d'activation ciblées

- **Time-to-matching** : < 15 min (signup → affichage des 3 profils).
- **Completion rate étape 2** (qualification besoin) : > 80 %.
- **Completion rate étape 4** (clic sur au moins un profil) : > 50 %.
- **Abandon par étape** : monitoré, alertes si un step dépasse 30 % d'abandon.

---

## Questions ouvertes

1. **Anti-abus signup** : faut-il un captcha dès l'étape 1 ou seulement si comportement suspect ? (Impact friction.)
2. **Modération profil entreprise** : vérification manuelle des nouvelles PME ou 100 % automatique via API INSEE ?
3. **Langue du copilote IA** : FR uniquement au MVP ou EN dispo pour internationaux résidant en FR ?
4. **Paiement** : Stripe Connect vs Lemonway vs MangoPay — à benchmarker à l'étape tech.
5. **Partage de coordonnées hors-plateforme** : stratégie anti-bypass (interdiction d'échange d'emails dans le chat avant signature) — MVP ou Phase 2 ?
