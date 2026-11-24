---
title: "Annexes du parcours Docker : aide-mémoire des commandes, dépannage, glossaire et QCM"
date: 2026-11-24
author: Nicolas BODAINE
tags:
  - docker
  - aide-memoire
  - depannage
  - cours
difficulty: débutant
os: Debian 13.7, Docker Engine 29.10
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                          -->
<!-- Pensez TOUJOURS à ajouter une entrée dans le fichier d'index  -->
<!-- (index.md) du dossier correspondant (ex: docs/cloud/index.md) -->
<!-- afin de référencer ce nouvel article et permettre aux         -->
<!-- visiteurs de le trouver et de cliquer dessus !                -->
<!-- ============================================================ -->

# Annexes

!!! abstract "Résumé"
    Les pages à garder ouvertes pendant et après le parcours : un **aide-mémoire** des commandes, classées par thème ; un guide de **dépannage** qui part des messages d'erreur réellement rencontrés dans les TP ; un **glossaire** ; et deux **QCM** pour vérifier ses connaissances.

| Propriété | Valeur |
|-----------|--------|
| Version décrite | Docker Engine 29.10, Docker Compose 5.8, Debian 13.7 |
| Place dans le parcours | Annexes du parcours [Docker](index.md) |
| Dernière mise à jour | 2026-11-24 |

---

<!-- NOTE DE RÉDACTION (non affichée) : l'aide-mémoire reprend et complète celui du cours 00 du formateur (« Aide-mémoire Docker : commandes de base »), en remplaçant les noms anglais (mycontainer, mynetwork) par des noms en français. Les messages d'erreur du dépannage sont tous recopiés des TP exécutés dans le lab (journal AVANCEMENT.md). Le QCM 1 est celui du cours 00 ; question 2 adaptée : « dépôts officiels d'Ubuntu » → « dépôts de Debian » (le parcours est sur Debian ; le paquet docker.io existe aussi dans Debian 13, en version 26.1.5). Le QCM 2 est ajouté pour couvrir l'ensemble du parcours. -->

## 1. Aide-mémoire des commandes

### 1.1 Conteneurs

| Commande | Effet | Partie |
|---|---|:---:|
| `docker run -d --name web -p 8080:80 nginx` | Lance un conteneur en arrière-plan, nommé, avec un port publié | 2 |
| `docker run -it --rm debian:13 bash` | Lance un conteneur interactif, supprimé à la sortie | 2 |
| `docker run … -v donnees:/chemin` / `-v ~/site:/chemin:ro` | Monte un volume nommé / un dossier de la VM (en lecture seule) | 5 |
| `docker run … --restart unless-stopped` | Redémarre le conteneur avec Docker, sauf s'il a été arrêté à la main | 3, 4 |
| `docker run … --memory 256m --cpus 0.5` | Limite la mémoire et le processeur | 12 |
| `docker ps` / `docker ps -a` | Conteneurs démarrés / tous les conteneurs | 2 |
| `docker stop web` / `docker start web` / `docker restart web` | Arrêter / démarrer / redémarrer | 2 |
| `docker rm web` / `docker rm -f web` | Supprimer (arrêté) / supprimer de force | 2 |
| `docker logs -f --tail 50 web` | Suivre les 50 dernières lignes du journal | 2, 12 |
| `docker exec -it web bash` (ou `sh`) | Ouvrir un shell dans un conteneur démarré | 2 |
| `docker inspect web` | Tout savoir d'un conteneur (format JSON) | 2 |
| `docker stats` / `docker top web` | Consommation en direct / processus d'un conteneur | 2, 12 |
| `docker cp web:/chemin/fichier .` | Copier un fichier depuis un conteneur (ou vers lui, en inversant) | — |
| `docker commit web mon-image:1.0` | Figer un conteneur en image (boîte noire) | 6 |

### 1.2 Images

