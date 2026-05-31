---
title: "Identifier les ports ouverts et les services à l’écoute avec `ss` et `lsof` sous Linux"
date: 2026-05-31
author: Nicolas BODAINE
tags:
  - linux
  - diagnostic
  - ports
  - ss
  - lsof
  - réseau
difficulty: débutant
os: Linux
status: publié
---

# Identifier les ports ouverts et les services à l’écoute avec `ss` et `lsof` sous Linux

!!! abstract "Résumé"
    Quand un service ne répond pas, il faut d’abord savoir **s’il écoute réellement**, **sur quel port**, **sur quelle adresse IP** et **quel processus** possède ce port. Ce tutoriel propose une méthode simple, reproductible et immédiatement utile en lab avec `ss`, `lsof` et `systemctl`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux, VM de lab ou serveur de test |
| Dernière mise à jour | 2026-05-31 |

## Contexte

En dépannage, beaucoup de débutants confondent plusieurs situations différentes :

- le service est **arrêté** ;
- le service est **démarré mais n’écoute pas** sur le port attendu ;
- le service écoute seulement en **local** sur `127.0.0.1` ;
- le service écoute correctement, mais le problème vient du **pare-feu** ou du **réseau**.

Avant de modifier UFW, Fail2ban, Nginx, Docker ou la configuration applicative, il faut donc répondre à une question simple :

> **Quel processus écoute réellement sur quel port ?**

Sous Linux, les deux outils les plus pratiques pour ce diagnostic sont :

- `ss` pour afficher rapidement les sockets réseau ;
- `lsof` pour relier un port à un processus et à un binaire précis.

## Prérequis

- Une machine Linux de test
- Un compte avec les droits `sudo`
- Les outils `ss` et `lsof`
- Optionnel : un service déjà installé (`ssh`, `nginx`, `apache2`, `docker`, etc.)

!!! note "Si `lsof` n’est pas encore installé"
    Sur Debian ou Ubuntu :
    ```bash
    sudo apt update
    sudo apt install -y lsof
    ```

!!! note "Si `ss` est introuvable"
    `ss` fait partie du paquet `iproute2` sur Debian et Ubuntu :
    ```bash
    sudo apt update
    sudo apt install -y iproute2
    ```

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `sudo ss -tulpn` | Afficher les ports TCP et UDP en écoute avec le nom du processus |
| `sudo ss -ltnp` | Afficher uniquement les ports TCP en écoute |
| `sudo ss -lunp` | Afficher uniquement les ports UDP en écoute |
| `sudo ss -tulpn | grep ':22'` | Rechercher un port précis |
| `sudo lsof -i -P -n` | Afficher les connexions et écoutes réseau sans résolution DNS ni noms de service |
| `sudo lsof -iTCP -sTCP:LISTEN -P -n` | Afficher uniquement les ports TCP en écoute |
| `sudo lsof -i :80 -P -n` | Identifier le processus qui utilise le port 80 |
| `sudo systemctl status ssh --no-pager` | Vérifier l’état d’un service géré par `systemd` |

## Procédure

### Étape 1 : vérifier que les outils sont disponibles

Commencez par vérifier que `ss` et `lsof` sont utilisables.

```bash
ss -V
lsof -v 2>&1 | head -n 1
```

!!! tip "Pourquoi cette étape est utile"
    En environnement minimal ou sur certaines images cloud, `lsof` n’est pas toujours installé par défaut.

### Étape 2 : afficher tous les ports en écoute avec `ss`

La commande la plus utile pour un premier diagnostic est :

```bash
sudo ss -tulpn
```

Voici la signification des options :

- `-t` : sockets **TCP** ;
- `-u` : sockets **UDP** ;
- `-l` : sockets en **écoute** ;
- `-p` : processus propriétaire du socket ;
- `-n` : affichage numérique des ports et adresses.

Exemple de sortie :

```text
Netid State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
udp   UNCONN 0      0      127.0.0.53:53   0.0.0.0:*    users:(("systemd-resolve",pid=632,fd=16))
tcp   LISTEN 0      128    0.0.0.0:22      0.0.0.0:*    users:(("sshd",pid=812,fd=3))
tcp   LISTEN 0      511    0.0.0.0:80      0.0.0.0:*    users:(("nginx",pid=1104,fd=5))
tcp   LISTEN 0      4096   127.0.0.1:8000  0.0.0.0:*    users:(("python3",pid=2541,fd=3))
```

### Étape 3 : interpréter correctement l’adresse d’écoute

La colonne `Local Address:Port` est essentielle.

- `127.0.0.1:8000` : le service écoute **uniquement en local**
- `0.0.0.0:80` : le service écoute sur **toutes les interfaces IPv4**
- `[::]:443` : le service écoute sur **toutes les interfaces IPv6**

!!! warning "Erreur classique"
    Un service en écoute sur `127.0.0.1` peut fonctionner parfaitement en local, tout en restant inaccessible depuis une autre machine du réseau.

### Étape 4 : filtrer un port précis avec `ss`

Pour vérifier rapidement si un port donné est utilisé, filtrez la sortie.

#### Vérifier le port SSH

```bash
sudo ss -tulpn | grep ':22'
```

#### Vérifier un port web

```bash
sudo ss -tulpn | grep ':80\|:443'
```

#### Vérifier un port de lab

```bash
sudo ss -tulpn | grep ':8000'
```

!!! tip "Bon réflexe"
    Si la commande ne renvoie rien, cela signifie en général que **rien n’écoute sur ce port** au moment du test.

### Étape 5 : identifier précisément le processus avec `lsof`

