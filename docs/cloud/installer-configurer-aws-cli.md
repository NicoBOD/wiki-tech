---
title: Configurer et utiliser AWS CLI pour interagir avec les services Amazon Web Services
date: 2026-06-18
author: Nicolas BODAINE
tags:
  - aws
  - cli
  - cloud
  - iac
  - shell
difficulty: débutant
os: Multi-plateforme
status: publié
---

# Configurer et utiliser AWS CLI

!!! abstract "Résumé"
    L'AWS Command Line Interface (CLI) est un outil unifié permettant de gérer l'ensemble de vos services Amazon Web Services depuis la ligne de commande et de les automatiser à l'aide de scripts. Ce tutoriel détaille comment l'installer, configurer vos accès sécurisés (Access Keys) et utiliser des profils multiples.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Windows / macOS / Linux |
| Dernière mise à jour | 2026-06-18 |

## Contexte

La console de gestion AWS (l'interface web) est pratique pour découvrir les services, mais s'avère vite chronophage et peu adaptée pour l'automatisation. L'**AWS CLI** est indispensable pour les administrateurs système, les ingénieurs DevOps et les développeurs qui souhaitent gérer leur infrastructure sous forme de code (IaC), écrire des scripts ou simplement gagner en rapidité lors de tâches répétitives.

## Prérequis

- Un compte **Amazon Web Services (AWS)** (le niveau gratuit _Free Tier_ suffit).
- Un utilisateur IAM (Identity and Access Management) disposant de clés d'accès (`Access Key ID` et `Secret Access Key`). **Ne jamais utiliser les clés du compte racine (root)**.
- Des droits administrateurs locaux sur votre machine pour procéder à l'installation.

## Procédure

### Étape 1 : Installation de l'AWS CLI (version 2)

L'AWS CLI v2 est la version la plus récente et recommandée. Elle inclut toutes les dépendances requises (pas besoin d'avoir Python d'installé).

=== "Linux (x86_64)"

    ```bash
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    ```

=== "Windows"

    Ouvrez PowerShell en tant qu'administrateur :
    ```powershell
    msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
    ```

=== "macOS"

    Téléchargez et exécutez le package officiel :
    ```bash
    curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
    sudo installer -pkg AWSCLIV2.pkg -target /
    ```

Vérifiez l'installation en fermant puis rouvrant votre terminal :
```bash
aws --version
```
!!! success "Résultat attendu"
    Vous devriez voir un résultat semblable à `aws-cli/2.15.0 Python/3.11 ...`.

### Étape 2 : Configuration initiale

La commande `aws configure` est la façon la plus rapide de configurer vos accès. Munissez-vous de vos clés IAM.

```bash
aws configure
```

L'outil vous demandera 4 informations de manière interactive :

1. **AWS Access Key ID** : L'identifiant de votre clé d'accès (ex: `AKIAIOSFODNN7EXAMPLE`).
2. **AWS Secret Access Key** : La clé secrète (ex: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`).
3. **Default region name** : La région AWS par défaut (ex: `eu-west-3` pour Paris ou `eu-west-1` pour l'Irlande).
4. **Default output format** : Le format des retours par défaut (entrez `json`, le plus standard).

!!! note "Où sont stockées ces informations ?"
    L'AWS CLI crée un dossier `.aws` dans votre répertoire utilisateur (`~/.aws/` sous Linux/macOS, `%USERPROFILE%\.aws\` sous Windows).
    - Les clés secrètes vont dans `~/.aws/credentials`.
    - La région et le format vont dans `~/.aws/config`.

### Étape 3 : Utilisation des profils nommés (Optionnel)

Si vous gérez plusieurs environnements (par exemple un compte "Dev" et un compte "Prod"), vous pouvez configurer des **profils**. 

Pour ajouter un nouveau profil, utilisez le paramètre `--profile` :

```bash
aws configure --profile prod
```

Ensuite, pour exécuter une commande avec ce compte spécifique, ajoutez `--profile prod` à la fin de la commande :

```bash
aws s3 ls --profile prod
```

Pour définir un profil par défaut temporairement pour votre session en cours, utilisez la variable d'environnement `AWS_PROFILE` :

=== "Linux / macOS"
    ```bash
    export AWS_PROFILE=prod
    ```

=== "Windows (PowerShell)"
    ```powershell
    $env:AWS_PROFILE="prod"
    ```

## Vérification

Pour valider que la configuration est correcte et que l'authentification fonctionne, appelez le service STS (Security Token Service) pour obtenir l'identité de l'appelant.

```bash
aws sts get-caller-identity
```

!!! success "Résultat attendu"
    La commande doit retourner un JSON contenant votre `Account` (l'ID de votre compte AWS), votre `UserId` et votre `Arn` (l'Amazon Resource Name de l'utilisateur IAM).
    ```json
    {
        "UserId": "AIDASAMPLEUSERID",
        "Account": "123456789012",
        "Arn": "arn:aws:iam::123456789012:user/votre_nom_utilisateur"
    }
    ```

## Ressources

- [Documentation officielle AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) — Guide de démarrage complet
- [Trouver les identifiants de sécurité de son compte AWS](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) — Documentation IAM pour générer ses Access Keys