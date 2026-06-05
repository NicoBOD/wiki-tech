---
title: Maintenir ses sessions terminal à distance avec tmux sous Linux
date: 2026-06-05
author: Nicolas BODAINE
tags:
  - linux
  - terminal
  - ssh
  - tmux
difficulty: débutant
os: Ubuntu 24.04 | Debian 12
status: publié
---

# Maintenir ses sessions terminal à distance avec tmux sous Linux

!!! abstract "Résumé"
    Ce tutoriel explique comment utiliser `tmux` (Terminal Multiplexer) pour maintenir des sessions terminal ouvertes même en cas de coupure réseau, et comment gérer plusieurs fenêtres ou panneaux dans une seule connexion SSH. C'est un outil indispensable pour l'administration système.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux (Ubuntu, Debian, etc.) |
| Dernière mise à jour | 2026-06-05 |

## Contexte

Lorsque vous administrez un serveur distant via SSH, l'exécution d'une commande longue (comme une mise à jour système, une compilation ou un script de sauvegarde) peut être risquée : si votre connexion réseau coupe ou que vous fermez accidentellement votre terminal, la commande s'interrompt brutalement.

**tmux** (Terminal Multiplexer) résout ce problème en créant une session persistante sur le serveur. Vous pouvez lancer votre commande, "détacher" la session pour fermer votre terminal en toute sécurité, puis vous y "rattacher" plus tard, depuis n'importe où. De plus, `tmux` permet de diviser un seul terminal en plusieurs panneaux ou fenêtres, évitant ainsi d'ouvrir de multiples connexions SSH.

## Prérequis

- Un accès à une machine Linux (physique, VM ou Cloud).
- Des droits d'administration (`sudo`) pour l'installation, bien que l'utilisation de `tmux` ne nécessite pas de privilèges particuliers.

## Procédure

### Étape 1 : Installation de tmux

Sur les distributions basées sur Debian ou Ubuntu, `tmux` est présent dans les dépôts officiels.

```bash
sudo apt update
sudo apt install -y tmux
```

### Étape 2 : Lancer et détacher une session simple

Pour démarrer votre première session `tmux`, tapez simplement :

```bash
tmux
```

Une nouvelle session s'ouvre avec une barre d'état verte en bas de l'écran. Vous pouvez y taper vos commandes normalement. Par exemple, lancez une commande qui tourne en boucle :

```bash
ping 8.8.8.8
```

Maintenant, nous allons **détacher** la session pour la laisser tourner en arrière-plan. Dans `tmux`, toutes les actions commencent par un préfixe clavier (par défaut `Ctrl+b`), suivi d'une touche d'action.

1. Appuyez sur ++ctrl+b++, puis relâchez les touches.
2. Appuyez sur la touche ++d++ (pour *detach*).

Vous retrouvez votre invite de commande d'origine. Le `ping` continue de tourner sur le serveur !

### Étape 3 : Lister et rattacher les sessions

Pour voir les sessions `tmux` actuellement actives sur le serveur :

```bash
tmux ls
```

!!! success "Résultat attendu"
    ```text
    0: 1 windows (created Fri Jun  5 10:00:00 2026) [80x24]
    ```

Pour revenir à cette session et voir le `ping` toujours en cours, rattachez-vous (*attach*) :

```bash
tmux attach -t 0
```
*(Vous pouvez utiliser `tmux a` en raccourci).*

Arrêtez le ping avec ++ctrl+c++, puis tapez `exit` pour fermer et détruire définitivement cette session `tmux`.

### Étape 4 : Créer des sessions nommées

Il est plus pratique de nommer ses sessions pour s'y retrouver.

```bash
tmux new -s supervision
```

Pour s'y rattacher plus tard :

```bash
tmux attach -t supervision
```

### Étape 5 : Gérer plusieurs fenêtres et panneaux

`tmux` brille par sa capacité à diviser l'écran. Assurez-vous d'être dans une session `tmux` pour tester ces raccourcis.

**Gérer les fenêtres (comme des onglets) :**

- Créer une nouvelle fenêtre : ++ctrl+b++ puis ++c++ (*create*)
- Passer à la fenêtre suivante : ++ctrl+b++ puis ++n++ (*next*)
- Revenir à la fenêtre précédente : ++ctrl+b++ puis ++p++ (*previous*)

**Diviser l'écran en panneaux (splits) :**

- Diviser l'écran **verticalement** (gauche/droite) : ++ctrl+b++ puis ++%++
- Diviser l'écran **horizontalement** (haut/bas) : ++ctrl+b++ puis ++"++
- Naviguer entre les panneaux : ++ctrl+b++ puis les **Flèches directionnelles**

## Aide-mémoire

Voici les raccourcis fondamentaux de `tmux` (le préfixe par défaut est **Ctrl+b**) :

| Action `tmux` | Raccourci / Commande |
|--------------|----------------------|
| **Démarrer une session** | `tmux` |
| **Démarrer une session nommée** | `tmux new -s <nom>` |
| **Détacher la session (laisser tourner)** | ++ctrl+b++ puis ++d++ |
| **Lister les sessions actives** | `tmux ls` |
| **Se rattacher à une session** | `tmux attach -t <nom_ou_numero>` |
| **Scroller dans le terminal** | ++ctrl+b++ puis ++[++ *(utilisez les flèches pour monter/descendre, puis ++q++ pour quitter)* |
| **Fermer la session actuelle** | Tapez `exit` ou ++ctrl+d++ |

## Ressources

- [Manuel officiel de tmux (man page)](https://man7.org/linux/man-pages/man1/tmux.1.html) — Documentation complète.
- [tmux Cheat Sheet](https://tmuxcheatsheet.com/) — Un excellent aide-mémoire visuel pour tous les raccourcis.
