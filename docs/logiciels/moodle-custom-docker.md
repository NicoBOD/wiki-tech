---
title: Migration et sécurisation de Moodle sous Docker
date: 2026-06-24
author: Nicolas BODAINE
tags:
  - Docker
  - Moodle
  - Coolify
  - PHP
  - Sécurité
difficulty: intermédiaire
os: Debian 13
status: publié
---

!!! abstract "Résumé"
    Ce guide documente la migration d'une instance Moodle en production (historiquement sous image Bitnami obsolète) vers une image Docker personnalisée, sécurisée et sans état (*stateless*) basée sur l'image Apache/PHP officielle. Il détaille également l'intégration de cette pile autonome dans l'interface de Coolify, la mise à niveau de la base de données vers MariaDB 12, l'installation sécurisée de plugins personnalisés via le processus de build, ainsi que les erreurs courantes à éviter.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Debian 13 (Trixie) / Coolify v4 |
| Dernière mise à jour | 2026-06-24 |

---

## Contexte

Pendant de nombreuses années, Bitnami a fourni des images Docker prêtes à l'emploi pour Moodle. Cependant, Bitnami a cessé de publier et de maintenir ces images (figées à la version 5.0.2). Pour des raisons évidentes de **sécurité** et de **pérennité applicative**, il était impératif de migrer vers une solution alternative stable et maintenable.

La solution mise en place repose sur :
1. Une **image Docker sur-mesure** basée sur l'image officielle `php:8.2-apache`.
2. Une **sécurisation stricte** : le code PHP de l'application est figé en lecture seule dans l'image.
3. Un **orchestrateur de production** : la pile est déclarée sous forme de service Docker Compose autonome et gérée depuis l'interface web de **Coolify** pour simplifier la supervision, la sauvegarde et les redémarrages.

---

## Architecture de la Solution

```
┌────────────────────────────────────────────────────────┐
│                   Reverse Proxy (Traefik)              │
└───────────────────────────┬────────────────────────────┘
                            │ (Port 80, Réseau: traefik-moodle)
                            ▼
┌────────────────────────────────────────────────────────┐
│             Conteneur moodle-custom-app                │
│                                                        │
│  - Code PHP en Lecture Seule (/var/www/html) -> root   │
│  - Config (/var/www/html/config.php) -> www-data       │
│  - Démon Cron en tâche de fond (toutes les minutes)    │
└───────────────────────────┬────────────────────────────┘
                            │ (Port 3306, Réseau: db)
                            ▼
┌────────────────────────────────────────────────────────┐
│              Conteneur moodle-custom-db                │
│                                                        │
│  - MariaDB 12 (Bitnami)                                │
│  - Persistance Physique (hk1pkqqots65e6occy3wfmhn_db)  │
└────────────────────────────────────────────────────────┘
```

---

## Prérequis

- Docker et Docker Compose installés sur le serveur hôte.
- Volumes Docker existants de l'ancien déploiement Moodle Bitnami :
  - `hk1pkqqots65e6occy3wfmhn_db` (données MariaDB)
  - `hk1pkqqots65e6occy3wfmhn_data` (données utilisateurs de Moodle / `moodledata`)
- Un réseau Docker externe nommé `traefik-moodle` pour le routage HTTPS.

---

## Procédure de déploiement

### Étape 1 : Construction de l'image personnalisée

Les fichiers nécessaires à la construction de l'image sont regroupés dans `/home/nicolas-bodaine/moodle-custom-build/`.

#### Le Dockerfile
Le `Dockerfile` installe les dépendances système requises pour Moodle, configure les extensions PHP recommandées (OPcache, GD, etc.), clone le code source officiel de Moodle et fige les permissions.

