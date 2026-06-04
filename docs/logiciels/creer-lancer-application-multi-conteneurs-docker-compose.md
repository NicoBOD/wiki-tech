---
title: Créer et lancer une application multi-conteneurs avec Docker Compose
date: 2026-06-04
author: Nicolas BODAINE
tags:
  - docker
  - docker-compose
  - devops
  - linux
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Créer et lancer une application multi-conteneurs avec Docker Compose

!!! abstract "Résumé"
    Après avoir installé Docker Engine, la prochaine étape logique est d'utiliser **Docker Compose**. Cet outil permet de définir et de lancer des applications composées de plusieurs conteneurs (par exemple, un serveur web et sa base de données) via un simple fichier de configuration en YAML. Ce tutoriel montre comment déployer une pile WordPress + MariaDB en quelques minutes.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 |
| Dernière mise à jour | 2026-06-04 |

## Contexte

Dans la pratique professionnelle (TSSR, administrations système), on déploie rarement un seul conteneur isolé. Les applications modernes nécessitent souvent une base de données, un backend, un frontend, un cache, etc. Lancer chaque conteneur manuellement avec de longues commandes `docker run` devient vite fastidieux et source d'erreurs.

**Docker Compose** résout ce problème en vous permettant de déclarer toute votre infrastructure dans un seul fichier : `docker-compose.yml`. Une seule commande suffit ensuite pour tout démarrer, interconnecter les conteneurs et configurer les volumes.

## Prérequis

- Une machine (ou VM) sous **Ubuntu 24.04**.
- Avoir suivi notre tutoriel pour [Installer Docker Engine et le plugin Docker Compose](installer-docker-engine-ubuntu-2404.md).
- Disposer des droits `sudo` ou être dans le groupe `docker`.

## Procédure

Dans ce laboratoire, nous allons déployer **WordPress** et **MariaDB**.

### Étape 1 : Créer le répertoire du projet

Il est de bonne pratique de dédier un dossier par projet Docker Compose.

```bash
mkdir -p ~/mon-projet-wordpress
cd ~/mon-projet-wordpress
```

### Étape 2 : Créer le fichier docker-compose.yml

Créez le fichier de déclaration de votre pile applicative à l'aide d'un éditeur de texte (comme `nano`).

```bash
nano docker-compose.yml
```

Insérez le contenu suivant :

```yaml title="docker-compose.yml"
services:
  db:
    image: mariadb:10.11
    container_name: wordpress_db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: motdepasseroot
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wp_user
      MYSQL_PASSWORD: wp_password
    volumes:
      - db_data:/var/lib/mysql

  wordpress:
    depends_on:
      - db
    image: wordpress:latest
    container_name: wordpress_app
    restart: always
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wp_user
      WORDPRESS_DB_PASSWORD: wp_password
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wp_data:/var/www/html

volumes:
  db_data:
  wp_data:
```

*Sauvegardez avec ++ctrl+o++, ++enter++, puis quittez avec ++ctrl+x++.*

### Étape 3 : Démarrer l'application

Lancez la création des volumes, le téléchargement des images et le démarrage des conteneurs avec l'option `-d` (détaché) pour laisser l'application tourner en arrière-plan.

```bash
docker compose up -d
```

!!! tip "Que se passe-t-il ?"
    Docker Compose crée automatiquement un réseau virtuel isolé pour que les deux conteneurs puissent communiquer. Le conteneur WordPress contacte la base de données simplement avec le nom de service `db`.

### Étape 4 : Suivre l'état des conteneurs

Vérifiez que vos deux conteneurs sont bien en cours d'exécution :

```bash
docker compose ps
```

Pour consulter les logs en temps réel (utile en cas de problème de connexion à la base de données) :

```bash
docker compose logs -f
```

## Vérification

1. Ouvrez votre navigateur web.
2. Allez sur l'adresse IP de votre serveur suivie du port **8080** : `http://IP_DE_VOTRE_SERVEUR:8080`
3. Vous devriez voir la page d'installation de WordPress.

!!! success "Résultat attendu"
    Si la page d'installation de WordPress s'affiche, cela confirme que le serveur web tourne correctement et qu'il a pu établir la communication avec le conteneur MariaDB !

## Aide-mémoire Docker Compose

| Commande | Description |
|----------|-------------|
| `docker compose up -d` | Démarre les services en arrière-plan |
| `docker compose ps` | Affiche l'état des conteneurs du projet actuel |
| `docker compose logs -f` | Affiche les journaux d'erreurs en direct |
| `docker compose down` | Arrête et supprime les conteneurs (et le réseau) |
| `docker compose down -v` | Arrête tout **et supprime les volumes de données** (Attention !) |

## Ressources

- [Documentation officielle Docker Compose](https://docs.docker.com/compose/) — Le guide officiel.
- [Docker Hub: WordPress](https://hub.docker.com/_/wordpress) — Image officielle et variables d'environnement.