| Commande | Effet | Partie |
|---|---|:---:|
| `docker pull nginx:1.31` | Télécharger une image | 2 |
| `docker image ls` (ou `docker images`) | Lister les images | 2 |
| `docker history nginx` | Voir les couches et les instructions d'une image | 2, 6, 14 |
| `docker build -t web:1.0 .` | Construire une image à partir du Dockerfile du dossier courant | 14 |
| `docker tag web:1.0 IP:5000/web:1.0` | Donner un autre nom à une image | 15 |
| `docker push IP:5000/web:1.0` | Envoyer une image vers un registre | 15 |
| `docker login -u <identifiant>` / `docker logout` | Se connecter à un registre (avec un jeton) / se déconnecter | 15 |
| `docker save -o image.tar web:1.0` / `docker load -i image.tar` | Exporter / importer une image dans un fichier | 6 |
| `docker rmi web:1.0` (ou `docker image rm`) | Supprimer une image | 2 |

### 1.3 Volumes et réseaux

| Commande | Effet | Partie |
|---|---|:---:|
| `docker volume ls` / `create` / `inspect` / `rm` | Gérer les volumes | 5 |
| `docker network ls` | Lister les réseaux | 7 |
| `docker network create mon_reseau` | Créer un réseau bridge personnalisé (avec résolution des noms) | 7 |
| `docker network connect mon_reseau web` / `disconnect` | Brancher / débrancher un conteneur | 7 |
| `docker network inspect mon_reseau` | Sous-réseau, passerelle, conteneurs branchés | 7 |
| `docker network create -d overlay --attachable reseau-app` | Créer un réseau overlay (Swarm) | 16 |

### 1.4 Docker Compose

| Commande | Effet | Partie |
|---|---|:---:|
| `docker compose up -d` | Créer et démarrer l'application du fichier `compose.yaml` | 8 |
| `docker compose ps` / `logs -f` | État / journaux des services | 8 |
| `docker compose stop` / `start` | Arrêter / redémarrer sans supprimer | 8 |
| `docker compose down` / `down -v` | Supprimer conteneurs et réseaux / **et les volumes** | 8 |
| `docker compose pull` puis `up -d` | Mettre à jour les images et recréer ce qui a changé | 12 |
| `docker compose exec nc bash` | Shell dans un service | 8 |

### 1.5 Swarm

| Commande | Effet | Partie |
|---|---|:---:|
| `docker swarm init --advertise-addr IP` | Créer un cluster (ce nœud devient manager) | 16 |
| `docker swarm join-token worker` | Réafficher la commande pour ajouter un worker | 16 |
| `docker swarm join --token … IP:2377` | Rejoindre un cluster | 16 |
| `docker node ls` | Lister les nœuds (sur un manager) | 16 |
| `docker node update --availability drain|active nœud` | Vider / remettre en service un nœud | 16 |
| `docker service create --name s --replicas 3 -p 8080:80 image` | Créer un service répliqué | 16 |
| `docker service ls` / `ps s` / `logs s` | Services / tâches d'un service / journaux | 16 |
| `docker service scale s=5` | Changer le nombre de répliques | 16 |
| `docker service update --image image:2.0 s` / `rollback s` | Mise à jour progressive / retour arrière | 16 |
| `docker service update --force s` | Remplacer les tâches (rééquilibrer) | 16 |
| `docker stack deploy -c compose.yaml pile` / `stack rm pile` | Déployer / supprimer une pile | 16 |

### 1.6 Ménage et diagnostic

| Commande | Effet | Partie |
|---|---|:---:|
| `docker system df` | Place occupée par images, conteneurs, volumes, cache | 12 |
| `docker container prune` / `image prune` | Supprimer les conteneurs arrêtés / les images sans nom | 12 |
| `docker system prune` | Les deux, plus les réseaux inutilisés et le cache de construction | 12 |
| `docker volume prune` | Supprimer les volumes **inutilisés** : données perdues, à manier avec prudence | 5, 12 |
| `docker info` | Version, pilote de stockage, registres, état Swarm | 6, 15, 16 |
| `docker events` | Suivre en direct ce que fait le moteur | 4 |
| `sudo dockerd --validate --config-file /etc/docker/daemon.json` | Vérifier la syntaxe du fichier de configuration | 12, 15 |

