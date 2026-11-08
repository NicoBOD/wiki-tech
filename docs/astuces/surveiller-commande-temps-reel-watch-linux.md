---
title: Surveiller une commande en temps réel avec watch sous Linux
date: 2026-11-08
author: Nicolas BODAINE
tags:
  - linux
  - terminal
  - supervision
  - outils
difficulty: débutant
os: Linux (toutes distributions)
status: publié
---

# Surveiller une commande en temps réel avec watch sous Linux

!!! abstract "Résumé"
    `watch` relance une commande à intervalle régulier et rafraîchit l'affichage. C'est idéal pour suivre l'espace disque, une copie en cours, un service qui redémarre ou les connexions réseau, sans écrire de boucle `while`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux (Ubuntu 24.04, Debian 13...) |
| Dernière mise à jour | 2026-11-08 |

## Contexte

Lancer la même commande dix fois de suite (`df -h`, `ls -l`, `systemctl status`...) pour voir si « ça bouge » est fastidieux. La commande `watch`, fournie par le paquet `procps` (installé par défaut sur la plupart des distributions), exécute la commande à votre place toutes les 2 secondes par défaut et affiche le résultat en plein écran.

## Prérequis

- Un terminal Linux (VM de test, WSL ou poste de lab)
- Aucun droit particulier, sauf pour les commandes surveillées elles-mêmes

Vérifiez que `watch` est présent :

```bash
watch --version
```

Si la commande est absente :

```bash
sudo apt install procps
```

## Procédure

### Étape 1 : Premier usage

```bash
watch date
```

L'heure se rafraîchit toutes les 2 secondes. En haut de l'écran, `watch` affiche l'intervalle, la commande et l'heure. Quittez avec ++ctrl+c++.

### Étape 2 : Changer l'intervalle avec -n

```bash
watch -n 5 df -h /
```

L'espace disque de `/` est relu toutes les 5 secondes.

### Étape 3 : Surligner les changements avec -d

```bash
watch -d -n 1 'ls -l /tmp'
```

L'option `-d` (`--differences`) met en surbrillance les caractères qui ont changé depuis le dernier rafraîchissement. Avec `-d=cumulative`, toutes les zones modifiées restent surlignées.

!!! tip "Testez-le"
    Dans un second terminal, lancez `touch /tmp/test-watch` : la nouvelle ligne apparaît surlignée.

### Étape 4 : Utiliser des pipes et des guillemets

Pour que le tube `|` soit interprété par la commande surveillée et non par votre shell, placez toute la commande entre guillemets :

```bash
watch -n 2 'ss -tn state established | wc -l'
```

Ici, on suit le nombre de connexions TCP établies.

### Étape 5 : Suivre un service ou un journal

```bash
watch -n 2 'systemctl is-active ssh'
```

```bash
watch -n 1 'journalctl -n 5 --no-pager'
```

### Étape 6 : Sortir automatiquement quand ça change ou échoue

- `-g` (`--chgexit`) : quitte dès que la sortie change. Pratique pour attendre un événement.
- `-e` (`--errexit`) : quitte si la commande renvoie un code d'erreur et attend une touche.

```bash
watch -g 'ls /mnt/usb'
```

La commande se termine dès qu'un contenu apparaît dans `/mnt/usb`.

### Étape 7 : Masquer l'en-tête et gérer les couleurs

```bash
watch -t -c 'ls --color=always'
```

- `-t` supprime l'en-tête
- `-c` (`--color`) interprète les couleurs ANSI

## Vérification

```bash
watch -n 1 -d 'date +%S'
```

!!! success "Résultat attendu"
    Les secondes s'incrémentent chaque seconde, avec les chiffres modifiés surlignés. ++ctrl+c++ rend la main.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `watch cmd` | Exécute `cmd` toutes les 2 s |
| `watch -n 5 cmd` | Intervalle de 5 s |
| `watch -d cmd` | Surligne les différences |
| `watch -t cmd` | Cache l'en-tête |
| `watch -c cmd` | Affiche les couleurs ANSI |
| `watch -g cmd` | Quitte quand la sortie change |
| `watch -e cmd` | Quitte en cas d'erreur |
| `watch 'a \| b'` | Guillemets pour les pipes |

## Bonnes pratiques

- Ne descendez pas sous 1 seconde sur une commande lourde : vous chargeriez inutilement la machine.
- `watch` ne conserve pas d'historique : pour garder une trace, utilisez plutôt un script avec [`tee`](capturer-afficher-sortie-simultanement-tee-linux.md) ou un vrai outil de supervision.
- Pour les journaux, `journalctl -f` est plus adapté (voir [journalctl](../debug/journalctl-lire-filtrer-suivre-logs-systemd-linux.md)).

## Ressources

- [Page de manuel watch(1)](https://man7.org/linux/man-pages/man1/watch.1.html) — Référence officielle des options
- [Projet procps-ng](https://gitlab.com/procps-ng/procps) — Source du paquet qui fournit watch
