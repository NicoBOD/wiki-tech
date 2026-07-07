---
title: UFW sur Ubuntu Server — ouvrir seulement SSH, HTTP et HTTPS
date: 2026-05-29
author: Nicolas BODAINE
tags:
  - ubuntu
  - ufw
  - pare-feu
  - openssh
  - nginx
  - securite
difficulty: débutant
os: Ubuntu 24.04
status: publié
---

# UFW sur Ubuntu Server — ouvrir seulement SSH, HTTP et HTTPS

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour activer un pare-feu simple sur Ubuntu Server avec **UFW** en n'autorisant que les flux utiles d'un petit serveur de lab : **SSH** pour l'administration, **HTTP** et **HTTPS** pour un site web.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu Server 24.04 |
| Dernière mise à jour | 2026-05-29 |

## Contexte

Quand on installe une VM Ubuntu Server, beaucoup de débutants pensent d'abord à installer les services, puis à la sécurité plus tard.

C'est une erreur classique : un serveur de test exposé trop vite avec des ports ouverts inutilement devient un mauvais réflexe d'administration.

**UFW** (*Uncomplicated Firewall*) simplifie la gestion du pare-feu Linux basé sur `iptables`/`nftables` selon la version du système. Sur Ubuntu, c'est l'outil le plus simple pour démarrer proprement.

Dans ce TP, l'objectif est de configurer une base saine :

- **refuser les connexions entrantes par défaut** ;
- **autoriser les connexions sortantes** ;
- **ouvrir SSH** pour administrer la machine ;
- **ouvrir HTTP/HTTPS** si la machine héberge un site web.

## Prérequis

- Une VM ou un serveur de test sous **Ubuntu Server 24.04**
- Un compte avec les droits `sudo`
- Un accès **console** à la VM ou une solution de secours en cas d'erreur
- Le service **SSH** installé si vous administrez la machine à distance

!!! warning "Évitez de vous couper l'accès SSH"
    Si vous travaillez à distance, **autorisez SSH avant d'activer UFW**.
    Gardez si possible une console d'administration ouverte dans l'hyperviseur, l'ILO, l'IPMI ou l'interface cloud.

## Procédure

### Étape 1 : vérifier l'installation de UFW

Sur Ubuntu, UFW est souvent présent par défaut, mais il vaut mieux contrôler son état.

```bash
sudo ufw status verbose
```

Si la commande n'existe pas, installez UFW :

```bash
sudo apt update
sudo apt install -y ufw
```

!!! success "Résultat attendu"
    La commande `ufw status verbose` doit répondre sans erreur.
    Au début du TP, l'état est généralement `inactive`.

### Étape 2 : vérifier que le service SSH est bien installé

Avant d'ouvrir un port, il faut confirmer que le service existe réellement.

```bash
systemctl status ssh --no-pager
ss -tulpn | grep ':22'
```

Si SSH n'est pas encore installé :

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

!!! tip "Pourquoi cette vérification est utile"
    Beaucoup d'apprenants ouvrent le port `22/tcp` dans le pare-feu alors que le service SSH n'est pas encore démarré. Le port semble "autorisé", mais la connexion reste impossible.

### Étape 3 : afficher les profils d'applications disponibles

UFW sait gérer des **profils applicatifs** fournis par certains paquets.
C'est plus lisible pour un débutant que de mémoriser tous les ports.

```bash
sudo ufw app list
```

Vous verrez souvent des profils comme :

```text
Available applications:
  Nginx Full
  Nginx HTTP
  Nginx HTTPS
  OpenSSH
```

Pour afficher le détail d'un profil :

```bash
sudo ufw app info OpenSSH
```

### Étape 4 : définir la politique par défaut

On applique une règle simple et saine :

- tout ce qui entre est refusé par défaut ;
- tout ce qui sort est autorisé.

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

### Étape 5 : autoriser SSH avant l'activation

Pour éviter de bloquer l'administration distante, ouvrez d'abord SSH.

```bash
sudo ufw allow OpenSSH
```

Si le profil `OpenSSH` n'est pas disponible, utilisez le port directement :

```bash
sudo ufw allow 22/tcp
```

Vérifiez les règles déjà présentes :

```bash
sudo ufw status numbered
```

### Étape 6 : autoriser HTTP et HTTPS pour un serveur web

Si la machine héberge un site ou une application web, ouvrez les ports nécessaires.

#### Cas 1 : vous utilisez Nginx

```bash
sudo ufw allow 'Nginx Full'
```

Le profil `Nginx Full` ouvre :

- le port **80/tcp** pour HTTP ;
- le port **443/tcp** pour HTTPS.

#### Cas 2 : vous voulez ouvrir les ports manuellement

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