## 2. Dépannage

Les messages ci-dessous ont été rencontrés pendant les TP (sauf les deux dernières lignes du tableau, des situations courantes en production). Commencer **toujours** par lire le message complet, puis `docker logs` (conteneur) ou `docker service ps --no-trunc` (service Swarm).

| Message ou symptôme | Cause | Solution |
|---|---|---|
| `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock` | L'utilisateur n'est pas dans le groupe `docker`, ou ne s'est pas reconnecté depuis | `sudo usermod -aG docker adminlab`, puis se **déconnecter et se reconnecter** (partie 1) |
| `Could not get lock /var/lib/apt/lists/lock` | Une mise à jour automatique tourne, juste après le démarrage | Attendre une minute, relancer |
| `Bind for 0.0.0.0:8080 failed: port is already allocated` | Un autre conteneur (ou programme) occupe ce port de la VM ; le nouveau conteneur reste en état `Created` | `docker ps` pour trouver qui l'occupe ; choisir un autre port ; supprimer le conteneur `Created` (partie 2) |
| `Conflict. The container name "/web" is already in use…` | Un conteneur de ce nom existe, même arrêté | `docker rm -f web` ou un autre nom (partie 2) |
| `cannot remove container "web": container is running` | On ne supprime pas un conteneur démarré | `docker stop web` puis `docker rm web`, ou `docker rm -f web` |
| Le conteneur passe aussitôt en `Exited (0)` | Son processus principal s'est terminé (par exemple `debian` sans `-it`, ou un service lancé en arrière-plan) | Une commande qui reste au premier plan (partie 2, partie 14) |
| `cannot attach stdin to a TTY-enabled container because stdin is not a terminal` | `-it` utilisé dans un script ou sans terminal | Retirer `-t` (ou `-it`) dans un script |
| Après `docker restart`, le service installé à la main ne répond plus (`curl: (56) Recv failure`) | Les services lancés à la main ne sont pas relancés : seul le processus principal l'est | Une image propre, avec la bonne commande de démarrage (partie 3, partie 14) |
| `Exited (137)`, et `docker inspect` affiche `OOMKilled=true` | Le conteneur a dépassé sa limite de mémoire et a été tué | Augmenter `--memory`, ou corriger l'application (partie 12) |
| Nextcloud : `SQLSTATE[HY000] [2002] Connection refused` à l'installation | La base de données n'avait pas fini de démarrer | `healthcheck` sur la base et `depends_on: condition: service_healthy` (partie 8) |
| `502 Bad Gateway` affiché par NPM (`openresty`) | NPM ne joint pas le conteneur de destination : pas de réseau commun, mauvais nom ou mauvais port, ou application pas encore démarrée | `docker network connect <réseau> npm-app-1`, vérifier nom et port **internes** (partie 9) |
| `mkdir: cannot create directory '/var/run/sshd': File exists` pendant `docker build` | Le dossier existe déjà dans l'image (Debian 13) | `mkdir -p /run/sshd` (partie 14) |
| `mysql: unrecognized service` dans `docker logs` | Sur Debian 13, le service s'appelle `mariadb` | `service mariadb start` (partie 14) |
| `http: server gave HTTP response to HTTPS client` | Registre en HTTP, non déclaré comme tel | `insecure-registries` dans `/etc/docker/daemon.json`, puis `sudo systemctl restart docker` (partie 15) |
| `localhost:5000` ne marche plus après avoir ajouté `insecure-registries` | La liste remplace la règle par défaut des adresses locales | Ajouter `"127.0.0.0/8", "::1/128"` à la liste (partie 15) |
| `This node is not a swarm manager…` | Commande de gestion tapée sur un worker | La taper sur un manager (partie 16) |
| `The network … cannot be used with services. Only networks scoped to the swarm can be used` | Réseau `bridge` dans une pile Swarm | `driver: overlay`, puis `docker stack rm` avant de redéployer (partie 17) |
| `port '8080' is already in use by service '…' as an ingress port` | Le port est déjà publié par un autre service, sur tout le cluster | Choisir un autre port (partie 17) |
| Tâches `Rejected` : `dial tcp [::1]:5000: connect: connection refused` | Image en `localhost:…` : chaque nœud cherche le registre chez lui | Nom d'image avec l'adresse IP (ou le nom) du registre (parties 16 et 17) |
| Après la panne d'un nœud, toutes les répliques restent sur les autres | Swarm ne déplace pas des conteneurs qui marchent | `docker service update --force <service>` (partie 16) |
| `toomanyrequests` au téléchargement depuis Docker Hub | Limite de téléchargements atteinte (100 par 6 h sans compte) | `docker login` (200 par 6 h), ou attendre, ou un registre local (partie 15) |
| Disque de la VM plein | Images, journaux et cache accumulés | `docker system df`, rotation des journaux, `docker system prune` (partie 12) |

