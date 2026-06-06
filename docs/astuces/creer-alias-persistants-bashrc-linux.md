---
title: Créer des alias persistants avec .bashrc
date: 2026-06-06
author: Nicolas BODAINE
tags:
  - bash
  - alias
  - linux
  - astuce
difficulty: débutant
os: Linux (toutes distributions)
status: publié
---

# Créer des alias persistants avec .bashrc

!!! abstract "Résumé"
    Sous Linux, on se retrouve souvent à taper les mêmes longues commandes encore et encore. Ce tutoriel montre comment utiliser les alias via le fichier `~/.bashrc` pour créer des raccourcis de commandes permanents et ainsi gagner du temps au quotidien.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux |
| Dernière mise à jour | 2026-06-06 |

## Contexte

Dans la vie d'un administrateur système ou d'un développeur, la ligne de commande est omniprésente. Taper sans cesse `sudo apt update && sudo apt upgrade -y` ou `ls -la --color=auto` finit par être laborieux. Heureusement, le shell `bash` (utilisé par défaut sur Ubuntu, Debian, et de nombreuses autres distributions) permet de créer des **alias** : des raccourcis personnels pour exécuter de longues commandes en quelques lettres seulement.

Toutefois, si vous créez un alias directement dans le terminal (par exemple `alias maj="sudo apt update"`), ce dernier disparaîtra dès que vous fermerez votre session. Pour les rendre persistants, il faut les inscrire dans un fichier de configuration, généralement `~/.bashrc` ou `~/.bash_aliases`.

## Procédure

### Étape 1 : Tester un alias temporaire

Avant de rendre un alias permanent, vous pouvez le tester dans votre session actuelle. 
Essayez par exemple de créer un raccourci `ll` pour la commande affichant le contenu d'un dossier en détail avec la taille lisible par un humain :

```bash
alias ll="ls -lah"
```

Tapez ensuite `ll` et validez. Vous devriez voir le contenu du répertoire courant s'afficher. Dès la fermeture du terminal, cet alias sera toutefois oublié.

### Étape 2 : Éditer le fichier `.bashrc` ou `.bash_aliases`

Pour qu'un alias survive aux redémarrages, il faut le définir dans votre profil utilisateur.
Sur de nombreuses distributions (comme Ubuntu), le fichier `~/.bashrc` contient déjà une condition qui charge le fichier `~/.bash_aliases` s'il existe. C'est donc la meilleure pratique d'utiliser ce second fichier pour ne pas polluer votre configuration principale.

Ouvrez (ou créez) ce fichier avec l'éditeur `nano` :

```bash
nano ~/.bash_aliases
```

### Étape 3 : Ajouter vos alias

Ajoutez vos raccourcis préférés dans le fichier. Voici quelques exemples classiques et très pratiques :

```bash title="~/.bash_aliases" linenums="1"
# Navigation rapide
alias ..="cd .."
alias ...="cd ../.."

# Gestion des paquets (Debian/Ubuntu)
alias maj="sudo apt update && sudo apt upgrade -y"
alias install="sudo apt install"

# Confort visuel et détails
alias ll="ls -lah --color=auto"
alias df="df -h" # Espace disque en format humain (Go, Mo)
alias free="free -h" # Mémoire RAM en format humain

# Sécurité : confirmation avant écrasement ou suppression
alias rm="rm -i"
alias cp="cp -i"
alias mv="mv -i"
```

Enregistrez les modifications (avec `nano`, tapez ++ctrl+o++, puis ++enter++, puis ++ctrl+x++).

### Étape 4 : Appliquer les changements

Pour que le shell prenne immédiatement en compte ces nouveaux alias sans avoir à fermer et rouvrir la session, utilisez la commande `source` pour recharger votre configuration :

```bash
source ~/.bashrc
```

## Vérification

Pour vérifier que vos alias sont bien enregistrés et fonctionnels, vous pouvez lister tous les alias actifs en tapant simplement la commande `alias` :

```bash
alias
```

!!! success "Résultat attendu"
    Le terminal doit vous afficher la liste complète des raccourcis définis, incluant ceux que vous venez d'ajouter, par exemple :
    `alias ll='ls -lah --color=auto'`

Vous pouvez alors taper `maj` ou `ll` pour vérifier leur bon fonctionnement.

## Ressources

- [Documentation GNU Bash - Aliases](https://www.gnu.org/software/bash/manual/html_node/Aliases.html) — Manuel officiel
- [Ubuntu Documentation - Command line aliases](https://help.ubuntu.com/community/Aliases) — Guide Ubuntu sur les alias