!!! note "Bon réflexe"
    N'ouvrez que les ports réellement utiles au rôle du serveur.
    Une VM de lab utilisée uniquement pour SSH n'a pas besoin d'ouvrir le web.

### Étape 7 : activer le pare-feu

Quand les règles utiles sont prêtes, activez UFW.

```bash
sudo ufw enable
```

Confirmez avec `y` si une demande de validation s'affiche.

Ensuite, contrôlez l'état détaillé :

```bash
sudo ufw status verbose
```

Exemple de résultat attendu :

```text
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW IN    Anywhere
Nginx Full                 ALLOW IN    Anywhere
OpenSSH (v6)               ALLOW IN    Anywhere (v6)
Nginx Full (v6)            ALLOW IN    Anywhere (v6)
```

### Étape 8 : renforcer un peu SSH avec `limit`

UFW permet de limiter des tentatives répétées sur SSH.
Ce n'est pas un remplacement complet de **Fail2ban**, mais c'est une bonne première mesure de lab.

```bash
sudo ufw limit OpenSSH
```

Si vous aviez déjà une règle `allow OpenSSH`, UFW peut créer une règle supplémentaire plus restrictive.
Vérifiez ensuite le résultat :

```bash
sudo ufw status numbered
```

!!! tip "Approche pédagogique"
    Pour un premier TP, commencez par `allow OpenSSH`, vérifiez que l'accès fonctionne, puis testez `limit OpenSSH` dans un second temps.

### Étape 9 : supprimer ou corriger une règle

En entraînement, on fait souvent des essais. UFW permet de retirer une règle facilement.

Afficher les règles numérotées :

```bash
sudo ufw status numbered
```

Exemple de suppression par numéro :

```bash
sudo ufw delete 2
```

Exemple de suppression par expression complète :

```bash
sudo ufw delete allow 80/tcp
```

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `sudo ufw status verbose` | Afficher l'état détaillé du pare-feu |
| `sudo ufw status numbered` | Afficher les règles avec un numéro |
| `sudo ufw default deny incoming` | Refuser les connexions entrantes par défaut |
| `sudo ufw default allow outgoing` | Autoriser les connexions sortantes par défaut |
| `sudo ufw allow OpenSSH` | Autoriser l'administration SSH |
| `sudo ufw allow 80/tcp` | Autoriser HTTP |
| `sudo ufw allow 443/tcp` | Autoriser HTTPS |
| `sudo ufw enable` | Activer le pare-feu |
| `sudo ufw disable` | Désactiver temporairement le pare-feu |
| `sudo ufw delete <règle>` | Supprimer une règle |

## Vérification

Après configuration, vérifiez trois points.

### 1. Le pare-feu est actif

```bash
sudo ufw status verbose
```

!!! success "Résultat attendu"
    L'état doit être `active` avec une politique `deny (incoming)`.

### 2. Le service SSH répond toujours

Depuis une autre machine du lab :

```bash
ssh utilisateur@IP_DU_SERVEUR
```

!!! success "Résultat attendu"
    La connexion SSH doit toujours fonctionner.

### 3. Les ports web répondent si un serveur web est installé

Depuis une autre machine du lab :

```bash
curl -I http://IP_DU_SERVEUR
curl -kI https://IP_DU_SERVEUR
```

!!! success "Résultat attendu"
    Vous devez obtenir un en-tête HTTP, par exemple `HTTP/1.1 200 OK` ou `HTTP/1.1 301 Moved Permanently` selon la configuration du serveur web.

## Checklist

- [x] UFW installé ou vérifié
- [x] SSH autorisé avant activation
- [x] Politique par défaut configurée
- [x] HTTP/HTTPS ouverts uniquement si nécessaire
- [x] Pare-feu activé
- [x] Accès SSH revalidé après changement

## Glossaire

`UFW`
:   *Uncomplicated Firewall*, interface simplifiée pour gérer le pare-feu sur Ubuntu.

`SSH`
:   Protocole d'administration distante sécurisé, très utilisé pour gérer les serveurs Linux.

`HTTP / HTTPS`
:   Protocoles utilisés pour publier un site ou une application web.

`Politique par défaut`
:   Comportement appliqué par le pare-feu quand aucun règle explicite ne correspond à un trafic.

## Ressources

- [Ubuntu Server documentation — Set up a firewall](https://documentation.ubuntu.com/server/how-to/security/firewalls/) — Documentation officielle Ubuntu Server, y compris la gestion des profils applicatifs
- [Manpage `ufw(8)` pour Ubuntu 24.04](https://manpages.ubuntu.com/manpages/noble/man8/ufw.8.html) — Référence des commandes UFW