!!! tip "La démarche de dépannage, en quatre questions"
    1. **Le conteneur tourne-t-il ?** `docker ps -a` : `Up`, `Exited (code)`, `Restarting` ?
    2. **Que dit-il ?** `docker logs <conteneur>` (ou `docker compose logs`, `docker service ps --no-trunc`).
    3. **Le port est-il publié, et vers le bon port interne ?** `docker ps` (colonne `PORTS`), puis `curl` depuis la VM.
    4. **Les conteneurs se voient-ils ?** `docker network inspect`, puis `getent hosts <nom>` ou `wget` depuis un conteneur du même réseau.

## 3. Glossaire

| Terme | Définition |
|---|---|
| **Bind mount** (dossier monté) | Un dossier de la machine hôte rendu visible dans un conteneur (partie 5) |
| **BuildKit** | Le moteur de construction d'images de Docker, utilisé par `docker build` |
| **Cluster** | Groupe de machines qui travaillent ensemble et se répartissent les services (partie 16) |
| **Compose** | Outil qui décrit une application multi-conteneurs dans un fichier YAML et la déploie en une commande (partie 8) |
| **Conteneur** | Processus isolé, lancé à partir d'une image, qui partage le noyau de la machine hôte |
| **Couche** (*layer*) | Une tranche d'image, en lecture seule, produite par une instruction ; les couches sont partagées entre images |
| **Démon Docker** (`dockerd`) | Le service qui fait tourner les conteneurs et répond aux commandes `docker` |
| **Digest** (empreinte) | Identifiant `sha256:…` du contenu exact d'une image ; il ne change jamais |
| **Dockerfile** | Fichier texte qui décrit la construction d'une image, instruction par instruction (partie 14) |
| **Docker Hub** | Le registre public de Docker (partie 15) |
| **Étiquette** (*tag*) | La partie après `:` dans le nom d'une image, en général la version (`nginx:1.31`) |
| **Healthcheck** | Commande qui teste régulièrement si le service d'un conteneur répond (parties 8 et 14) |
| **Image** | Modèle en lecture seule à partir duquel on lance des conteneurs |
| **Ingress** | Réseau overlay de Swarm qui porte le maillage de routage (partie 16) |
| **Jeton d'accès** (*access token*) | Mot de passe dédié, limitable et révocable, pour se connecter à un registre (partie 15) |
| **Maillage de routage** (*routing mesh*) | Chaque nœud du cluster accepte le port publié d'un service et transmet à une réplique (partie 16) |
| **Manager** / **Worker** | Nœud qui gère le cluster / nœud qui exécute les tâches (partie 16) |
| **Nœud** (*node*) | Une machine membre d'un cluster Swarm |
| **Orchestrateur** | Logiciel qui maintient l'état voulu d'un ensemble de services sur plusieurs machines (Swarm, Kubernetes) |
| **Overlay** | Réseau virtuel qui s'étend sur plusieurs machines (parties 7 et 16) |
| **Pile** (*stack*) | Application décrite par un fichier Compose et déployée sur un cluster Swarm (partie 16) |
| **Publication de port** | Redirection d'un port de la machine hôte vers un port du conteneur (`-p`) (partie 2) |
| **Quorum** | Majorité des managers nécessaire pour qu'un cluster Swarm prenne une décision (partie 16) |
| **Registre** (*registry*) | Serveur qui stocke et distribue des images (partie 15) |
| **Réplique** / **tâche** | Un conteneur lancé par Swarm pour un service (partie 16) |
| **Reverse proxy** | Serveur qui reçoit les requêtes web et les transmet au bon service selon le nom demandé (partie 9) |
| **Service** (Swarm) | Description de l'état voulu : image, nombre de répliques, ports, réseaux (partie 16) |
| **Socket Docker** | Le fichier `/var/run/docker.sock` par lequel on commande le démon ; y avoir accès revient à être `root` (parties 1, 4, 12) |
| **Volume** | Espace de stockage géré par Docker, indépendant de la vie du conteneur (partie 5) |
| **VXLAN** | Technique qui transporte des trames réseau dans des paquets UDP (port 4789) : la base des réseaux overlay (partie 16) |

