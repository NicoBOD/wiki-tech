---
title: Utiliser DBeaver pour explorer et administrer ses bases de données
date: 2026-07-01
author: Nicolas BODAINE
tags:
  - bdd
  - dbeaver
  - sql
  - outil
difficulty: débutant
os: Linux | Windows | macOS
status: publié
---

# Utiliser DBeaver pour explorer et administrer ses bases de données

!!! abstract "Résumé"
    DBeaver est un outil graphique universel de gestion de bases de données, gratuit et open source. Il permet de se connecter à presque tous les moteurs du marché (PostgreSQL, MySQL, SQLite, Oracle, SQL Server, etc.), d'exécuter des requêtes SQL et d'explorer visuellement la structure et les données. Ce tutoriel vous guide pour l'installer et créer votre première connexion.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Multi-plateforme (Linux, Windows, macOS) |
| Dernière mise à jour | 2026-07-01 |

## Contexte

Dans le cadre de l'administration système, du développement web ou du support applicatif, il est très fréquent de devoir interagir avec une base de données. Plutôt que d'utiliser de multiples outils en ligne de commande (`psql`, `mysql`, etc.) ou de dépendre des interfaces spécifiques à chaque moteur (comme phpMyAdmin ou pgAdmin), un client lourd universel permet de centraliser la gestion de toutes vos connexions.

DBeaver est basé sur Java (Eclipse) et utilise des pilotes JDBC pour se connecter aux moteurs. Son grand avantage : il télécharge automatiquement les pilotes nécessaires lorsque vous vous connectez à un nouveau type de base de données.

## Prérequis

- Une machine de travail (Windows, Linux ou macOS).
- Les accès (IP, port, nom de la base, utilisateur et mot de passe) vers une base de données fonctionnelle (ou une base locale pour s'entraîner).
- Une connexion Internet pour que DBeaver puisse télécharger les pilotes JDBC.

## Procédure

### Étape 1 : Installation de DBeaver Community

DBeaver est disponible en version *Community* (gratuite et open source) ou *PRO* (payante). Pour la grande majorité des usages (notamment avec les bases relationnelles), la version Community est suffisante.

=== "Windows"

    Téléchargez l'installateur sur le [site officiel de DBeaver](https://dbeaver.io/download/) et lancez le `.exe`. Vous pouvez également l'installer via **Winget** :
    ```powershell
    winget install dbeaver.dbeaver
    ```

=== "Linux (Ubuntu / Debian)"

    Il est possible de l'installer via un fichier `.deb`, ou via Flatpak ou Snap (qui est souvent la méthode la plus simple sur Ubuntu) :
    ```bash
    sudo snap install dbeaver-ce
    ```

=== "macOS"

    Si vous utilisez Homebrew, vous pouvez l'installer avec la commande suivante :
    ```bash
    brew install --cask dbeaver-community
    ```

### Étape 2 : Créer une première connexion

Lors du premier lancement de DBeaver, il peut vous proposer un projet par défaut.

1. Cliquez sur l'icône **Nouvelle Connexion** en haut à gauche (elle ressemble à une prise électrique avec un `+`).
2. Une liste de bases de données s'affiche. Choisissez le type de base auquel vous souhaitez vous connecter (par exemple, **PostgreSQL** ou **MySQL** / **MariaDB**). Cliquez sur **Suivant**.
3. Remplissez les informations de connexion :
    - **Hôte** : L'adresse IP ou le nom d'hôte de la base (par défaut `localhost` ou `127.0.0.1` pour une base locale).
    - **Port** : Le port par défaut est généralement prérempli (ex: 5432 pour PostgreSQL, 3306 pour MySQL).
    - **Base de données** / **Database** : Le nom de la base à laquelle se connecter.
    - **Nom d'utilisateur** et **Mot de passe** : Vos identifiants de connexion.
4. Cliquez sur **Test de connexion...** en bas à gauche.
    - Si c'est la première fois que vous utilisez ce type de base, DBeaver vous demandera l'autorisation de **télécharger les pilotes JDBC** nécessaires. Acceptez (cliquez sur *Download*).
    - Si la connexion réussit, un message de succès s'affichera. S'il y a une erreur (connexion refusée, identifiants incorrects), vérifiez vos paramètres et l'état de votre serveur.
5. Cliquez sur **Terminer** pour valider.

### Étape 3 : Explorer et modifier les données

Votre nouvelle connexion apparaît maintenant dans le panneau de gauche (**Navigateur de base de données**).

1. Déroulez l'arborescence (cliquez sur la petite flèche) pour voir les **Bases de données**, puis les **Schémas**, puis les **Tables**.
2. Double-cliquez sur une table pour l'ouvrir. Vous verrez alors deux onglets principaux dans la fenêtre centrale :
    - **Propriétés** : Pour voir la structure de la table (les colonnes, les types de données, les contraintes, les clés étrangères).
    - **Données** : Pour afficher le contenu sous forme de tableur.
3. Depuis l'onglet **Données**, vous pouvez directement modifier une cellule, ajouter une nouvelle ligne (avec les icônes en bas de l'écran) ou en supprimer une.
    !!! warning "Attention à l'enregistrement"
        Toute modification visuelle ne modifie pas immédiatement la base. Vous devez cliquer sur le bouton **Enregistrer** (l'icône `Save` en bas) pour exécuter les requêtes `UPDATE` ou `INSERT` générées par vos actions, ou annuler avec **Revert**.

### Étape 4 : Exécuter des requêtes SQL personnalisées

Bien que l'exploration visuelle soit pratique, l'écriture de scripts SQL est souvent indispensable.

1. Sélectionnez votre connexion dans l'arborescence, puis cliquez sur le bouton **Éditeur SQL** (icône représentant un parchemin avec un crayon, ou raccourci ++ctrl+enter++ et "Nouveau script SQL").
2. Tapez votre requête, par exemple :
   ```sql
   SELECT * FROM utilisateurs WHERE statut = 'actif';
   ```
3. Exécutez la requête avec le raccourci ++ctrl+enter++ (ou le bouton `Execute SQL Statement` avec l'icône de lecture verte).
4. Le résultat s'affichera dans le panneau inférieur.

## Checklist

- [x] L'outil est installé sur la machine de travail.
- [x] La connexion au serveur de base de données est configurée.
- [x] Les pilotes JDBC ont été téléchargés avec succès.
- [x] Vous savez explorer les tables et ouvrir une vue SQL.

## Ressources

- [Site officiel DBeaver](https://dbeaver.io/) — Pour télécharger le logiciel et consulter la documentation.
- [Documentation DBeaver (Wiki)](https://github.com/dbeaver/dbeaver/wiki) — Guide d'utilisation détaillé (en anglais).
