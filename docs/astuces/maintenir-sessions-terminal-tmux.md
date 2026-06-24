---
title: Maintenir ses sessions terminal actives et multiplexer son affichage avec Tmux
date: 2026-06-24
author: Nicolas BODAINE
tags:
  - tmux
  - terminal
  - linux
  - astuces
  - productivité
difficulty: débutant
os: Linux (Debian, Ubuntu, CentOS...)
status: publié
---

# Maintenir ses sessions terminal actives et multiplexer son affichage avec Tmux

!!! abstract "Résumé"
    Tmux (Terminal Multiplexer) est un outil indispensable pour tout administrateur système, développeur ou étudiant en informatique. Il permet de diviser la fenêtre de son terminal en plusieurs panneaux (multiplexage) et surtout de détacher une session pour la laisser tourner en arrière-plan, puis s'y rattacher plus tard. Idéal pour lancer de longs scripts sur un serveur distant sans craindre une coupure de connexion SSH !

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux |
| Dernière mise à jour | 2026-06-24 |

## Contexte

Lorsque vous êtes connecté en SSH sur un serveur distant et que vous lancez une commande longue (une mise à jour système, un script de sauvegarde, une compilation), la perte de votre connexion internet ou la fermeture de votre terminal va interrompre brutalement le processus.

Tmux résout ce problème en créant un environnement persistant sur le serveur. Même si vous vous déconnectez, les processus lancés à l'intérieur de Tmux continuent de s'exécuter. De plus, il vous permet d'avoir plusieurs terminaux visibles sur un seul écran.

## Prérequis

- Un accès terminal à une machine Linux (locale ou distante).
- Les droits d'installation des paquets si Tmux n'est pas déjà présent.

## Procédure

### Étape 1 : Installation de Tmux

La plupart des distributions Linux proposent Tmux dans leurs dépôts officiels.

=== "Debian / Ubuntu"

    ```bash
    sudo apt update
    sudo apt install tmux -y
    ```

=== "RHEL / CentOS / Fedora"

    ```bash
    sudo dnf install tmux -y
    ```

=== "Arch Linux"

    ```bash
    sudo pacman -S tmux
    ```

### Étape 2 : Lancer et nommer une session

Il est recommandé de toujours nommer ses sessions pour les retrouver facilement.

```bash
# Lancer une nouvelle session nommée "mise-a-jour"
tmux new -s mise-a-jour
```

Votre terminal change légèrement d'apparence, avec une barre d'état verte en bas. Vous êtes maintenant "dans" Tmux.

### Étape 3 : Multiplexer (diviser l'écran)

Dans Tmux, toutes les actions au clavier commencent par une combinaison de touches appelée "Prefix" (ou préfixe). Par défaut, c'est ++ctrl+b++.

1. Appuyez sur ++ctrl+b++ puis relâchez.
2. Appuyez sur une autre touche pour déclencher une action.

**Diviser l'écran :**
- ++ctrl+b++ puis ++"++ : Divise le panneau actuel **horizontalement** (haut/bas).
- ++ctrl+b++ puis ++%++ : Divise le panneau actuel **verticalement** (gauche/droite).

**Naviguer entre les panneaux :**
- ++ctrl+b++ puis utiliser les **flèches directionnelles** pour passer d'un panneau à l'autre.

**Fermer un panneau :**
- Tapez `exit` ou utilisez le raccourci ++ctrl+d++ pour fermer le panneau actif.

### Étape 4 : Détacher et rattacher une session

C'est la fonctionnalité la plus puissante de Tmux.

1. **Détacher la session (laisser tourner en arrière-plan) :**
   Appuyez sur ++ctrl+b++ puis ++d++. Vous revenez à votre terminal classique, mais la session Tmux continue de tourner.

2. **Lister les sessions actives :**
   ```bash
   tmux ls
   ```
   *Exemple de sortie : `mise-a-jour: 1 windows (created Wed Jun 24 12:00:00 2026) [80x24]`*

3. **Se rattacher à la session (revenir dedans) :**
   ```bash
   tmux attach -t mise-a-jour
   ```
   Vous retrouvez votre environnement exactement comme vous l'aviez laissé.

## Aide-mémoire des raccourcis essentiels

Le préfixe par défaut est ++ctrl+b++.

| Action | Raccourci |
|--------|-----------|
| Créer une nouvelle fenêtre | ++ctrl+b++ puis ++c++ |
| Passer à la fenêtre suivante | ++ctrl+b++ puis ++n++ |
| Passer à la fenêtre précédente | ++ctrl+b++ puis ++p++ |
| Diviser horizontalement | ++ctrl+b++ puis ++"++ |
| Diviser verticalement | ++ctrl+b++ puis ++%++ |
| Naviguer entre les panneaux | ++ctrl+b++ puis **flèches** |
| Détacher la session | ++ctrl+b++ puis ++d++ |
| Activer le mode défilement/copie | ++ctrl+b++ puis ++[++ (utiliser `q` pour quitter) |

## Ressources

- [Manuel de Tmux (man page)](https://man7.org/linux/man-pages/man1/tmux.1.html) — Documentation officielle complète.
- [Tmux Cheat Sheet](https://tmuxcheatsheet.com/) — Liste exhaustive de raccourcis utiles.