## 4. QCM : découverte de Docker

Cinq questions sur les bases du jour 1.

1. Qu'est-ce qu'un conteneur Docker ?
    - a) Un programme de virtualisation complet qui contient un système d'exploitation complet
    - b) Une instance exécutable d'une image Docker qui contient tout ce dont l'application a besoin pour fonctionner
    - c) Un outil pour créer des machines virtuelles
    - d) Une image Docker téléchargeable depuis Docker Hub
2. Quelle commande installe Docker à partir des dépôts **de Debian** (et non du dépôt officiel de Docker) ?
    - a) `sudo apt install docker-ce`
    - b) `sudo apt update docker`
    - c) `sudo apt install docker.io`
    - d) `sudo install docker`
3. Quel est l'avantage d'ajouter l'utilisateur au groupe `docker` avec `sudo usermod -aG docker ${USER}` ?
    - a) Pour installer Docker sans utiliser de mot de passe
    - b) Pour ne plus avoir besoin d'utiliser `sudo` à chaque commande Docker
    - c) Pour permettre à Docker de démarrer automatiquement au démarrage
    - d) Pour créer de nouveaux conteneurs plus rapidement
4. Comment vérifier que Docker est bien en cours d'exécution sur la machine ?
    - a) `docker --check`
    - b) `sudo docker check-status`
    - c) `sudo systemctl status docker`
    - d) `docker run status`
5. Quelle commande télécharge une image depuis Docker Hub ?
    - a) `docker push [image]`
    - b) `docker pull [image]`
    - c) `docker install [image]`
    - d) `docker download [image]`

??? success "Réponses"
    **1b ; 2c ; 3b ; 4c ; 5b.**

    1. Un conteneur est une **instance** d'une image : il partage le noyau de la machine, contrairement à une VM (a, c) ; l'image est le modèle, pas le conteneur (d).
    2. `docker.io` est le paquet **de Debian** (version 26.1 sur Debian 13). `docker-ce` est le paquet du **dépôt officiel de Docker**, celui installé en partie 1 (version 29.10), plus récent.
    3. Plus besoin de `sudo`. Attention : être dans le groupe `docker` revient à être **`root`** sur la machine (partie 1).
    4. `systemctl status docker` affiche l'état du service (`active (running)`).
    5. `pull` télécharge, `push` envoie vers un registre (partie 15).

## 5. QCM : fin de parcours

1. Les données d'un conteneur MariaDB lancé **sans** `-v` sont…
    - a) perdues dès l'arrêt du conteneur
    - b) dans un volume anonyme, gardé à la suppression du conteneur mais facile à perdre avec `docker volume prune`
    - c) automatiquement sauvegardées sur Docker Hub