`ss` est excellent pour une vue globale. `lsof` est très pratique pour savoir **quel binaire** utilise un port.

#### Afficher tous les ports réseau utilisés

```bash
sudo lsof -i -P -n
```

#### Afficher seulement les services TCP en écoute

```bash
sudo lsof -iTCP -sTCP:LISTEN -P -n
```

#### Identifier le propriétaire d’un port précis

```bash
sudo lsof -i :80 -P -n
```

Exemple de résultat :

```text
COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
nginx   1104 root    5u  IPv4  21543      0t0  TCP *:80 (LISTEN)
nginx   1105 www-data 5u IPv4  21543      0t0  TCP *:80 (LISTEN)
```

Les options importantes sont :

- `-i` : filtrer les fichiers réseau ;
- `-P` : conserver les numéros de port au lieu de noms comme `http` ;
- `-n` : ne pas faire de résolution DNS.

!!! note "Pourquoi utiliser `sudo`"
    Sans `sudo`, Linux peut masquer une partie des informations sur les processus appartenant à d’autres utilisateurs.

### Étape 6 : faire un mini lab reproductible avec `python3`

Pour apprendre sans casser un vrai service, vous pouvez créer un serveur web temporaire.

Dans un premier terminal :

```bash
mkdir -p ~/lab-ports
cd ~/lab-ports
python3 -m http.server 8000 --bind 127.0.0.1
```

Le terminal reste occupé : c’est normal, le serveur tourne au premier plan.

Dans un deuxième terminal, vérifiez ce qui écoute :

```bash
sudo ss -ltnp | grep ':8000'
sudo lsof -iTCP:8000 -sTCP:LISTEN -P -n
```

Résultat attendu :

```text
LISTEN 0 5 127.0.0.1:8000 0.0.0.0:* users:(("python3",pid=2541,fd=3))
```

Puis testez localement :

```bash
curl http://127.0.0.1:8000
```

!!! success "Ce que ce lab démontre"
    Vous voyez immédiatement qu’un service peut être **actif** et **en écoute**, mais seulement sur l’adresse locale `127.0.0.1`.

Pour arrêter le serveur, revenez dans le premier terminal puis utilisez `Ctrl+C`.

### Étape 7 : comparer une écoute locale et une écoute sur toutes les interfaces

Relancez le même serveur, mais cette fois sur toutes les interfaces IPv4 :

```bash
python3 -m http.server 8000 --bind 0.0.0.0
```

Vérifiez à nouveau :

```bash
sudo ss -ltnp | grep ':8000'
```

Vous devez voir quelque chose comme :

```text
LISTEN 0 5 0.0.0.0:8000 0.0.0.0:* users:(("python3",pid=2610,fd=3))
```

Cette fois, si le pare-feu le permet et si le réseau est correct, le service peut être joint depuis une autre machine.

### Étape 8 : croiser le diagnostic avec `systemctl`

Si un service est censé être lancé automatiquement, contrôlez aussi son état côté `systemd`.

Exemples :

```bash
sudo systemctl status ssh --no-pager
sudo systemctl status nginx --no-pager
```

Méthode simple de diagnostic :

1. **`systemctl status`** : le service est-il démarré ?
2. **`ss -tulpn`** : écoute-t-il sur le bon port ?
3. **`lsof -i`** : quel processus possède le port ?
4. Si tout est correct, vérifier ensuite le **pare-feu** et le **réseau**.

## Problème

Le symptôme le plus fréquent est le suivant :

!!! failure "Le service semble démarré, mais impossible de se connecter"
    Le client affiche un timeout, un refus de connexion, ou une page inaccessible.

## Solution

Utilisez cette grille de lecture simple :

- **Aucune sortie dans `ss` pour le port attendu** → le service n’écoute pas, ou pas sur ce port
- **Le service écoute sur `127.0.0.1`** → il n’est accessible qu’en local
- **Le service écoute sur `0.0.0.0` ou `[::]`** → le problème est probablement après le service : pare-feu, routage, NAT, groupe de sécurité, proxy, etc.
- **`lsof` ne montre pas le processus attendu** → un autre programme utilise peut-être déjà le port

## Vérification

À la fin du diagnostic, vous devez être capable de répondre à ces quatre questions :

```bash
sudo ss -tulpn
sudo lsof -iTCP -sTCP:LISTEN -P -n
```

- Quel port est en écoute ?
- En TCP ou en UDP ?
- Sur quelle adresse IP ?
- Quel processus possède ce port ?

!!! success "Résultat attendu"
    Vous savez distinguer un service arrêté, un mauvais port, une écoute limitée à `127.0.0.1` et un problème situé après le service (pare-feu ou réseau).

## Glossaire

`Port en écoute`
:   Port sur lequel un processus attend des connexions entrantes.

`Socket`
:   Point d’échange utilisé par une application pour communiquer sur le réseau.

`127.0.0.1`
:   Adresse de boucle locale (*loopback*), accessible uniquement depuis la machine elle-même.

`0.0.0.0`
:   Adresse utilisée pour indiquer une écoute sur toutes les interfaces IPv4.

## Ressources

- [`ss(8)` — manpage iproute2](https://manpages.debian.org/bookworm/iproute2/ss.8.en.html) — Référence des options et de l’interprétation des sockets
- [`lsof(8)` — manpage Debian](https://manpages.debian.org/bookworm/lsof/lsof.8.en.html) — Référence pour identifier les processus et fichiers réseau
- [`systemctl` — documentation officielle systemd](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) — Vérification et gestion de l’état des services