```dockerfile
FROM php:8.2-apache

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

# Dépendances système requises par Moodle
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpng-dev libjpeg-dev libfreetype6-dev libzip-dev \
    libicu-dev libxml2-dev libxslt1-dev libldap2-dev \
    libgmp-dev libpq-dev libtidy-dev libbz2-dev \
    libsodium-dev unzip git cron ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Compilation et activation des extensions PHP
RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-configure ldap --with-libdir=lib/x86_64-linux-gnu/ \
    && docker-php-ext-install -j$(nproc) \
        bcmath bz2 calendar exif gd gettext gmp intl ldap \
        mysqli opcache pdo_mysql pdo_pgsql soap sockets sodium tidy xsl zip

# Configuration OPcache recommandée
RUN { \
    echo 'opcache.enable=1'; \
    echo 'opcache.memory_consumption=512'; \
    echo 'opcache.max_accelerated_files=10000'; \
    echo 'opcache.revalidate_freq=60'; \
    echo 'opcache.use_cwd=1'; \
    echo 'opcache.validate_timestamps=1'; \
    echo 'opcache.save_comments=1'; \
    echo 'opcache.enable_file_override=0'; \
    } > /usr/local/etc/php/conf.d/opcache-recommended.ini

# Limites de ressources PHP recommandées
RUN { \
    echo 'max_execution_time=600'; \
    echo 'memory_limit=512M'; \
    echo 'post_max_size=100M'; \
    echo 'upload_max_filesize=100M'; \
    echo 'max_input_vars=5000'; \
    } > /usr/local/etc/php/conf.d/moodle-recommended.ini

RUN a2enmod rewrite

# Clonage du code source stable de Moodle
ARG MOODLE_BRANCH=MOODLE_500_STABLE
RUN rm -rf /var/www/html/* \
    && git clone --depth 1 -b ${MOODLE_BRANCH} https://github.com/moodle/moodle.git /var/www/html

# Copie du fichier de configuration Moodle
COPY config.php /var/www/html/config.php

# Copie des plugins personnalisés (le cas échéant)
COPY tutotech /var/www/html/local/tutotech

# Figer les permissions système
RUN mkdir -p /var/moodledata \
    && chown -R www-data:www-data /var/moodledata \
    && chmod 770 /var/moodledata \
    && chown -R root:root /var/www/html \
    && find /var/www/html -type d -exec chmod 755 {} + \
    && find /var/www/html -type f -exec chmod 644 {} + \
    && chown www-data:www-data /var/www/html/config.php \
    && chmod 440 /var/www/html/config.php

# Planification du Cron Moodle
RUN echo "* * * * * www-data /usr/local/bin/php /var/www/html/admin/cli/cron.php >/dev/null 2>&1" > /etc/cron.d/moodle-cron \
    && chmod 0644 /etc/cron.d/moodle-cron

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]
CMD ["apache2-foreground"]
```

#### Le Script d'Entrée (entrypoint.sh)
Ce script démarre le service `cron` système en arrière-plan avant de lancer le serveur Apache au premier plan.
```bash
#!/bin/bash
set -e

# Démarrer le démon cron
cron

# Exécuter la commande par défaut du conteneur (apache2-foreground)
exec "$@"
```

#### Fichier de build (build.sh)
Pour simplifier la mise à jour, un script `build.sh` permet de relancer la compilation de l'image locale :
```bash
#!/bin/bash
set -e
cd "$(dirname "$0")"
docker build --build-arg MOODLE_BRANCH=MOODLE_500_STABLE -t moodle-custom:latest .
```

---

### Étape 2 : Configuration de la Persistance et du Docker Compose

Les fichiers de configuration opérationnelle sont regroupés sur l'hôte dans `/opt/docker/moodle-custom/` :
- `docker-compose.yml` : Fichier de description des conteneurs.
- `.env` : Fichier de variables d'environnement.
- `secrets/` : Mots de passe de production isolés.

