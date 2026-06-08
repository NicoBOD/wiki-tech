---
title: Créer son premier pipeline CI/CD avec GitHub Actions
date: 2026-06-08
author: Nicolas BODAINE
tags:
  - cicd
  - github
  - devops
  - git
difficulty: débutant
os: Indépendant
status: publié
---

# Créer son premier pipeline CI/CD avec GitHub Actions

!!! abstract "Résumé"
    Découvrez comment automatiser vos tâches de test et de déploiement directement depuis votre dépôt de code grâce à GitHub Actions. Nous allons créer un pipeline simple qui vérifiera la qualité du code à chaque modification.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Indépendant (Cloud) |
| Dernière mise à jour | 2026-06-08 |

## Contexte

Dans le développement logiciel et l'administration système moderne, on utilise l'**Intégration Continue (CI)** pour vérifier automatiquement le code à chaque modification, et le **Déploiement Continu (CD)** pour le mettre en production.

**GitHub Actions** est la solution native de GitHub pour exécuter ces workflows (pipelines). Il ne nécessite aucune infrastructure supplémentaire à maintenir (comme Jenkins), puisque les tâches sont exécutées directement sur des serveurs temporaires (runners) hébergés par GitHub.

L'objectif de ce tutoriel est de mettre en place un pipeline CI simple pour un projet Python qui :

1. Se déclenche à chaque fois qu'un code est poussé (push) sur le dépôt.
2. Configure l'environnement Python.
3. Installe les dépendances.
4. Exécute les tests automatiques.

## Prérequis

- Un compte GitHub.
- Un dépôt contenant un projet basique (pour l'exemple, nous utiliserons un script Python et un fichier de test).
- Les bases de Git (`git add`, `git commit`, `git push`).

## Procédure

### Étape 1 : Préparer un projet de test

Si vous n'avez pas de projet sous la main, créez un petit script Python et son test. Dans la racine de votre dépôt local, créez :

```python title="calculatrice.py"
def addition(a, b):
    return a + b
```

```python title="test_calculatrice.py"
from calculatrice import addition

def test_addition():
    assert addition(2, 3) == 5
    assert addition(-1, 1) == 0
```

Créez également un fichier de dépendances :

```text title="requirements.txt"
pytest==8.0.0
```

Poussez (push) ces fichiers sur votre dépôt GitHub.

### Étape 2 : Créer le fichier de workflow

GitHub Actions lit les instructions depuis des fichiers YAML placés dans un répertoire spécifique de votre dépôt : `.github/workflows/`.

1. À la racine de votre projet local, créez les dossiers `.github` puis `workflows`.
2. Créez un fichier nommé `ci.yml` à l'intérieur.

```bash
mkdir -p .github/workflows
touch .github/workflows/ci.yml
```

### Étape 3 : Configurer le pipeline (le fichier YAML)

Ouvrez le fichier `.github/workflows/ci.yml` et insérez le code suivant :

```yaml title=".github/workflows/ci.yml"
name: Pipeline CI Python

# 1. Déclencheurs (quand exécuter ce pipeline ?)
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

# 2. Les tâches (jobs)
jobs:
  tester-code:
    # 3. L'environnement d'exécution (runner)
    runs-on: ubuntu-latest

    # 4. Les étapes (steps)
    steps:
      # Étape A : Récupérer le code source du dépôt
      - name: Checkout du code
        uses: actions/checkout@v4

      # Étape B : Installer la version de Python souhaitée
      - name: Configuration de Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      # Étape C : Installer les dépendances
      - name: Installation des dépendances
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      # Étape D : Lancer les tests
      - name: Exécution des tests avec pytest
        run: |
          pytest
```

**Explications :**

- `on`: Définit les évènements déclencheurs. Ici, le workflow démarre lors d'un push ou d'une pull request vers la branche `main`.
- `runs-on`: Indique le système d'exploitation du runner. `ubuntu-latest` est le plus courant et le plus rapide.
- `uses`: Permet d'appeler des "actions" pré-conçues par la communauté ou GitHub (comme cloner le dépôt ou installer Python).
- `run`: Permet d'exécuter des commandes shell classiques sur le runner.

### Étape 4 : Déployer et observer

1. Ajoutez le workflow, commitez et poussez les changements vers GitHub :

```bash
git add .github/workflows/ci.yml
git commit -m "ci: ajout du workflow github actions"
git push origin main
```

2. Rendez-vous sur la page de votre dépôt sur le site GitHub.
3. Cliquez sur l'onglet **Actions** en haut.
4. Vous devriez voir votre workflow "Pipeline CI Python" en cours d'exécution (ou déjà terminé). Cliquez dessus pour voir les détails de chaque étape et les logs.

## Vérification

Une fois l'exécution terminée dans l'onglet **Actions** de GitHub :

!!! success "Résultat attendu"
    Vous devez voir une coche verte (:material-check-circle: en vert) indiquant que le pipeline s'est terminé avec succès. Les logs du job `tester-code` montreront que l'étape `pytest` a bien trouvé et validé le test.

Si vous modifiez `calculatrice.py` pour introduire une erreur (par exemple `return a - b`) et que vous poussez le code, le pipeline échouera et une croix rouge (:material-close-circle:) apparaîtra. Vous recevrez également un e-mail d'alerte, vous avertissant que le code n'est pas fonctionnel.

## Ressources

- [Documentation officielle GitHub Actions](https://docs.github.com/fr/actions) — Guide complet, concepts de base et références.
- [GitHub Marketplace (Actions)](https://github.com/marketplace?type=actions) — Catalogue des actions communautaires réutilisables.
