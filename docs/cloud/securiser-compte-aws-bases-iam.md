---
title: "Sécuriser son compte AWS : les bases d'IAM (Identity and Access Management)"
date: 2026-06-26
author: Nicolas BODAINE
tags:
  - AWS
  - IAM
  - Cloud
  - Sécurité
difficulty: débutant
os: AWS
status: publié
---

# Sécuriser son compte AWS : les bases d'IAM (Identity and Access Management)

!!! abstract "Résumé"
    Ce tutoriel présente les bonnes pratiques pour sécuriser votre compte AWS dès sa création. Vous apprendrez à configurer l'authentification multifacteur (MFA) pour l'utilisateur racine, et à créer un utilisateur administrateur via IAM pour vos opérations quotidiennes, en respectant le principe du moindre privilège.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | AWS Management Console |
| Dernière mise à jour | 2026-06-26 |

## Contexte

Lorsque vous créez un compte Amazon Web Services (AWS), vous disposez d'un **utilisateur racine** (Root user) qui possède un accès illimité à l'intégralité des ressources et des services de facturation. Si les identifiants de ce compte tombent entre de mauvaises mains, les conséquences (notamment financières) peuvent être désastreuses. 

Il est donc crucial de sécuriser cet accès racine et de créer des utilisateurs restreints pour l'administration et le déploiement au quotidien via le service **IAM** (Identity and Access Management).

## Prérequis

- Un compte AWS fraîchement créé (ou existant).
- L'accès à l'adresse email associée au compte racine.
- Une application d'authentification sur votre smartphone (Authy, Google Authenticator, Microsoft Authenticator...).

## Procédure

### Étape 1 : Sécuriser l'utilisateur racine (Root user)

La première étape indispensable est de verrouiller l'accès au compte racine.

1. Connectez-vous à la [Console de gestion AWS](https://console.aws.amazon.com/) en utilisant l'option **Utilisateur racine**.
2. Dans la barre de navigation supérieure droite, cliquez sur votre nom de compte, puis sur **Security credentials** (Informations d'identification de sécurité).
3. Dans la section **Multi-factor authentication (MFA)**, cliquez sur **Assign MFA device** (Attribuer un appareil MFA).
4. Saisissez un nom (ex: `MFA-Root`), sélectionnez **Authenticator app** (Application d'authentification) puis cliquez sur **Next**.
5. Scannez le QR code affiché avec votre application smartphone.
6. Entrez deux codes successifs générés par l'application pour valider la configuration.

!!! warning "Ne créez jamais de clés d'accès (Access Keys) pour le compte racine"
    Le compte racine ne doit **jamais** être utilisé de manière programmatique via l'AWS CLI ou par des scripts.

### Étape 2 : Créer un groupe d'administrateurs

Plutôt que d'attribuer des droits directement à des utilisateurs, la bonne pratique (inspirée des recommandations de sécurité comme le NIST) consiste à attribuer les droits à un groupe, puis d'y placer les utilisateurs.

1. Allez dans le service **IAM**.
2. Dans le menu de gauche, cliquez sur **User groups** (Groupes d'utilisateurs), puis sur **Create group**.
3. Nommez le groupe `Admins`.
4. Dans la section **Attach permissions policies**, recherchez la stratégie `AdministratorAccess`.
5. Cochez la case correspondante et cliquez sur **Create group**.

### Étape 3 : Créer un utilisateur IAM pour le quotidien

Vous allez maintenant créer votre compte d'administration quotidien.

1. Toujours dans **IAM**, cliquez sur **Users** dans le menu de gauche, puis sur **Create user**.
2. Nommez l'utilisateur (ex: `nicolas-admin`).
3. Cochez **Provide user access to the AWS Management Console**.
4. Sélectionnez **I want to create an IAM user** et choisissez **Custom password**. Décochez la demande de changement de mot de passe à la première connexion si vous êtes le seul utilisateur.
5. Cliquez sur **Next**.
6. À l'étape des permissions, choisissez **Add user to group**, et sélectionnez le groupe `Admins` créé précédemment.
7. Cliquez sur **Next**, puis sur **Create user**.
8. **Important :** Téléchargez ou copiez le fichier CSV contenant l'URL de connexion spécifique à votre compte, le nom d'utilisateur et le mot de passe. 

### Étape 4 : Activer le MFA pour l'utilisateur IAM

Même si cet utilisateur n'est pas le compte racine, il possède des droits d'administration. Le MFA est indispensable.

1. Déconnectez-vous du compte racine.
2. Utilisez l'URL de connexion récupérée à l'étape précédente pour vous connecter avec le nouvel utilisateur IAM.
3. Allez dans **IAM** > **Users**, cliquez sur votre nom d'utilisateur.
4. Dans l'onglet **Security credentials**, activez un appareil MFA (Même procédure qu'à l'Étape 1).

### Étape 5 : Définir une politique de mot de passe (Password Policy)

Pour renforcer la sécurité de l'ensemble des futurs utilisateurs de votre compte :

1. Dans **IAM**, menu de gauche, sélectionnez **Account settings** (Paramètres du compte).
2. Dans **Password policy**, cliquez sur **Edit**.
3. Cochez les options recommandées :
    - Longueur minimale de 14 caractères.
    - Exiger au moins une lettre majuscule, une lettre minuscule, un chiffre et un caractère spécial.
    - Empêcher la réutilisation des mots de passe.
4. Cliquez sur **Save changes**.

## Vérification

Pour vous assurer que votre compte est correctement configuré :

1. Connectez-vous avec votre **utilisateur IAM**. L'authentification MFA doit vous être demandée.
2. Rendez-vous sur le tableau de bord IAM.
3. Vérifiez la section **Security recommendations** à droite de l'écran. Vous devriez avoir une coche verte indiquant que votre compte racine est protégé par MFA.

!!! success "Résultat attendu"
    Votre compte racine est désormais sécurisé et vous opérez via un compte IAM tracé, respectant ainsi le principe de séparation des privilèges.

## Ressources

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) — Documentation officielle AWS sur les bonnes pratiques de sécurité.
- [Principes du moindre privilège](https://csrc.nist.gov/glossary/term/least_privilege) — Référentiel NIST sur la sécurité informatique.
- [Tutoriel : Installer et configurer l'AWS CLI](installer-configurer-aws-cli.md) — Pour configurer vos accès programmatiques avec un utilisateur IAM.
