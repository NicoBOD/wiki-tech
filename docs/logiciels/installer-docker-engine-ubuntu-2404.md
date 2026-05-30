---
title: Installer Docker Engine et le plugin Docker Compose sur Ubuntu 24.04
date: 2026-05-30
author: Nicolas BODAINE
tags:
  - docker
  - docker-compose
  - ubuntu
  - conteneurs
  - lab
difficulty: débutant
os: Ubuntu 24.04
status: publié
---

# Installer Docker Engine et le plugin Docker Compose sur Ubuntu 24.04

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour installer **Docker Engine** sur **Ubuntu 24.04**, ajouter le **plugin Docker Compose**, démarrer le service, tester un premier conteneur et permettre à un utilisateur d'exécuter Docker sans `sudo`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 |
| Dernière mise à jour | 2026-05-30 |

## Contexte

Docker permet d'exécuter des applications dans des **conteneurs**.
Dans un lab, c'est très pratique pour :

- lancer rapidement un service de test ;
- isoler une application du reste du système ;
- reproduire facilement un TP sur plusieurs machines ;
- préparer des environnements pour `n8n`, `nginx`, `postgres`, `portainer` ou d'autres outils.

Sur Ubuntu, il existe plusieurs façons d'obtenir Docker.
Pour un tutoriel propre et durable, le plus fiable est d'utiliser le **dépôt APT officiel de Docker**, puis d'installer :

- **Docker Engine** ;
- le **client Docker** ;
- **containerd** ;
- le **plugin Docker Compose** ;
- le **plugin Buildx**.

L'objectif de ce TP est de partir d'une VM Ubuntu 24.04 propre et d'arriver à un environnement prêt pour les prochains labs.

!!! note "Pourquoi éviter le paquet `docker.io` pour ce tutoriel"
    Ubuntu propose son propre paquet `docker.io`, mais la documentation officielle Docker recommande d'utiliser le dépôt Docker pour obtenir les versions prévues par l'éditeur et une procédure de mise à jour cohérente.

## Prérequis

- Une VM ou une machine de test sous **Ubuntu 24.04**
- Un compte avec les droits `sudo`
- Un accès Internet pour télécharger les paquets
- Au moins **2 Go de RAM** recommandés pour être à l'aise dans les futurs labs

!!! tip "Dans quel cas faire ce TP ?"
    Ce tutoriel est adapté si vous préparez une machine de lab personnelle, une VM de démonstration ou un poste de test pour exécuter des stacks simples avec `docker run` ou `docker compose`.

## Procédure

### Étape 1 : vérifier que le système est bien Ubuntu 24.04

Commencez par identifier clairement la distribution et la version installée.

```bash
cat /etc/os-release
uname -r
```

Résultat attendu :

```text
PRETTY_NAME="Ubuntu 24.04 LTS"
```

Cette vérification évite de copier une procédure Ubuntu sur une autre distribution sans s'en rendre compte.

### Étape 2 : supprimer d'anciens paquets Docker s'ils existent

La documentation officielle Docker recommande de retirer d'anciens paquets susceptibles d'entrer en conflit.

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt-get remove -y "$pkg"
done
```

!!! note "Important"
    Cette commande peut afficher des messages du type **« paquet non installé »**.
    Ce n'est pas un problème : sur une VM neuve, c'est même normal.

### Étape 3 : mettre à jour APT et installer les paquets nécessaires

Installez les outils nécessaires pour utiliser un dépôt HTTPS signé.

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
```

Ces paquets servent notamment à :

- récupérer la clé GPG du dépôt Docker ;
- stocker cette clé proprement ;
- utiliser APT avec un dépôt distant sécurisé.

### Étape 4 : créer le répertoire de clés APT

```bash
sudo install -m 0755 -d /etc/apt/keyrings
```

Ce dossier est utilisé pour stocker la clé du dépôt Docker.

### Étape 5 : ajouter la clé GPG officielle de Docker

```bash
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

Vérifiez que le fichier existe :

```bash
ls -l /etc/apt/keyrings/docker.asc
```

### Étape 6 : ajouter le dépôt officiel Docker

Ajoutez ensuite le dépôt APT correspondant à votre architecture et à votre version Ubuntu.

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Vérifiez le contenu du fichier :

```bash
cat /etc/apt/sources.list.d/docker.list
```

Exemple attendu sur Ubuntu 24.04 :

```text
deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu noble stable
```

### Étape 7 : actualiser l'index des paquets

```bash
sudo apt update
```

Si tout est correct, APT doit maintenant voir les paquets fournis par Docker.

Vous pouvez le vérifier avec :

```bash
apt-cache policy docker-ce
```

!!! success "Résultat attendu"
    La commande `apt-cache policy docker-ce` doit afficher un **Candidate** provenant de `download.docker.com`.

### Étape 8 : installer Docker Engine, Compose et Buildx

Installez maintenant les composants principaux.

```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Explication rapide des paquets

- `docker-ce` : moteur Docker ;
- `docker-ce-cli` : client en ligne de commande ;
- `containerd.io` : runtime de conteneurs ;
- `docker-buildx-plugin` : fonctionnalités de build modernes ;
- `docker-compose-plugin` : commande `docker compose`.