2. Deux conteneurs sur le réseau `bridge` **par défaut** peuvent-ils se joindre par leur nom ?
    - a) Oui, toujours
    - b) Non : la résolution des noms ne fonctionne que sur un réseau personnalisé
    - c) Seulement avec `--network host`
3. Dans un fichier Compose, à quoi sert `depends_on` avec `condition: service_healthy` ?
    - a) À démarrer un service seulement quand le `healthcheck` de l'autre répond
    - b) À redémarrer un service en panne
    - c) À répartir les services sur plusieurs machines
4. Pourquoi ne faut-il pas monter `/var/run/docker.sock` dans un conteneur sans raison ?
    - a) Cela ralentit Docker
    - b) Le conteneur pourrait piloter Docker, donc devenir `root` sur la machine
    - c) Le conteneur ne pourrait plus démarrer
5. Que fait l'instruction `EXPOSE 80` d'un Dockerfile ?
    - a) Elle publie le port 80 de la machine
    - b) Elle ouvre le pare-feu
    - c) Elle documente le port de l'application, sans rien publier
6. Pourquoi l'image d'un service Swarm doit-elle venir d'un registre ?
    - a) Chaque nœud télécharge l'image lui-même
    - b) Swarm refuse les images locales par sécurité
    - c) Pour profiter des limites de Docker Hub
7. Un cluster Swarm a 3 managers. Combien peuvent tomber sans bloquer la gestion du cluster ?
    - a) 0
    - b) 1
    - c) 2
8. Quel port doit être ouvert **uniquement** vers les managers d'un cluster Swarm ?
    - a) 2377/TCP
    - b) 7946/UDP
    - c) 4789/UDP

??? success "Réponses"
    **1b ; 2b ; 3a ; 4b ; 5c ; 6a ; 7b ; 8a.**

    1. L'image MariaDB déclare un `VOLUME` : sans `-v`, Docker crée un **volume anonyme** (nom de 64 caractères), conservé à la suppression du conteneur, mais impossible à reconnaître et supprimé par `docker volume prune` (partie 5).
    2. Sur le bridge par défaut, il faut l'adresse IP ; un réseau personnalisé apporte le DNS intégré de Docker (partie 7).
    3. Le service attend que la base soit **réellement prête**, pas seulement démarrée (partie 8).
    4. Qui pilote Docker peut lancer un conteneur qui monte `/` de la machine : c'est un accès `root` (parties 1, 4, 12).
    5. `EXPOSE` documente ; la publication se fait avec `-p` (partie 14).
    6. Une image construite sur un nœud n'existe que là ; les autres nœuds la téléchargent depuis un registre qu'ils peuvent joindre (parties 15 et 16).
    7. La majorité de 3 est 2 : on supporte la perte d'**un** manager, (3-1)/2 = 1 (partie 16).
    8. 2377/TCP sert à la gestion du cluster, sur les managers ; 7946 et 4789 sont nécessaires entre **tous** les nœuds (partie 16).

---

## Ressources

- [Documentation officielle de Docker](https://docs.docker.com/) — la référence (en anglais).
- [Référence de la ligne de commande `docker`](https://docs.docker.com/reference/cli/docker/) — toutes les commandes et leurs options.
- [Référence du fichier Compose](https://docs.docker.com/reference/compose-file/) — tous les champs d'un `compose.yaml`.
- Retour à l'[accueil du parcours](index.md) · Partie précédente : [Défi final](17-defi-final.md).

*[DNS]: Domain Name System — résolution des noms en adresses IP
*[NPM]: Nginx Proxy Manager
*[VM]: Virtual Machine — machine virtuelle
*[YAML]: format de fichier texte structuré par l'indentation
*[QCM]: questionnaire à choix multiples
*[JSON]: JavaScript Object Notation — format de données texte
*[TCP]: Transmission Control Protocol
*[UDP]: User Datagram Protocol
