---
title: Diagnostiquer la consommation CPU et mémoire sous Linux avec htop et free
date: 2026-06-13
author: Nicolas BODAINE
tags:
  - linux
  - debug
  - cpu
  - ram
  - htop
  - free
difficulty: débutant
os: Linux
status: publié
---

# Diagnostiquer la consommation CPU et mémoire sous Linux avec htop et free

!!! abstract "Résumé"
    Apprenez à identifier rapidement quels processus consomment le plus de ressources (CPU et mémoire) sur un serveur Linux grâce aux commandes `htop` et `free`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu / Debian / RHEL |
| Dernière mise à jour | 2026-06-13 |

## Contexte

Lorsqu'un serveur devient lent ou qu'une application plante inopinément, la première étape du diagnostic consiste souvent à vérifier la consommation des ressources de la machine : le processeur (CPU) et la mémoire vive (RAM).

Linux fournit des outils intégrés et légers pour surveiller ces métriques en temps réel. Les plus courants sont `free` pour une vue d'ensemble de la mémoire, et `htop` pour le détail par processus.

## Prérequis

- Un accès terminal (local ou via SSH) à une machine Linux.
- Les droits d'installation de paquets si `htop` n'est pas déjà présent.

## Procédure

### 1. Vue d'ensemble de la mémoire avec `free`

La commande `free` permet de voir d'un coup d'œil l'état de la mémoire RAM et du swap (mémoire virtuelle sur le disque).

```bash
free -h
```

!!! tip "L'option `-h` (human-readable)"
    Elle affiche les valeurs en Mo (Mégaoctets) ou Go (Gigaoctets) au lieu des kilooctets par défaut, ce qui facilite grandement la lecture.

**Exemple de sortie :**

```text
               total        used        free      shared  buff/cache   available
Mem:           7.8Gi       1.2Gi       3.4Gi        20Mi       3.2Gi       6.3Gi
Swap:          2.0Gi          0B       2.0Gi
```

**Que regarder en priorité ?**

- **total** : La quantité totale de RAM installée.
- **available** : C'est le chiffre le plus important ! Il indique la mémoire *réellement* disponible pour de nouvelles applications, sans que le système ait besoin d'utiliser le swap.
- **buff/cache** : Mémoire utilisée par Linux pour accélérer les accès disques. Cette mémoire est relâchée automatiquement si une application en a besoin.

!!! warning "Ne confondez pas `free` et `available`"
    La colonne `free` indique la mémoire totalement inutilisée, ce qui est souvent faible sur Linux car le système utilise l'espace libre pour mettre en cache des fichiers (`buff/cache`). Référez-vous toujours à la colonne `available`.

### 2. Installer `htop`

`htop` est un gestionnaire de tâches interactif en ligne de commande. S'il n'est pas installé, vous pouvez l'ajouter facilement :

=== "Ubuntu / Debian"

    ```bash
    sudo apt update
    sudo apt install htop
    ```

=== "RHEL / Rocky Linux / AlmaLinux"

    ```bash
    sudo dnf install epel-release
    sudo dnf install htop
    ```

### 3. Analyser la consommation en temps réel avec `htop`

Lancez l'outil simplement en tapant :

```bash
htop
```

!!! note "Lancer avec sudo"
    Certaines informations sur les processus d'autres utilisateurs ou du système peuvent être masquées. Lancer `sudo htop` permet de tout voir.

**Comprendre l'interface :**

L'écran est divisé en deux parties principales :

1. **En haut (l'en-tête) :**
   - **Barres numérotées (1, 2, 3...) :** L'utilisation de chaque cœur du processeur.
   - **Mem :** La consommation de RAM (code couleur : vert = utilisé par les processus, bleu = buffers, jaune = cache).
   - **Swp :** L'utilisation du fichier d'échange (Swap).
   - **Load average :** La charge moyenne du système sur les 1, 5 et 15 dernières minutes. Si ce chiffre dépasse durablement le nombre de cœurs de votre processeur, le serveur est surchargé.

2. **En bas (la liste des processus) :**
   - **PID :** L'identifiant unique du processus.
   - **USER :** L'utilisateur qui a lancé le processus.
   - **%CPU :** Le pourcentage de processeur utilisé par le processus.
   - **%MEM :** Le pourcentage de mémoire vive utilisé.
   - **Command :** Le nom de l'application ou la ligne de commande exécutée.

### 4. Naviguer et filtrer dans `htop`

`htop` est interactif. Voici les raccourcis essentiels pour trouver le coupable :

- **Trier par consommation CPU :** Appuyez sur ++f6++ (SortBy) puis sélectionnez `PERCENT_CPU`. (C'est souvent le tri par défaut).
- **Trier par consommation mémoire :** Appuyez sur ++f6++ puis sélectionnez `PERCENT_MEM`.
- **Rechercher un processus spécifique :** Appuyez sur ++f3++ (Search), tapez le nom (ex: `nginx` ou `mysql`) et appuyez sur ++enter++.
- **Filtrer l'affichage :** Appuyez sur ++f4++ (Filter) pour n'afficher que les lignes contenant un mot précis.
- **Tuer un processus bloqué :** Sélectionnez le processus avec les flèches haut/bas, appuyez sur ++f9++ (Kill), choisissez le signal `SIGTERM` (ou `SIGKILL` en dernier recours) et validez avec ++enter++.

Pour quitter `htop`, appuyez sur ++f10++ ou la touche `q`.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `free -h` | Affiche la RAM totale, utilisée et disponible en format lisible. |
| `htop` | Lance le gestionnaire de tâches interactif. |
| `F6` (dans htop) | Ouvre le menu de tri (pour trier par CPU ou MEM). |
| `F9` (dans htop) | Envoie un signal pour arrêter (tuer) le processus sélectionné. |
| `q` (dans htop) | Quitter l'interface. |

## Ressources

- [Manuel de free (en anglais)](https://man7.org/linux/man-pages/man1/free.1.html)
- [Site officiel de htop](https://htop.dev/)