#### Fichier docker-compose.yml
```yaml
services:
  mariadb:
    image: docker.io/bitnami/mariadb:latest
    container_name: moodle-custom-db
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - MARIADB_ROOT_PASSWORD_FILE=/run/secrets/mariadb_root_password
      - MARIADB_PASSWORD_FILE=/run/secrets/mariadb_password
      - MARIADB_USER=tutotech_moodle_db_user
      - MARIADB_DATABASE=tutotech_moodle_db
      - MARIADB_CHARACTER_SET=utf8mb4
      - MARIADB_COLLATE=utf8mb4_unicode_ci
      - ALLOW_EMPTY_PASSWORD=no
    volumes:
      - db:/bitnami/mariadb
    secrets:
      - mariadb_root_password
      - mariadb_password
    networks:
      - db

  moodle:
    image: moodle-custom:latest
    container_name: moodle-custom-app
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - MOODLE_DATABASE_HOST=mariadb
      - MOODLE_DATABASE_PORT_NUMBER=3306
      - MOODLE_DATABASE_USER=tutotech_moodle_db_user
      - MOODLE_DATABASE_NAME=tutotech_moodle_db
      - MOODLE_DATABASE_PASSWORD_FILE=/run/secrets/mariadb_password
      - MOODLE_WWWROOT=https://learn.tutotech.org
      - MOODLE_SSL_PROXY=true
    volumes:
      - data:/var/moodledata
    secrets:
      - mariadb_password
    depends_on:
      - mariadb
    networks:
      - db
      - app
      - traefik-moodle
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=traefik-moodle"
      - "traefik.http.routers.moodle-custom.rule=Host(`learn.tutotech.org`)"
      - "traefik.http.routers.moodle-custom.entrypoints=https"
      - "traefik.http.routers.moodle-custom.tls=true"
      - "traefik.http.routers.moodle-custom.tls.certresolver=letsencrypt"
      - "traefik.http.services.moodle-custom.loadbalancer.server.port=80"

volumes:
  db:
    external: true
    name: hk1pkqqots65e6occy3wfmhn_db
  data:
    external: true
    name: hk1pkqqots65e6occy3wfmhn_data

networks:
  db:
  app:
  traefik-moodle:
    name: traefik-moodle
    external: true

secrets:
  mariadb_root_password:
    file: /opt/docker/moodle-custom/secrets/mariadb_root_password
  mariadb_password:
    file: /opt/docker/moodle-custom/secrets/mariadb_password
```

---

### Étape 3 : Migration de la Base de Données et Droits d'Accès

#### Le Piège des Droits d'Accès
L'ancienne image Bitnami exécutait le serveur web en tant qu'utilisateur non-root `1001` (user `daemon`). L'image officielle `php:8.2-apache` exécute Apache sous l'utilisateur `www-data` (UID `33`). 

Si vous démarrez directement le nouveau conteneur sans modifier la propriété physique du dossier de données sur l'hôte, le conteneur Moodle renverra des **erreurs HTTP 500** car il ne pourra pas écrire dans son dossier de données `/var/moodledata` (sessions, cache, fichiers).

Avant de lancer le nouveau déploiement, il faut réassigner la propriété du volume de données :
```bash
docker run --rm -v hk1pkqqots65e6occy3wfmhn_data:/var/moodledata alpine chown -R 33:33 /var/moodledata
```

#### Mise à niveau MariaDB
L'ancienne base Bitnami reposait sur MariaDB 10.6. En pointant le nouveau Compose vers la dernière image `bitnami/mariadb:latest` (MariaDB 12), le conteneur MariaDB se chargera automatiquement de mettre à jour la base physique persistée dans le volume `hk1pkqqots65e6occy3wfmhn_db` au premier démarrage.

---

### Étape 4 : Intégration dans l'interface de Coolify

Afin de pouvoir contrôler Moodle directement via le tableau de bord Coolify (graphes, logs, gestion de statut) sans modifier l'emplacement des fichiers sur l'hôte :

1. Ouvrez l'interface Coolify, allez dans votre Projet -> service **moodle**.
2. Modifiez la configuration brute Docker Compose du service avec le contenu ci-dessus.
3. Assurez-vous d'avoir adapté le chemin des secrets et de l'environnement (`/opt/docker/moodle-custom/` au lieu de `/opt/docker/moodle/`).
4. Stoppez la pile de conteneurs démarrés manuellement sur l'hôte pour éviter les conflits :
   ```bash
   cd /opt/docker/moodle-custom && docker compose down
   ```
