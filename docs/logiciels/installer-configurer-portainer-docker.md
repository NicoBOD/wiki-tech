---
title: Installer et configurer Portainer pour gérer ses conteneurs Docker
date: 2026-06-14
author: Nicolas BODAINE
tags:
  - docker
  - portainer
  - conteneurs
  - interface-web
difficulty: débutant
os: Ubuntu 24.04
status: publié
---

# Installer et configurer Portainer pour gérer ses conteneurs Docker

!!! abstract "Résumé"
    Ce tutoriel explique comment déployer Portainer, une interface web graphique (GUI) légère et puissante, pour gérer facilement vos environnements Docker sans passer exclusivement par la ligne de commande.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 |
| Dernière mise à jour | 2026-06-14 |

## Contexte

Gérer des conteneurs avec les commandes `docker ps`, `docker logs` ou `docker inspect` est incontournable. Cependant, lorsqu'on administre plusieurs dizaines de conteneurs, avoir une vue d'ensemble graphique devient extrêmement pratique. 

**Portainer** répond à ce besoin en offrant une interface web intuitive. Il permet de déployer des conteneurs, consulter les logs en direct, ouvrir une console interactive à l'intérieur d'un conteneur, ou encore gérer les réseaux et les volumes Docker en quelques clics.

## Prérequis

- Un système Linux (ex: Ubuntu 24.04) ou un environnement de type laboratoire.
- **Docker Engine** installé et fonctionnel (voir le tutoriel dédié : *Installer Docker Engine sur Ubuntu 24.04*).
- Les droits d'administration (via `sudo` ou `root`).
- Un accès réseau au serveur (pour afficher l'interface web sur le port 9443).

## Procédure

Le déploiement de Portainer s'effectue sous la forme d'un simple conteneur Docker, qui va venir se brancher directement sur le socket Docker du serveur hôte pour le piloter.

### Étape 1 : Créer un volume pour les données de Portainer

Pour que la configuration de Portainer et ses données soient conservées même si le conteneur est redémarré ou mis à jour, il est indispensable de créer un volume Docker persistant.

```bash
sudo docker volume create portainer_data
```

### Étape 2 : Déployer le conteneur Portainer Server

Nous allons maintenant télécharger l'image officielle et lancer le conteneur. L'argument `--restart=always` garantit que Portainer redémarrera automatiquement au lancement du serveur ou si Docker plante.

```bash
sudo docker run -d -p 8000:8000 -p 9443:9443 \
    --name portainer \
    --restart=always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v portainer_data:/data \
    portainer/portainer-ce:latest
```

!!! note "Explication des paramètres"
    - `-p 9443:9443` : Expose l'interface web sécurisée de Portainer (HTTPS) sur le port 9443 de votre machine physique.
    - `-v /var/run/docker.sock:/var/run/docker.sock` : C'est le lien crucial. Il donne au conteneur Portainer la permission de discuter avec le démon Docker de l'hôte pour le contrôler.
    - `portainer-ce:latest` : Utilise la version *Community Edition* (gratuite).

### Étape 3 : Configuration initiale via l'interface web

1. Ouvrez votre navigateur web et rendez-vous sur l'adresse : `https://<IP_DE_VOTRE_SERVEUR>:9443`
2. Vous rencontrerez très probablement un avertissement de sécurité (car Portainer génère un certificat auto-signé). Acceptez le risque et poursuivez vers le site.
3. Lors de la première connexion, Portainer vous demandera de créer l'utilisateur administrateur par défaut. Choisissez un mot de passe robuste (au moins 12 caractères).
4. Cliquez sur le bouton **Create user**.
5. Sélectionnez ensuite votre environnement local (généralement pré-configuré par défaut sous l'appellation "local") et cliquez sur **Get Started**.

Vous voilà sur le tableau de bord de Portainer, avec la liste de vos images, conteneurs, réseaux et volumes !

## Vérification

Pour vous assurer que le conteneur tourne correctement en arrière-plan sur votre serveur, vous pouvez lister les conteneurs actifs :

```bash
sudo docker ps | grep portainer
```

!!! success "Résultat attendu"
    Vous devriez voir une ligne indiquant que `portainer/portainer-ce` est à l'état *Up* (en cours d'exécution) et écoute sur les ports `8000` et `9443`.

## Ressources

- [Documentation officielle de Portainer (en anglais)](https://docs.portainer.io/start/install-ce/server/docker/linux) — Guide d'installation complet.
- [Docker Hub - Portainer CE](https://hub.docker.com/r/portainer/portainer-ce) — Page de l'image officielle.