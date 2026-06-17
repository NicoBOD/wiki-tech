---
title: Manipuler et exécuter des commandes en lots avec xargs
date: 2026-06-17
author: Nicolas BODAINE
tags:
  - linux
  - terminal
  - bash
  - xargs
  - astuces
difficulty: intermédiaire
os: Linux
status: publié
---

# Manipuler et exécuter des commandes en lots avec xargs

!!! abstract "Résumé"
    Découvrez comment utiliser `xargs` pour exécuter des commandes efficacement sur de grandes listes d'éléments. Cet outil est indispensable pour traiter en lot les résultats d'autres commandes, comme `find` ou `grep`, et accélérer les tâches répétitives en ligne de commande.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux, macOS, Unix |
| Dernière mise à jour | 2026-06-17 |

## Contexte

Dans l'administration système et l'utilisation quotidienne du terminal Linux, il est fréquent de devoir appliquer une même commande à de multiples fichiers ou résultats. Si les boucles `for` sont souvent utilisées, la commande `xargs` se révèle beaucoup plus rapide, concise et puissante. Elle permet de construire et d'exécuter des commandes à partir de l'entrée standard (stdin).

## Fonctionnement de base

`xargs` lit des éléments délimités par des espaces ou des sauts de ligne depuis l'entrée standard, et exécute la commande spécifiée une ou plusieurs fois avec ces éléments comme arguments initiaux.

```bash
# Exemple basique : passer une liste de mots à la commande echo pour créer des fichiers
echo "fichier1 fichier2 fichier3" | xargs touch
```

Cette commande crée trois fichiers. C'est l'équivalent de taper `touch fichier1 fichier2 fichier3`.

## Cas d'usage courants

### 1. Traitement combiné avec `find`

L'utilisation la plus courante de `xargs` est le couplage avec la commande `find` pour agir sur des fichiers trouvés.

```bash
# Supprimer tous les fichiers .log vieux de plus de 30 jours
find /var/log -name "*.log" -mtime +30 | xargs rm
```

!!! warning "Espaces dans les noms de fichiers"
    Si vos noms de fichiers contiennent des espaces, l'exemple précédent échouera, car `xargs` considérera chaque mot comme un argument distinct. Utilisez l'option `-print0` avec `find` et `-0` avec `xargs` pour séparer les éléments par le caractère nul (`\0`).

```bash
# Version robuste (gère les noms avec espaces)
find /var/log -name "*.log" -mtime +30 -print0 | xargs -0 rm
```

### 2. Contrôler le nombre d'arguments par exécution

Par défaut, `xargs` tente de passer un maximum d'arguments en une seule fois. L'option `-n` permet de limiter le nombre d'arguments par exécution.

```bash
# Afficher les fichiers deux par deux
echo "a b c d e f" | xargs -n 2 echo
```

### 3. Utiliser un paramètre de remplacement (placeholder)

Lorsque la commande requiert que l'argument soit inséré à un endroit précis (et non simplement ajouté à la fin), utilisez l'option `-I` pour définir un caractère de remplacement, souvent `{}`.

```bash
# Copier tous les fichiers .txt vers un dossier de sauvegarde
find . -name "*.txt" | xargs -I {} cp {} /backup/
```

### 4. Parallélisation des tâches

Pour exécuter plusieurs processus en parallèle, utilisez l'option `-P`. Cela peut accélérer considérablement les tâches sur les machines multi-cœurs.

```bash
# Télécharger une liste d'URLs en parallèle (jusqu'à 4 processus)
cat urls.txt | xargs -n 1 -P 4 wget -q
```

## Vérification et exécution sûre

L'option `-p` demande une confirmation avant d'exécuter chaque commande. L'option `-t` affiche la commande sur la sortie standard d'erreur avant de l'exécuter.

```bash
# Confirmer avant de supprimer
find /tmp -name "*.tmp" | xargs -p rm
```

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `xargs -0` | Traite l'entrée séparée par le caractère nul (indispensable avec `find -print0`). |
| `xargs -I {}` | Remplace `{}` par la valeur lue dans la ligne de commande. |
| `xargs -n X` | Utilise au maximum `X` arguments par exécution. |
| `xargs -P Y` | Exécute jusqu'à `Y` processus simultanément. |
| `xargs -t` | Affiche la commande avant de l'exécuter. |
| `xargs -p` | Demande confirmation (`y`/`n`) avant chaque exécution. |

## Ressources

- [Manuel GNU Findutils pour xargs](https://www.gnu.org/software/findutils/manual/html_node/find_html/xargs-options.html) — Documentation officielle détaillée.
- [Ubuntu Manpage (man xargs)](https://manpages.ubuntu.com/manpages/jammy/en/man1/xargs.1.html) — Page de manuel en ligne d'Ubuntu.
