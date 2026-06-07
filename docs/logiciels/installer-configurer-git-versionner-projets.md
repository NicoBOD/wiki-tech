---
title: Installer et configurer Git pour versionner ses premiers projets
date: 2026-06-07
author: Nicolas BODAINE
tags:
  - git
  - versionning
  - devops
  - github
difficulty: débutant
os: Ubuntu 24.04 / Windows
status: publié
---

# Installer et configurer Git pour versionner ses premiers projets

!!! abstract "Résumé"
    Git est l'outil standard incontournable pour suivre les modifications de son code (versioning) et travailler en équipe. Ce tutoriel détaille l'installation, la configuration initiale obligatoire et les toutes premières commandes pour versionner vos scripts en local.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 / Windows 11 |
| Dernière mise à jour | 2026-06-07 |

## Contexte

Dès lors que vous écrivez des scripts, des fichiers de configuration ou du code (comme des manifestes Docker ou Ansible), vous avez besoin d'un outil pour :
- **Conserver un historique** de toutes les modifications.
- **Revenir en arrière** si une modification casse votre application.
- **Collaborer** facilement avec d'autres personnes via des plateformes comme GitHub ou GitLab.

L'outil standard de l'industrie pour cela est Git.

## Prérequis

- Un système d'exploitation fonctionnel (Windows, macOS ou Linux).
- Des droits d'administration pour installer le paquet.
- Un terminal (Bash sur Linux/macOS, PowerShell sur Windows).

## Procédure

### Étape 1 : Installer Git

L'installation de Git dépend de votre système d'exploitation.

=== "Linux (Ubuntu/Debian)"

    ```bash
    sudo apt update
    sudo apt install git
    ```

=== "Windows"

    Vous pouvez télécharger l'installeur classique depuis le [site officiel de Git](https://git-scm.com/downloads) (Git for Windows), ou utiliser `winget` dans PowerShell :

    ```powershell
    winget install --id Git.Git -e --source winget
    ```

### Étape 2 : Vérifier l'installation

Assurez-vous que la commande `git` est désormais reconnue par votre système.

```bash
git --version
```

!!! success "Résultat attendu"
    Vous devriez obtenir un retour indiquant la version, par exemple : `git version 2.43.0`. Si vous êtes sur Windows et que la commande n'est pas trouvée, redémarrez votre terminal PowerShell.

### Étape 3 : Configuration initiale

Avant de faire votre premier "commit" (enregistrement dans l'historique), Git doit savoir qui vous êtes. Ces informations seront attachées à chaque modification que vous validerez de manière permanente.

Configurez votre identité globale en exécutant ces deux commandes :

```bash
git config --global user.name "Votre Prénom Nom"
git config --global user.email "votre.email@exemple.com"
```

!!! tip "Adresse email"
    Utilisez l'adresse email rattachée à votre compte GitHub/GitLab si vous prévoyez d'envoyer votre code en ligne par la suite.

### Étape 4 : Initialiser son premier dépôt local

Un dépôt (ou *repository* / *repo*) n'est rien d'autre qu'un dossier dont le contenu est surveillé par Git.

1. Créez un dossier pour votre projet et déplacez-vous dedans :
    ```bash
    mkdir mon-premier-projet
    cd mon-premier-projet
    ```

2. Initialisez Git dans ce dossier :
    ```bash
    git init
    ```
    *Un dossier caché `.git` est créé. C'est ici que Git stockera tout l'historique de votre projet.*

3. Créez un fichier basique et ajoutez-y du contenu pour faire un premier test :
    ```bash
    echo "Mon premier script" > script.sh
    ```

### Étape 5 : Versionner ses modifications (Add et Commit)

Git procède en deux étapes pour enregistrer des modifications : la préparation dans la zone de transit (*staging area*) et la validation finale (*commit*).

1. Vérifiez l'état de votre projet :
    ```bash
    git status
    ```
    *Git vous indique que le fichier `script.sh` est "Untracked" (non suivi par Git).*

2. Ajoutez le fichier à la zone de transit (ce qu'on s'apprête à valider) :
    ```bash
    git add script.sh
    ```
    *(Pour tout ajouter d'un coup de manière récursive, on utilise souvent `git add .`)*

3. Validez les changements avec un message explicite :
    ```bash
    git commit -m "docs: création du premier script"
    ```

## Vérification

Pour voir l'historique de vos validations, utilisez la commande log qui permet de tracer les modifications :

```bash
git log --oneline
```

!!! success "Résultat attendu"
    Une liste compacte des commits s'affiche, du plus récent au plus ancien, par exemple :
    `a1b2c3d docs: création du premier script`

## Ressources

- [Documentation officielle Git](https://git-scm.com/doc) — Livre complet *Pro Git* (gratuit et traduit en français).
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials) — Excellents tutoriels visuels sur les concepts de Git.