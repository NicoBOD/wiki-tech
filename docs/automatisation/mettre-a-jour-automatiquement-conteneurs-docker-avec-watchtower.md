---
title: Mettre à jour automatiquement ses conteneurs Docker avec Watchtower
date: 2026-06-10
author: Nicolas BODAINE
tags:
  - docker
  - watchtower
  - automatisation
  - mise-a-jour
difficulty: intermédiaire
os: Linux (Docker)
status: publié
---

# Mettre à jour automatiquement ses conteneurs Docker avec Watchtower

!!! abstract "Résumé"
    Maintenir ses conteneurs Docker à jour manuellement peut vite devenir fastidieux. Watchtower est un outil conçu pour automatiser ce processus : il surveille vos conteneurs en cours d'exécution et, lorsqu'une nouvelle image est disponible, il les recrée automatiquement avec la dernière version tout en conservant leur configuration.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux avec Docker |
| Dernière mise à jour | 2026-06-10 |

## Contexte

Dans une infrastructure reposant sur Docker, il est courant d'avoir de nombreux conteneurs en cours d'exécution. Les images de base évoluent pour corriger des failles de sécurité, ajouter des fonctionnalités ou améliorer les performances. Mettre à jour ces images manuellement implique de tirer la nouvelle image (`docker pull`), stopper l'ancien conteneur, le supprimer et le recréer avec les mêmes paramètres. Watchtower automatise tout ce flux de travail.

## Prérequis

- Un hôte sous Linux avec Docker et Docker Compose installés.
- Des conteneurs déjà en cours d'exécution que vous souhaitez maintenir à jour.

## Procédure

### Étape 1 : Lancement basique de Watchtower

La méthode la plus rapide pour utiliser Watchtower est de le lancer lui-même comme un conteneur Docker.

```bash
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower
```

!!! note "Explication"
    Watchtower a besoin d'accéder au socket Docker (`/var/run/docker.sock`) de l'hôte pour pouvoir interagir avec l'API Docker, vérifier les images et recréer les conteneurs.

Par défaut, cette commande vérifiera toutes les 24 heures si de nouvelles images sont disponibles pour **tous** les conteneurs en cours d'exécution.

### Étape 2 : Lancement avec Docker Compose (recommandé)

Pour une meilleure gestion, il est préférable d'utiliser un fichier `docker-compose.yml`.

Créez un dossier pour Watchtower et ajoutez-y le fichier :

```yaml title="docker-compose.yml"
services:
  watchtower:
    image: containrrr/watchtower
    container_name: watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      # Définit le fuseau horaire
      - TZ=Europe/Paris
      # Vérifie les mises à jour tous les jours à 04h00 du matin (format Cron)
      - WATCHTOWER_SCHEDULE=0 0 4 * * *
      # Supprime les anciennes images après la mise à jour pour libérer de l'espace
      - WATCHTOWER_CLEANUP=true
    restart: unless-stopped
```

Lancez ensuite le service :

```bash
docker compose up -d
```

### Étape 3 : Surveiller des conteneurs spécifiques

Par défaut, Watchtower surveille *tous* les conteneurs. Si vous hébergez des applications critiques qui nécessitent des mises à jour manuelles contrôlées, ce comportement peut être dangereux.

Vous pouvez indiquer à Watchtower de ne mettre à jour que certains conteneurs en ajoutant leur nom à la fin de la commande ou dans le fichier Compose.

Dans `docker-compose.yml` :
```yaml title="docker-compose.yml" hl_lines="13"
services:
  watchtower:
    image: containrrr/watchtower
    container_name: watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - TZ=Europe/Paris
      - WATCHTOWER_SCHEDULE=0 0 4 * * *
      - WATCHTOWER_CLEANUP=true
    restart: unless-stopped
    # Ne mettre à jour que ces deux conteneurs
    command: nginx-proxy portainer
```

**Alternativement (opt-out)** :
Vous pouvez laisser Watchtower surveiller tous les conteneurs par défaut, mais exclure spécifiquement un conteneur en lui ajoutant un label dédié.

Par exemple, lors du lancement d'une base de données critique avec `docker run` :
```bash
docker run -d --label=com.centurylinklabs.watchtower.enable=false ma-base-de-donnees
```

Ou dans un fichier `docker-compose.yml` de votre application :
```yaml title="docker-compose.yml" hl_lines="5 6"
services:
  db:
    image: postgres:15
    # ...
    labels:
      - "com.centurylinklabs.watchtower.enable=false"
```

## Vérification

Pour vérifier que Watchtower fonctionne et planifie correctement les mises à jour, consultez ses logs :

```bash
docker logs watchtower
```

!!! success "Résultat attendu"
    Vous devriez voir un message indiquant l'heure du prochain contrôle planifié (par exemple, à 4h du matin selon notre configuration Cron).
    `time="2026-06-10T..." level=info msg="Starting Watchtower and scheduling first run: 2026-06-11 04:00:00 +0200 CEST"`

## Ressources

- [Documentation officielle de Watchtower](https://containrrr.dev/watchtower/) — Documentation complète et exhaustive.
- [Docker Hub - Watchtower](https://hub.docker.com/r/containrrr/watchtower) — Dépôt de l'image Docker.