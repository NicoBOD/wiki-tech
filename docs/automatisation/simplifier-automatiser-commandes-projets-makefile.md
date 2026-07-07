---
title: Simplifier et automatiser les commandes de ses projets avec un Makefile
date: 2026-06-23
author: Nicolas BODAINE
tags:
  - Makefile
  - Automatisation
  - Outils
  - Productivité
difficulty: débutant
os: Linux | macOS | Windows (WSL)
status: publié
---

# Simplifier et automatiser les commandes de ses projets avec un Makefile

!!! abstract "Résumé"
    Bien que conçu à l'origine pour compiler du code C, **Make** est un formidable outil pour regrouper, documenter et automatiser toutes les commandes récurrentes de vos projets (lancement de conteneurs Docker, exécution de tests, déploiement...). Fini les fichiers `readme.md` avec des commandes de trois lignes à copier-coller : un simple `make start` suffit !

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux, macOS, WSL |
| Dernière mise à jour | 2026-06-23 |

## Contexte

Dans la plupart des projets informatiques modernes (développement, infrastructure as code, data science), on accumule rapidement des commandes complexes :
- Démarrer l'environnement : `docker compose -f docker-compose.yml up -d`
- Lancer les tests : `pytest --cov=src tests/`
- Nettoyer les caches : `find . -type d -name "__pycache__" -exec rm -rf {} +`

Plutôt que d'écrire des scripts bash individuels ou de documenter ces commandes pour que les nouveaux membres de l'équipe les tapent manuellement, on peut utiliser un **Makefile** à la racine du projet. 

## Prérequis

- L'outil `make` installé sur votre système :
    - **Ubuntu/Debian** : `sudo apt update && sudo apt install make`
    - **CentOS/RHEL** : `sudo dnf install make`
    - **Windows** : Utiliser WSL (Windows Subsystem for Linux) ou Git Bash.

## Principes de base

Un `Makefile` est un simple fichier texte (nommé `Makefile` avec un "M" majuscule) qui contient des "règles". Chaque règle est structurée de la façon suivante :

```makefile
cible: dependances
	commande
```

!!! danger "Attention aux tabulations"
    Dans un fichier Makefile, l'indentation avant une commande **doit obligatoirement être une tabulation** (touche `Tab` du clavier), et non des espaces. Si vous mettez des espaces, `make` renverra l'erreur `*** missing separator. Stop.`.

## Procédure

### Étape 1 : Créer votre premier Makefile

Placez-vous dans le dossier de votre projet et créez un fichier nommé `Makefile`.

```bash
cd /chemin/vers/votre/projet
touch Makefile
```

### Étape 2 : Ajouter des cibles simples

Ouvrez le fichier dans votre éditeur (VS Code, nano, vim) et ajoutez vos premières commandes. Par exemple, pour un projet utilisant Docker :

```makefile title="Makefile"
up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f
```

### Étape 3 : Exécuter une commande

Dans votre terminal, il suffit maintenant de taper `make` suivi du nom de la cible :

```bash
make up
make logs
```

Si vous tapez juste `make`, l'outil exécutera **la première cible** du fichier par défaut.

### Étape 4 : Déclarer les cibles ".PHONY"

Si par hasard vous avez un fichier nommé `up` ou `logs` dans votre dossier, `make` croira que la cible est "à jour" et n'exécutera pas la commande.
Pour indiquer que vos cibles ne sont pas des noms de fichiers à générer (mais juste des raccourcis de commandes), ajoutez la ligne spéciale `.PHONY` en haut du fichier :

```makefile title="Makefile"
.PHONY: up down logs

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f
```

### Étape 5 : Utiliser des variables

Pour rendre votre Makefile plus lisible et facile à modifier, vous pouvez utiliser des variables.

```makefile title="Makefile"
.PHONY: install clean deploy

PYTHON=python3
ENV_DIR=venv

install:
	$(PYTHON) -m venv $(ENV_DIR)
	./$(ENV_DIR)/bin/pip install -r requirements.txt

clean:
	rm -rf $(ENV_DIR)
	rm -rf .pytest_cache
```

Pour utiliser la variable, on l'entoure de parenthèses précédées d'un dollar : `$(NOM_VARIABLE)`.

### Étape 6 : Documenter automatiquement le Makefile (Astuce avancée)

Une excellente pratique consiste à ajouter une cible `help` pour que n'importe qui puisse lister les commandes disponibles en tapant `make help`.

```makefile title="Makefile"
.PHONY: help up down

# Cible par défaut lorsqu'on tape juste "make"
.DEFAULT_GOAL := help

help:
	@echo "Commandes disponibles :"
	@echo "  make up    - Démarre l'environnement de développement"
	@echo "  make down  - Arrête et supprime les conteneurs"

up:
	docker compose up -d

down:
	docker compose down
```

!!! tip "Le symbole @"
    Placer un `@` devant une commande empêche `make` d'afficher la commande elle-même dans le terminal avant de l'exécuter. Cela rend la sortie plus propre.

## Vérification

Pour vérifier que votre Makefile fonctionne correctement, exécutez la commande `make` (qui devrait appeler la cible par défaut, ici `help`) :

```bash
make
```

!!! success "Résultat attendu"
    ```text
    Commandes disponibles :
      make up    - Démarre l'environnement de développement
      make down  - Arrête et supprime les conteneurs
    ```

## Ressources

- [GNU Make - Documentation officielle](https://www.gnu.org/software/make/manual/make.html) — Référence exhaustive.
- [Alerte "Missing separator" expliquée](https://stackoverflow.com/questions/16931770/makefile4-missing-separator-stop) — L'erreur la plus commune des débutants.