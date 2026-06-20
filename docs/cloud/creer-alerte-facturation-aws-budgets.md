---
title: Créer une alerte de facturation sur AWS (AWS Budgets) pour sécuriser ses travaux pratiques
date: 2026-06-20
author: Nicolas BODAINE
tags:
  - aws
  - billing
  - cloud
  - securite
difficulty: débutant
os: Console AWS
status: publié
---

# Créer une alerte de facturation sur AWS (AWS Budgets) pour sécuriser ses travaux pratiques

!!! abstract "Résumé"
    Lorsque l'on débute sur AWS, il est très facile d'oublier de supprimer une ressource (instance EC2, base RDS) à la fin d'un TP et de se retrouver avec une facture surprise à la fin du mois. Cette fiche vous montre comment configurer une alerte de budget (AWS Budgets) qui vous notifiera par email dès que vos dépenses estimées dépassent un seuil défini (par exemple, 1 ou 5$).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Console Web AWS |
| Dernière mise à jour | 2026-06-20 |

## Contexte

Les services cloud publics comme Amazon Web Services (AWS) fonctionnent sur le modèle *Pay-As-You-Go* (paiement à l'usage). Même avec le "Free Tier" (Niveau Gratuit), une erreur d'inattention peut vous coûter cher. 

Pour travailler sereinement lors de vos labs ou TPs, la toute première étape sur un nouveau compte AWS doit toujours être de créer un "Garde-fou" : **une alerte de facturation**. AWS Budgets permet de définir un montant maximal que l'on souhaite dépenser (même 1$), et d'être prévenu par e-mail si les dépenses s'en approchent ou le dépassent.

## Prérequis

- Un compte AWS actif
- Avoir accès à la console avec un utilisateur ayant les permissions sur le service `Billing` (le compte Root a ces droits par défaut)
- (Optionnel) Avoir activé les alertes de facturation globales dans les préférences de facturation (recommandé).

## Procédure

### Étape 1 : Accéder au tableau de bord de facturation (Billing Dashboard)

1. Connectez-vous à la [Console AWS](https://console.aws.amazon.com/).
2. En haut à droite de l'interface, cliquez sur votre nom de compte.
3. Dans le menu déroulant, sélectionnez **Facturation et gestion des coûts** (Billing and Cost Management).

!!! tip "Raccourci de recherche"
    Vous pouvez aussi simplement taper `Billing` dans la barre de recherche globale (en haut au centre de la console) et cliquer sur le service "Billing".

### Étape 2 : Activer la réception des alertes de facturation (Préférence)

1. Dans le menu de gauche, descendez jusqu'à la section **Préférences** et cliquez sur **Préférences de facturation** (Billing preferences).
2. Dans l'encadré **Alert Alert preferences**, assurez-vous que les alertes sont activées et qu'une adresse email valide est renseignée pour recevoir les notifications relatives au solde gratuit (Free Tier usage alerts).

### Étape 3 : Créer le budget via AWS Budgets

1. Dans le menu de gauche (toujours dans *Billing*), repérez la section **Budgets et planification** et cliquez sur **Budgets**.
2. Cliquez sur le bouton orange **Créer un budget** (Create budget).
3. Par défaut, AWS vous propose une **Configuration simplifiée** (Simplified). Laissez cette option cochée.
4. Dans le panneau de configuration rapide, choisissez **Budget à montant fixe nul** (Zero spend budget) ou **Budget mensuel** (Monthly cost budget) :
   - *Budget à dépense nulle* : Vous alertera dès que le compte dépassera les limites du niveau gratuit (0.01$). Très pratique pour un compte exclusivement "Lab étudiant".
   - *Budget mensuel des coûts* : Si vous prévoyez une petite dépense, vous pouvez saisir par exemple `5$` dans le champ **Montant budgété** (Budgeted amount).
5. Saisissez l'adresse email sur laquelle vous souhaitez recevoir les alertes (Email recipients). Vous pouvez en séparer plusieurs par des virgules.
6. Cliquez sur le bouton en bas à droite : **Créer le budget** (Create budget).

!!! warning "Délai d'application"
    Une fois le budget créé, il peut s'écouler jusqu'à 24 heures avant que les premières métriques financières soient entièrement calculées et rattachées au budget par AWS.

## Vérification

Pour vérifier que le budget est actif et configuré :

1. Retournez dans le menu **Budgets** de la console de facturation.
2. Votre nouveau budget apparaît dans la liste (ex: *My Zero-Spend Budget*).
3. Son statut doit être **OK**. Si les dépenses dépassent le seuil, le statut passera à **Alarm** et un email sera expédié automatiquement.

!!! success "Résultat attendu"
    Votre budget est listé. Vous êtes maintenant protégé contre les mauvaises surprises. Pensez malgré tout à toujours éteindre ou détruire (via Terraform ou AWS CLI) vos ressources à la fin de vos TPs !

## Ressources

- [Documentation officielle AWS : Gestion des coûts avec AWS Budgets](https://docs.aws.amazon.com/fr_fr/cost-management/latest/userguide/budgets-managing-costs.html) — Détails sur la configuration avancée.
- [Le Niveau Gratuit AWS (Free Tier)](https://aws.amazon.com/fr/free/) — Liste des services inclus gratuitement pendant les 12 premiers mois.
