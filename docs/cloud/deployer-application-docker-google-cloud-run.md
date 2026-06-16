---
title: Déployer une application Docker sans serveur avec Google Cloud Run
date: 2026-06-16
author: Nicolas BODAINE
tags:
  - gcp
  - docker
  - cloud-run
  - serverless
difficulty: intermédiaire
os: Linux
status: publié
---

# Déployer une application Docker sans serveur avec Google Cloud Run

!!! abstract "Résumé"
    Ce tutoriel explique comment déployer un conteneur Docker sur Google Cloud Run, un environnement d'exécution sans serveur (serverless). Cela permet de faire tourner une application sans avoir à gérer l'infrastructure sous-jacente.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux / Google Cloud Platform |
| Dernière mise à jour | 2026-06-16 |

## Contexte

La gestion de serveurs virtuels (VM) peut s'avérer fastidieuse (mises à jour, sécurité, dimensionnement). Google Cloud Run permet d'exécuter des conteneurs Docker en mode serverless. La plateforme gère automatiquement l'infrastructure, la mise à l'échelle (scale-to-zero y compris), et le routage HTTP. C'est idéal pour des API, des backends ou des sites web légers.

## Prérequis

- Un compte [Google Cloud Platform (GCP)](https://cloud.google.com/) avec un projet actif.
- La facturation activée sur ce projet (GCP propose un niveau gratuit très généreux pour Cloud Run).
- Le [Google Cloud SDK (`gcloud`)](https://cloud.google.com/sdk/docs/install) installé sur votre machine locale.
- Docker installé en local (optionnel si vous utilisez Google Cloud Build, mais recommandé pour tester).

## Procédure

### Étape 1 : S'authentifier et configurer le projet

Ouvrez un terminal et connectez-vous à votre compte Google Cloud, puis sélectionnez votre projet.

```bash
# Se connecter à GCP
gcloud auth login

# Lier le terminal à votre projet (remplacez ID_DU_PROJET)
gcloud config set project ID_DU_PROJET

# Activer l'API Cloud Run et Artifact Registry
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

### Étape 2 : Préparer l'application et le Dockerfile

Nous allons créer une application web minimaliste en Python (Flask).
Créez un dossier pour votre projet et ajoutez-y trois fichiers.

=== "app.py"

    ```python title="app.py"
    import os
    from flask import Flask

    app = Flask(__name__)

    @app.route("/")
    def hello():
        return "Bonjour depuis Cloud Run !"

    if __name__ == "__main__":
        # Cloud Run utilise la variable d'environnement PORT (par défaut 8080)
        port = int(os.environ.get("PORT", 8080))
        app.run(debug=True, host="0.0.0.0", port=port)
    ```

=== "requirements.txt"

    ```text title="requirements.txt"
    Flask==3.0.0
    gunicorn==21.2.0
    ```

=== "Dockerfile"

    ```dockerfile title="Dockerfile"
    # Utiliser une image Python officielle légère
    FROM python:3.12-slim

    # Définir le répertoire de travail
    WORKDIR /app

    # Copier les fichiers de dépendances et les installer
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # Copier le code de l'application
    COPY app.py .

    # Commande de démarrage
    CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
    ```

### Étape 3 : Créer un dépôt Artifact Registry

Cloud Run a besoin d'accéder à l'image Docker de votre application. Nous allons utiliser Artifact Registry pour stocker l'image.

```bash
# Créer un dépôt nommé "mon-repo-docker" dans la région europe-west1 (Belgique/France)
gcloud artifacts repositories create mon-repo-docker \
    --repository-format=docker \
    --location=europe-west1 \
    --description="Dépôt pour mes images Docker"
```

### Étape 4 : Construire et pousser l'image Docker

Plutôt que de compiler l'image en local, nous pouvons confier cette tâche à **Google Cloud Build**, qui la poussera directement dans le registre. Assurez-vous d'être dans le dossier contenant le `Dockerfile`.

```bash
# Construire et pousser l'image dans Artifact Registry
gcloud builds submit --tag europe-west1-docker.pkg.dev/ID_DU_PROJET/mon-repo-docker/mon-app-flask
```

!!! tip "Astuce"
    Si vous préférez compiler en local, utilisez `docker build -t ...` puis `docker push ...` après avoir configuré Docker pour qu'il s'authentifie auprès d'Artifact Registry avec `gcloud auth configure-docker europe-west1-docker.pkg.dev`.

### Étape 5 : Déployer sur Cloud Run

Maintenant que l'image est hébergée, nous pouvons la déployer sur Cloud Run.

```bash
gcloud run deploy mon-service-flask \
    --image europe-west1-docker.pkg.dev/ID_DU_PROJET/mon-repo-docker/mon-app-flask \
    --region europe-west1 \
    --allow-unauthenticated
```

Le paramètre `--allow-unauthenticated` rend l'application accessible publiquement (sur internet) sans nécessiter d'authentification IAM.

## Vérification

Une fois la commande `gcloud run deploy` terminée, le terminal affichera une **URL publique** (se terminant par `.run.app`).

```bash
# Exemple de sortie attendue :
# Service [mon-service-flask] revision [mon-service-flask-00001-abc] has been deployed and is serving 100 percent of traffic.
# Service URL: https://mon-service-flask-abcdefgh-ew.a.run.app
```

Ouvrez cette URL dans votre navigateur web ou utilisez `curl` pour vérifier que l'application répond :

```bash
curl https://mon-service-flask-abcdefgh-ew.a.run.app
# Résultat attendu : Bonjour depuis Cloud Run !
```

!!! success "Succès"
    Votre application est désormais en ligne ! Elle passera à 0 instance (scale-to-zero) si personne ne s'y connecte, ce qui permet de ne rien payer lorsque l'application est inactive.

## Ressources

- [Documentation officielle Google Cloud Run](https://cloud.google.com/run/docs) — Déploiement et gestion des services
- [Guide de démarrage Artifact Registry](https://cloud.google.com/artifact-registry/docs)
- [Optimiser les conteneurs pour Cloud Run](https://cloud.google.com/run/docs/tips/general)