5. Déployez le service depuis Coolify. Les conteneurs créés s'appelleront `moodle-hk1pkqqots65e6occy3wfmhn` et `mariadb-hk1pkqqots65e6occy3wfmhn`.
6. Exécutez l'upgrade CLI de Moodle à l'intérieur du conteneur pour mettre à niveau les schémas de base de données :
   ```bash
   docker exec moodle-hk1pkqqots65e6occy3wfmhn php /var/www/html/admin/cli/upgrade.php --non-interactive
   ```

---

## Gestion des Plugins en Environnement Sans État (Stateless)

### Pourquoi ne PAS installer de plugin via l'interface web ?
Dans un conteneur standard, le dossier `/var/www/html` n'est pas persistant (il n'est pas mappé à un volume pour des raisons de sécurité). Si vous autorisez l'interface web à installer un plugin, les fichiers PHP seront écrits de manière temporaire. Au prochain déploiement ou redémarrage de la pile, **le plugin disparaîtra**, provoquant un crash ou des dysfonctionnements majeurs puisque la base de données Moodle s'attend à ce que le plugin soit toujours présent.

### Procédure de déploiement d'un plugin (exemple: `local_tutotech`)

1. **Extraction** : Téléchargez et extrayez le plugin dans `/home/nicolas-bodaine/moodle-custom-build/`.
2. **Nommage du dossier** : Respectez strictement la nomenclature Moodle. Par exemple, pour un composant nommé `local_tutotech`, Moodle s'attend à ce que le code soit placé dans le répertoire `local/tutotech/`. Renommez le dossier extrait en `tutotech` sur l'hôte.
3. **Déclaration de copie** : Ajoutez l'instruction de copie dans le `Dockerfile` (voir Étape 1) :
   ```dockerfile
   COPY tutotech /var/www/html/local/tutotech
   ```
4. **Build** : Compilez la nouvelle image locale en exécutant `./build.sh`.
5. **Déploiement** : Cliquez sur **Deploy** ou redémarrez le service dans Coolify pour lancer le nouveau conteneur.
6. **Mise à niveau de la base de données** : Indiquez à Moodle d'appliquer la mise à jour en base :
   ```bash
   docker exec moodle-hk1pkqqots65e6occy3wfmhn php /var/www/html/admin/cli/upgrade.php --non-interactive
   ```
7. **Purge du Cache** :
   ```bash
   docker exec moodle-hk1pkqqots65e6occy3wfmhn php /var/www/html/admin/cli/purge_caches.php
   ```

---

## Points de Vigilance et Erreurs à Éviter

!!! warning "Reversion de Permissions"
    Si vous devez interagir manuellement avec le volume de données utilisateurs via d'autres scripts ou conteneurs, veillez à ne jamais repasser la propriété à `1001:1001` (Bitnami) sous peine de casser l'accès en écriture d'Apache (`www-data:www-data`).

!!! danger "Dossier applicatif non sécurisé"
    N'utilisez jamais la commande `chown -R www-data:www-data /var/www/html` dans le conteneur de production. Bien que cela facilite l'installation de plugins via le web, cela détruit la barrière de sécurité principale en lecture seule et expose l'instance aux injections de code PHP malveillant.

---

## Vérification

Pour valider le fonctionnement et l'intégration :

```bash
# Vérifier la réponse HTTP
curl -kI https://learn.tutotech.org
```

!!! success "Résultat attendu"
    La commande renvoie un code de statut `HTTP/2 200` ou un redirect `302` avec l'en-tête `set-cookie: MoodleSession=...`.

---

## Ressources

- [Dépôt Officiel de Moodle sur GitHub](https://github.com/moodle/moodle)
- [Image Officielle PHP sur Docker Hub](https://hub.docker.com/_/php)
- [Documentation Docker Compose](https://docs.docker.com/compose/)