### Étape 9 : vérifier que le service Docker est démarré

Contrôlez l'état du service :

```bash
sudo systemctl status docker --no-pager
```

Vous pouvez aussi vérifier qu'il démarre au boot :

```bash
sudo systemctl is-enabled docker
sudo systemctl is-active docker
```

Si nécessaire, activez-le explicitement :

```bash
sudo systemctl enable --now docker
```

!!! success "Résultat attendu"
    Le service `docker` doit être **active (running)**.

### Étape 10 : vérifier les versions installées

```bash
docker --version
docker compose version
docker buildx version
```

Exemple de lecture :

```text
Docker version 28.x.x, build ...
Docker Compose version v2.x.x
github.com/docker/buildx ...
```

### Étape 11 : lancer un premier conteneur de test

Le test classique recommandé par Docker consiste à exécuter l'image `hello-world`.

```bash
sudo docker run hello-world
```

Au premier lancement, Docker télécharge automatiquement l'image si elle n'est pas encore présente sur la machine.

Extrait de résultat attendu :

```text
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

!!! success "Ce que prouve ce test"
    Si `hello-world` s'exécute correctement, cela signifie en général que :
    
    - le démon Docker fonctionne ;
    - le client peut dialoguer avec le démon ;
    - le téléchargement d'image fonctionne ;
    - l'exécution d'un conteneur est opérationnelle.

### Étape 12 : afficher les conteneurs et les images locales

Après le test, affichez les objets présents localement.

```bash
sudo docker ps -a
sudo docker images
```

Vous devez voir au moins l'image `hello-world` et le conteneur créé pour le test.

### Étape 13 : autoriser un utilisateur à utiliser Docker sans `sudo`

Par défaut, les commandes Docker passent souvent par `sudo`.
La documentation officielle propose d'utiliser le groupe `docker` pour simplifier l'usage quotidien.

Créez le groupe s'il n'existe pas déjà :

```bash
sudo groupadd docker
```

Ajoutez ensuite votre utilisateur au groupe :

```bash
sudo usermod -aG docker $USER
```

Appliquez le changement dans la session courante :

```bash
newgrp docker
```

Puis retestez sans `sudo` :

```bash
docker run hello-world
```

!!! warning "Déconnexion parfois nécessaire"
    Selon la session utilisée, il peut être nécessaire de **se déconnecter puis se reconnecter** avant que l'appartenance au groupe `docker` soit prise en compte partout.

### Étape 14 : vérifier que Docker Compose fonctionne

Le plugin moderne s'utilise avec **`docker compose`** et non plus avec l'ancienne commande séparée **`docker-compose`**.

```bash
docker compose version
```

!!! note "Bonne pratique"
    Dans les nouveaux tutoriels, utilisez la syntaxe **`docker compose`**.
    Elle correspond au plugin officiellement maintenu par Docker.

### Étape 15 : faire un mini test avec `docker compose`

Créez un dossier de lab :

```bash
mkdir -p ~/lab-docker-nginx
cd ~/lab-docker-nginx
```

Créez ensuite le fichier `compose.yaml` suivant :

```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: lab-nginx
    ports:
      - "8080:80"
    restart: unless-stopped
```

Démarrez le service :

```bash
docker compose up -d
```

Vérifiez son état :

```bash
docker compose ps
docker logs lab-nginx
```

Testez ensuite depuis la machine locale :

```bash
curl http://127.0.0.1:8080
```

!!! success "Résultat attendu"
    La commande `curl` doit renvoyer le HTML par défaut de **nginx**.

Quand le test est terminé, vous pouvez arrêter et supprimer le conteneur :

```bash
docker compose down
```

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `docker --version` | Afficher la version du client Docker |
| `docker compose version` | Vérifier le plugin Docker Compose |
| `sudo systemctl status docker --no-pager` | Vérifier l'état du service Docker |
| `docker ps` | Afficher les conteneurs en cours d'exécution |
| `docker ps -a` | Afficher tous les conteneurs, même arrêtés |
| `docker images` | Afficher les images locales |
| `docker run hello-world` | Tester le fonctionnement de Docker |
| `docker compose up -d` | Démarrer une stack en arrière-plan |
| `docker compose down` | Arrêter et supprimer les conteneurs de la stack |

## Vérification

Après ce TP, vous devez pouvoir valider les points suivants :

```bash
docker --version
docker compose version
systemctl is-active docker
docker run hello-world
```

!!! success "Résultat attendu"
    - `docker --version` répond correctement ;
    - `docker compose version` répond correctement ;
    - `systemctl is-active docker` renvoie `active` ;
    - `docker run hello-world` s'exécute sans erreur.

## Ressources

- [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/) — Documentation officielle Docker pour Ubuntu
- [Linux post-installation steps for Docker Engine](https://docs.docker.com/engine/install/linux-postinstall/) — Post-configuration officielle, notamment l'usage sans `sudo`
- [Docker Compose](https://docs.docker.com/compose/) — Documentation officielle du plugin Compose
- [Docker Engine overview](https://docs.docker.com/engine/) — Vue d'ensemble du moteur Docker
