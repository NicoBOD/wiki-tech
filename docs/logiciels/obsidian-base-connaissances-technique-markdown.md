---
title: "Obsidian : Créer et organiser sa propre base de connaissances technique en Markdown"
date: 2026-06-21
author: Nicolas BODAINE
tags:
  - markdown
  - documentation
  - productivite
  - git
difficulty: débutant
os: Multi-plateforme
status: publié
---

# Obsidian : Créer et organiser sa propre base de connaissances technique en Markdown

!!! abstract "Résumé"
    Apprenez à utiliser Obsidian, un outil de prise de notes puissant reposant entièrement sur des fichiers Markdown locaux, pour construire votre propre base de connaissances technique (PKM). Idéal pour documenter vos TP, vos astuces et vos projets sans dépendre d'un service cloud propriétaire.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Windows, Linux, macOS |
| Dernière mise à jour | 2026-06-21 |

## Contexte

En tant qu'étudiant ou professionnel de l'informatique, vous accumulez une quantité massive d'informations : commandes utiles, erreurs rencontrées, procédures de dépannage, notes de cours. S'appuyer sur sa mémoire, des post-its ou des documents Word éparpillés montre rapidement ses limites. 

**Obsidian** est un éditeur de texte spécialisé dans la gestion des connaissances. Contrairement à Notion ou Evernote, vos notes vous appartiennent : elles sont stockées localement sur votre machine au format standardisé Markdown (`.md`). Si Obsidian disparaît demain, vos notes restent lisibles par n'importe quel éditeur de texte.

## Prérequis

- Avoir téléchargé et installé Obsidian depuis [le site officiel (obsidian.md)](https://obsidian.md/).
- (Optionnel mais recommandé) Avoir Git installé pour versionner et sauvegarder sa base de connaissances.

## Procédure

### Étape 1 : Créer son "Vault" (Coffre-fort)

Un "Vault" dans Obsidian n'est rien d'autre qu'un dossier sur votre ordinateur qui contiendra tous vos fichiers Markdown et vos images.

1. Lancez Obsidian.
2. Cliquez sur **Create new vault** (Créer un nouveau coffre).
3. Nommez-le, par exemple `BaseDeConnaissances` ou `IT-Brain`.
4. Choisissez l'emplacement sur votre disque dur (ex: `~/Documents/IT-Brain`).
5. Cliquez sur **Create**.

L'interface principale s'ouvre, vous pouvez directement créer votre première note avec ++ctrl+n++.

### Étape 2 : Comprendre les concepts clés (Markdown et Liens bidirectionnels)

Toute votre documentation se fait en syntaxe Markdown classique (titres avec `#`, listes avec `-`, code avec les backticks `` ` ``).

La véritable puissance d'Obsidian réside dans ses **liens bidirectionnels**. Vous pouvez lier des concepts entre eux instantanément avec la syntaxe `[[Nom de la note]]`.

Créez par exemple une note `Docker` :
```markdown
# Docker
Docker est une plateforme de conteneurisation. 
Pour l'installer sous Ubuntu, voir la procédure d'[[Installation Docker Ubuntu]].
```
En cliquant sur le lien `[[Installation Docker Ubuntu]]`, Obsidian créera automatiquement cette nouvelle note si elle n'existe pas encore. Au fil du temps, vous constituez un véritable réseau de connaissances techniques (visible via la fonctionnalité "Graph view" de l'application).

### Étape 3 : Organiser ses notes (Dossiers vs Tags)

Inutile de créer des arborescences de dossiers trop profondes. Obsidian excelle dans la recherche et les liens. Une structure simple suffit :

- `📁 Projets` (Pour vos TP, stages, missions en cours)
- `📁 Ressources` (Commandes, snippets, tutos)
- `📁 Journal` (Pour vos notes quotidiennes)
- `📁 Fichiers` (Pour ranger automatiquement les images collées)

Utilisez les **tags** (ex: `#linux`, `#reseau`, `#python`) à l'intérieur de vos notes pour les regrouper par thématique, quelle que soit leur position dans les dossiers.

### Étape 4 : Activer les notes quotidiennes (Daily notes)

Très utile en entreprise ou en TP pour garder une trace de ce que vous avez fait ou cherché.

1. Allez dans les paramètres d'Obsidian (++ctrl+,++ ou l'icône engrenage).
2. Dans le menu de gauche, sous **Core plugins**, trouvez et activez **Daily notes**.
3. Vous avez maintenant un bouton dans le menu de gauche (une icône de calendrier) permettant de créer instantanément une note à la date du jour. 
4. Vous pouvez y documenter : *Ce que j'ai testé aujourd'hui*, *L'erreur rencontrée sur le serveur web*, etc.

### Étape 5 : Sauvegarder et versionner avec Git (Idéal pour les profils Tech)

Puisque votre Vault n'est qu'un dossier de fichiers texte, la meilleure façon de le sauvegarder et de le synchroniser entre plusieurs PC est d'utiliser Git !

=== "Terminal (Linux/Mac/Windows)"

    ```bash
    # Se placer dans le dossier du Vault
    cd ~/Documents/IT-Brain
    
    # Initialiser le dépôt
    git init
    
    # Ajouter le dossier cache d'Obsidian au .gitignore pour ne pas le polluer
    echo ".obsidian/workspace" >> .gitignore
    echo ".obsidian/workspace.json" >> .gitignore
    
    # Ajouter et commit ses notes
    git add .
    git commit -m "docs: sauvegarde initiale de la base de connaissances"
    ```

Vous pouvez ensuite pousser (push) ce dépôt sur un repo privé GitHub ou GitLab.
Il existe également un plugin communautaire nommé `Obsidian Git` qui automatise ce processus (commit automatique toutes les X minutes, push/pull automatiques à l'ouverture/fermeture d'Obsidian).

## Ressources

- [Documentation officielle d'Obsidian](https://help.obsidian.md/) — Le guide officiel.
- [Obsidian Git Plugin](https://github.com/denolehov/obsidian-git) — Le plugin pour automatiser ses sauvegardes via Git.
- [Markdown Guide](https://www.markdownguide.org/basic-syntax/) — Rappel de la syntaxe de base.
