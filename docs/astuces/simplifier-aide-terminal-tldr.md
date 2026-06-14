---
title: "Simplifier l'aide dans le terminal : utiliser tldr au lieu des pages man"
date: 2026-06-14
author: Nicolas BODAINE
tags:
  - astuce
  - terminal
  - linux
  - cli
  - productivité
difficulty: débutant
os: Linux | macOS | Windows
status: publié
---

# Simplifier l'aide dans le terminal : utiliser tldr au lieu des pages man

!!! abstract "Résumé"
    Les pages `man` sont très complètes mais souvent trop denses et difficiles à lire rapidement. L'outil `tldr` (Too Long; Didn't Read) propose des exemples pratiques et concis pour les commandes en ligne de commande. Ce tutoriel montre comment l'installer et l'utiliser pour gagner du temps au quotidien.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux / macOS / Windows |
| Dernière mise à jour | 2026-06-14 |

## Contexte

Vous êtes face à une commande que vous n'avez pas utilisée depuis un moment (comme `tar`, `find` ou `curl`). Vous tapez `man tar` pour retrouver la syntaxe exacte, mais vous vous retrouvez face à un long document expliquant chaque drapeau dans les moindres détails. Vous perdez du temps à chercher l'exemple de base dont vous avez besoin pour simplement décompresser une archive. 

Le projet **tldr-pages** a été créé pour résoudre ce problème : il s'agit d'un ensemble de pages d'aide communautaires simplifiées, axées sur les cas d'usage réels et fréquents, présentées sous forme d'exemples faciles à copier-coller.

## Procédure

### Étape 1 : Installer tldr

Plusieurs implémentations de `tldr` existent. La plus commune est basée sur Node.js ou Python, mais de nombreuses distributions proposent un client rapide natif (en C ou Rust).

=== "Debian / Ubuntu"

    Sur les systèmes basés sur Debian/Ubuntu, le paquet s'appelle `tldr`.

    ```bash
    sudo apt update
    sudo apt install tldr
    ```

=== "Arch Linux"

    ```bash
    sudo pacman -S tldr
    ```

=== "macOS (Homebrew)"

    ```bash
    brew install tldr
    ```

=== "NPM / Node.js"

    Si vous avez Node.js installé, vous pouvez utiliser l'implémentation officielle (qui fonctionne sur Windows également).

    ```bash
    npm install -g tldr
    ```

=== "Python / pip"

    ```bash
    pip install tldr
    ```

### Étape 2 : Mettre à jour le cache local

La plupart des clients `tldr` nécessitent de télécharger le catalogue des pages localement la première fois, ou pour avoir la dernière version des exemples.

```bash
tldr --update
```

*Note : Certaines implémentations, comme `tealdeer` (souvent installable sous le nom `tldr` ou `tealdeer`), se mettent à jour avec `tldr --update` ou font cette mise à jour automatiquement.*

### Étape 3 : Utiliser tldr

Pour obtenir de l'aide sur une commande, il suffit de taper `tldr` suivi du nom de la commande.

Essayons avec `tar` :

```bash
tldr tar
```

!!! example "Résultat de tldr tar"
    L'outil affichera une liste colorée d'exemples pratiques, comme :

    - Extraire une archive (fichier compressé) :
      `tar xf {{chemin/vers/archive.tar}}`
    
    - Extraire une archive compressée au format gzip :
      `tar xzf {{chemin/vers/archive.tar.gz}}`
    
    - Créer une archive gzip compressée :
      `tar czf {{chemin/vers/archive.tar.gz}} {{chemin/vers/fichier_ou_dossier1 chemin/vers/fichier_ou_dossier2 ...}}`

C'est concis, droit au but, et couvre 90% des usages quotidiens. Si vous avez besoin d'une information très pointue, vous pourrez toujours vous rabattre sur `man tar`.

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `tldr <commande>` | Affiche les exemples pratiques pour la commande demandée |
| `tldr --update` (ou `-u`) | Met à jour le cache local des pages d'aide |
| `tldr --list` | Liste toutes les commandes pour lesquelles une page tldr existe |
| `tldr -l <langue> <commande>` | Affiche la page dans une langue spécifique (ex: `-l fr` si disponible) |

## Ressources

- [Site officiel du projet tldr-pages](https://tldr.sh/) — Pour consulter les pages en ligne (web) ou découvrir d'autres clients.
- [Dépôt GitHub tldr-pages](https://github.com/tldr-pages/tldr) — Pour contribuer et ajouter vos propres exemples aux pages d'aide.