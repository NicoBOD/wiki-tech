---
title: Gagner en productivité dans le terminal avec fzf (Fuzzy Finder)
date: 2026-06-11
author: Nicolas BODAINE
tags:
  - linux
  - terminal
  - bash
  - outils
difficulty: débutant
os: Linux (toutes distributions)
status: publié
---

# Gagner en productivité dans le terminal avec fzf (Fuzzy Finder)

!!! abstract "Résumé"
    Découvrez `fzf` (Fuzzy Finder), un outil en ligne de commande ultra-rapide qui révolutionne la recherche de fichiers, la navigation dans l'historique et la sélection interactive dans le terminal Linux.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux, macOS (fonctionne aussi sous WSL/Windows) |
| Dernière mise à jour | 2026-06-11 |

## Contexte

Dans le terminal, la recherche d'un fichier spécifique ou d'une ancienne commande peut rapidement devenir fastidieuse. Les commandes classiques comme `find` ou l'historique de base (`Ctrl+R`) manquent souvent de souplesse si vous ne vous rappelez pas du nom ou de la syntaxe exacte. 

C'est là qu'intervient **`fzf` (Fuzzy Finder)**. C'est un filtre interactif en ligne de commande qui utilise la "recherche floue" : vous tapez simplement quelques lettres correspondant à ce que vous cherchez, même dans le désordre, et `fzf` vous affiche instantanément les meilleurs résultats.

## Prérequis

- Un terminal sous Linux (ou macOS / WSL).
- Des droits suffisants pour installer un paquet (privilèges sudo).

## Installation

L'installation de `fzf` est extrêmement simple puisqu'il est disponible dans la plupart des dépôts officiels.

=== "Debian / Ubuntu"

    ```bash
    sudo apt update
    sudo apt install fzf
    ```

=== "RHEL / Fedora / CentOS"

    ```bash
    sudo dnf install fzf
    ```

=== "Arch Linux"

    ```bash
    sudo pacman -S fzf
    ```

=== "Git (Toutes distros)"

    Pour avoir la toute dernière version et installer les raccourcis clavier automatiques pour votre shell (bash, zsh) :
    ```bash
    git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
    ~/.fzf/install
    ```
    *(Répondez "y" pour activer l'autocomplétion et les raccourcis clavier).*

## Procédure et Cas d'usage

Voici les utilisations les plus pratiques de `fzf` pour booster votre productivité quotidienne.

### 1. Recherche floue de fichiers (Usage basique)

La façon la plus simple d'utiliser `fzf` est de l'appeler directement dans un dossier.

```bash
fzf
```

Une liste interactive apparaît. Tapez quelques lettres (par exemple `conf ssh`) pour voir tous les fichiers contenant ces lettres, naviguez avec les flèches du clavier et appuyez sur ++enter++ pour valider. `fzf` retournera alors le chemin du fichier sélectionné.

### 2. Le raccourci magique pour l'historique : ++ctrl+r++

Si vous avez installé les raccourcis clavier (automatique avec la méthode Git, ou via l'ajout de `source /usr/share/doc/fzf/examples/key-bindings.bash` dans votre `.bashrc`), `fzf` remplace la recherche d'historique par défaut.

Appuyez sur :
++ctrl+r++

Plutôt que l'interface austère classique, une liste plein écran de votre historique de commandes s'affiche. Tapez des mots clés (ex: `docker run ubuntu`) pour filtrer instantanément, et validez avec ++enter++ pour copier la commande dans votre prompt actuel.

### 3. Trouver des fichiers et dossiers : ++ctrl+t++ et ++alt+c++

- **++ctrl+t++** : Insère automatiquement le chemin d'un fichier sélectionné via `fzf` à l'endroit actuel de votre curseur. 
  *Exemple : tapez `nano ` puis appuyez sur ++ctrl+t++, trouvez votre fichier, validez. La commande devient `nano /chemin/vers/le/fichier`.*

- **++alt+c++** : Permet de naviguer rapidement dans l'arborescence. Une fenêtre `fzf` s'ouvre avec la liste de tous les sous-dossiers. Sélectionnez-en un, et vous y ferez un `cd` automatique !

### 4. Combiner fzf avec d'autres commandes (Pipes)

La vraie puissance de `fzf` réside dans sa capacité à lire l'entrée standard (stdin). Vous pouvez chainer n'importe quelle commande avec `fzf`.

**Trouver un processus à tuer :**
```bash
ps aux | fzf | awk '{print $2}' | xargs kill -9
```
*Ici, on liste les processus, on filtre visuellement avec fzf, on extrait le PID (2ème colonne) et on le tue.*

**Naviguer dans les logs système :**
```bash
journalctl -u nginx | fzf
```

**Rechercher dans des paquets installés (ex: Debian/Ubuntu) :**
```bash
dpkg -l | fzf
```

## Aide-mémoire

| Action `fzf` | Description |
|--------------|-------------|
| ++ctrl+r++ | Recherche floue dans l'historique des commandes (remplace le comportement par défaut) |
| ++ctrl+t++ | Recherche de fichiers et injection du chemin dans la commande courante |
| ++alt+c++ | Recherche de dossier et commande `cd` automatique vers ce dossier |
| `cmd \| fzf` | Filtre interactif sur le résultat de n'importe quelle commande `cmd` |

## Ressources

- [Dépôt GitHub officiel de fzf](https://github.com/junegunn/fzf) — Documentation complète et options avancées.
- [Vim + fzf](https://github.com/junegunn/fzf.vim) — Intégration de fzf directement dans l'éditeur Vim.