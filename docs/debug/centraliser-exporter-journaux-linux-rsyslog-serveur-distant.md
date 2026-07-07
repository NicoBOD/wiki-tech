---
title: "Centraliser et exporter les journaux Linux avec rsyslog vers un serveur de logs distant"
date: 2026-07-04
author: Nicolas BODAINE
tags:
  - linux
  - rsyslog
  - logs
  - debug
  - reseau
difficulty: intermédiaire
os: Ubuntu 24.04 / Debian 12
status: publié
---

# Centraliser et exporter les journaux Linux avec rsyslog vers un serveur de logs distant

!!! abstract "Résumé"
    Sur une flotte de serveurs Linux, fouiller les journaux machine par machine devient vite ingérable. `rsyslog` — le daemon de logs installé par défaut sur la plupart des distributions — sait à la fois **recevoir** les journaux envoyés par d'autres machines et **les relayer** vers un collecteur central. Ce tutoriel met en place, sur deux VM, une chaîne complète : un client qui exporte ses logs, un serveur qui les reçoit et les trie par origine dans `/var/log/remote/`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 / Debian 12 (2 VM) |
| Dernière mise à jour | 2026-07-04 |

## Contexte

Quand on gère plusieurs serveurs (web, base de données, pare-feu…), chaque machine conserve ses propres journaux dans `/var/log/`. En cas d'incident — une intrusion, un service qui tombe, une saturation disque — il faut se connecter à chaque machine pour reconstituer le scénario. C'est lent, et les attaquants savent effacer leurs traces localement.

La bonne pratique, recommandée notamment par l'ANSSI, est la **centralisation des journaux** : expédier en temps réel les logs vers un serveur dédié, idéalement en accès très restreint. `rsyslog` est l'outil de référence pour cela sur Debian/Ubuntu : il est déjà installé, parle le protocole Syslog normalisé par la RFC 5424, et sait router les messages selon l'hôte source, la priorité ou le programme émetteur.

Ce TP reproduit une chaîne de centralisation minimale mais réaliste, entièrement reproductible dans un lab avec deux machines virtuelles.

## Prérequis

- Deux machines virtuelles (ou conteneurs LXC) sous **Ubuntu 24.04** ou **Debian 12** :
    - **`logs-srv`** (serveur de collecte) — IP `192.168.56.20`
    - **`web-client`** (client qui exporte) — IP `192.168.56.21`
- Accès `sudo` sur les deux machines.
- Les deux VM doivent pouvoir se pinguer :
    ```bash
    # Depuis web-client
    ping -c 2 192.168.56.20
    ```
- `rsyslog` est présent par défaut. Vérifier :
    ```bash
    systemctl is-active rsyslog
    # attendu : active
    rsyslogd -v
    ```
- Pare-feu désactivé ou configuré (voir Étape 1 côté serveur) sur le port **514/UDP**.

!!! warning "Ne jamais exposer un collecteur rsyslog sur Internet"
    Le protocole Syslog historique (UDP 514, texte clair) n'est ni chiffré ni authentifié. On ne l'utilise que sur un réseau isolé ou privé (LAN de lab, VLAN dédié). Pour un déploiement de production, on chiffrera avec **TLS** (module `imtcp` + `gtls`), hors scope de cette introduction.

## Architecture du lab

```
┌─────────────────┐   UDP 514    ┌─────────────────────┐
│   web-client    │ ───────────▶ │      logs-srv       │
│  192.168.56.21  │  /var/log/*  │  192.168.56.20      │
│  rsyslog client │              │  rsyslog serveur    │
└─────────────────┘              │  /var/log/remote/   │
                                 └─────────────────────┘
```

Le client envoie une copie de tous ses journaux ; le serveur les range dans un dossier dédié, un fichier **par hôte source**, ce qui permet de relire les logs de `web-client` sans mélange.

## Procédure

### Étape 1 : Configurer le serveur de collecte (`logs-srv`)

`rsyslog` modules et règles se configurent dans `/etc/rsyslog.conf` et dans des fichiers `/etc/rsyslog.d/*.conf`. On va :

1. Activer la réception UDP sur le port 514.
2. Créer un **template** qui range les logs distants dans `/var/log/remote/<nom-hôte>.log`.
3. Stocker les logs reçus via le réseau **avant** les règles de fichiers locaux, pour éviter qu'ils ne tombent dans `/var/log/syslog`.

Créer un fichier dédié (plus propre que d'éditer `rsyslog.conf`) :

```bash
sudo nano /etc/rsyslog.d/10-remote.conf
```

Coller :

```bash
# 1. Charger le module de réception UDP
module(load="imudp")
input(type="imudp" port="514")

# 2. Template : un fichier par hôte source, horodaté
template(name="RemotePerHost" type="string"
         string="/var/log/remote/%fromhost%/%$year%%$month%%$day%.log")

# 3. Router les messages reçus du réseau vers le template
if ($inputname == "imudp") then {
    action(type="omfile" dynaFile="RemotePerHost")
    stop   # ne pas retomber dans les règles par défaut (syslog)
}
```

Explications :

- `module(load="imudp")` active la **entrée** UDP ; `input(...)` ouvre le port 514.
- `%fromhost%` est une propriété dynamique : `rsyslog` injecte le nom d'hôte du client émetteur, donc chaque machine source obtient son propre dossier sous `/var/log/remote/`.
- `stop` arrête le traitement du message : il va dans le fichier distant dédié, pas dans `/var/log/syslog`.

Créer le dossier de stockage et redémarrer :

```bash
sudo mkdir -p /var/log/remote
sudo chown syslog:adm /var/log/remote
sudo systemctl restart rsyslog
sudo systemctl status rsyslog --no-pager
```

Vérifier que le port 514 écoute :

```bash
sudo ss -lntu | grep ':514'
# attendu : udp  UNCONN  ...  0.0.0.0:514  ...
```

Si `ufw` est actif, ouvrir le port :

```bash
sudo ufw allow 514/udp
```

!!! tip "Le module imtcp pour du TCP fiable"
    Pour ne pas perdre de messages en cas de pic de charge, préférez TCP : remplacez `imudp` par `module(load="imtcp")` et `input(type="imtcp" port="514")`. TCP ajoute cependant de la latence et consomme plus ; UDP reste standard pour du Syslog simple.

### Étape 2 : Configurer le client (`web-client`)

Côté client, on charge le module de **sortie** réseau et on déclare une règle `*.* @@serveur:514` qui expédie tout vers le serveur.

```bash
sudo nano /etc/rsyslog.d/20-forward.conf
```

Coller :

```bash
# Charger le module de sortie réseau
module(load="omudp")

# Expedier TOUS les journaux (toutes priorités) vers logs-srv en UDP
*.* action(type="omudp" target="192.168.56.20" port="514")
```

> **Syntaxe alternative** sans module explicite : `*.* @192.168.56.20:514` (un seul `@` = UDP ; `@@` = TCP). C'est la forme historique, toujours valable.

Conserver une copie locale (les logs restent dans `/var/log/syslog` sur le client) — c'est le comportement par défaut, on n'a rien à interdire. On a donc à la fois :

- les logs **locaux** (pour un débogage immédiat) ;
- les logs **centralisés** sur `logs-srv` (pour la post-mortem et l'audit).

Redémarrer :

```bash
sudo systemctl restart rsyslog
sudo systemctl status rsyslog --no-pager
```

### Étape 3 : Émettre un message de test et vérifier la chaîne

Depuis `web-client`, générer un message Syslog avec `logger` (commande fournie par `util-linux`, déjà installée) :

```bash
logger -t LAB_TEST "salut depuis web-client, test de centralisation"
```

Côté serveur `logs-srv`, vérifier l'arrivée :

```bash
sudo ls /var/log/remote/
# attendu : un dossier portant le nom (ou l'IP) de web-client

sudo find /var/log/remote/ -type f -exec tail -n 5 {} +
```

On doit voir apparaître une ligne du type :

```text
Jul  4 19:42:11 web-client LAB_TEST[1234]: salut depuis web-client, test de centralisation
```

!!! success "Résultat attendu"
    Le message arrive sur `logs-srv` rangé dans `/var/log/remote/web-client/AAAAMMJJ.log`. La chaîne d'export fonctionne.

Si rien n'arrive, passer à la section « Dépannage » ci-dessous.

### Étape 4 : Filtrer et ne router que certaines priorités

Envoyer **tout** (`*.*`) est simple mais verbeux. En pratique, on peut vouloir n'expédier que les erreurs et alertes pour économiser la bande passante. Sur le **client**, remplacez la règle `20-forward.conf` par :

```bash
module(load="omudp")

# N'expédier que les priorités WARNING (4) et plus graves (0=emerg ... 3=err)
*.warning;*.err;*.crit;*.alert;*.emerg action(type="omudp" target="192.168.56.20" port="514")
```

Tester avec deux messages de priorité différente :

```bash
logger -p user.info "INFO — ne doit PAS partir vers le serveur"
logger -p user.warning "WARN — doit arriver sur logs-srv"
```

Sur `logs-srv`, seules les lignes de priorité `warning` et supérieure doivent apparaître dans `/var/log/remote/web-client/AAAAMMJJ.log`.

### Étape 5 : Garder une trace durable avec logrotate

Un collecteur qui ne rotated pas ses fichiers finit par saturer son propre disque. `logrotate` est déjà présent sous Ubuntu/Debian ; on ajoute une politique pour le dossier distant.

```bash
sudo nano /etc/logrotate.d/remote-logs
```

Coller :

```bash
/var/log/remote/*/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 syslog adm
}
```

Tester sans attendre le lendemain :

```bash
sudo logrotate -d /etc/logrotate.d/remote-logs   # simulation (dry-run)
sudo logrotate -f /etc/logrotate.d/remote-logs   # force réelle
```

## Vérification

!!! checklist "Checklist de validation"
    - [x] Le port `514/udp` écoute sur `logs-srv` (`ss -lntu | grep 514`).
    - [x] Un `logger` depuis `web-client` apparaît dans `/var/log/remote/<hôte>/AAAAMMJJ.log` sur `logs-srv`.
    - [x] `rsyslog` est `active` sur les deux VM (`systemctl is-active rsyslog`).
    - [x] Les fichiers `/var/log/remote/.../*.log` appartiennent à `syslog:adm`.
    - [x] `logrotate -d /etc/logrotate.d/remote-logs` ne renvoie aucune erreur.

## Dépannage

| Symptôme | Cause probable | Action |
|----------|----------------|--------|
| Rien n'arrive sur `logs-srv` | `imudp` non chargé ou service non redémarré | `sudo systemctl restart rsyslog` ; vérifier `sudo ss -lntu \| grep 514` |
| Rien n'arrive (encore) | Pare-feu bloque UDP 514 | `sudo ufw allow 514/udp` ou `sudo iptables -L -n` |
| Message d'erreur « imudp: module not found » | Ubuntu minimaliste sans le paquet de modules | `sudo apt install rsyslog` puis `rsyslogd -v` ≥ 8.x |
| Le fichier distant contient tout du *serveur* | La règle `if ($inputname=="imudp")` est placée **après** les règles locales | Mettre `10-remote.conf` (préfixe le plus petit possible, ex. `00-remote.conf` si nécessaire) |
| Logs en double dans `/var/log/syslog` | On a oublié `stop` dans le bloc `imudp` | Ajouter `stop` dans le bloc `if (...){...}` côté serveur |

Activer le debug de `rsyslog` côté serveur pour voir le flux entrant :

```bash
sudo systemctl stop rsyslog
sudo rsyslogd -dn   # debug interactif, Ctrl+C pour quitter
```

## Aide-mémoire

| Commande / Action | Description |
|--------------------|-------------|
| `logger -t APP "msg"` | Envoyer un message Syslog local |
| `logger -p user.warning "msg"` | Envoyer un message avec une priorité précise |
| `rsyslogd -v` | Afficher la version de rsyslog |
| `rsyslogd -dn` | Lancer en mode debug interactif (foreground) |
| `sudo ss -lntu \| grep 514` | Vérifier l'écoute UDP/TCP 514 |
| `*.* @ip:514` | Syntaxe historique : tout envoyer en UDP vers `ip:514` |
| `*.* @@ip:514` | Idem en TCP |

| Propriété rsyslog | Signification |
|--------------------|---------------|
| `%fromhost%` | Nom d'hôte du client expéditeur |
| `%hostname%` | Nom d'hôte **local** (serveur) |
| `%$year% %$month% %$day%` | Date du message (mode template dynamique) |
| `module(load="imudp")` | Module d'entrée UDP (serveur) |
| `module(load="omudp")` | Module de sortie UDP (client) |
| `module(load="imtcp")` | Module d'entrée TCP (serveur fiable) |

## Glossaire

rsyslog
:   Daemon de gestion des journaux issu du projet Debian/Ubuntu, dérivé du `syslogd` classique. Surcouche très performante (multifilaire, plus de quarante modules) du protocole Syslog original.

Syslog
:   Protocole et format de message normalisé par la RFC 5424 ("The Syslog Protocol"). Chaque message contient une priorité (facility + severity), un horodatage, un nom d'hôte, un programme et un texte.

Facility / Severity
:   Deux axes de classification d'un message Syslog. La **facility** identifie l'origine (kern, user, mail, auth…), la **severity** la gravité (de `emerg`=0 à `debug`=7).

Template
:   Structure de mise en forme ou de routage de rsyslog. Permet, par exemple, de décider dynamiquement du nom de fichier de sortie en fonction de l'hôte source (`%fromhost%`).

logrotate
:   Outil standards de rotation/compression des fichiers de logs sous Linux. Exploité ici pour limiter la croissance du dossier `/var/log/remote/`.

## Ressources

- [Documentation officielle rsyslog](https://www.rsyslog.com/doc/) — Référence des modules `imudp`, `omudp`, templates, actions.
- [RFC 5424 — The Syslog Protocol (IETF)](https://www.rfc-editor.org/rfc/rfc5424) — Format normalisé des messages Syslog.
- [Ubuntu Server Guide — Logging](https://help.ubuntu.com/lts/serverguide/log-files.html) — Vue d'ensemble de rsyslog sur Ubuntu Server.
- [Debian Administrator's Handbook — syslog & rsyslog](https://www.debian.org/doc/manuals/debian-handbook/sect.syslog.en.html) — Comprendre l'écosystème Syslog sous Debian.
- [ANSSI — Recommandations relatives à l'exploitation des journaux](https://messervices.cyber.gouv.fr/documents-guides/anssi-guide-recommandations_securite_architecture_systeme_journalisation.pdf) — Guide d'hygiène : justifications de la centralisation des logs en environnement professionnel.
- Manpage locale : `man rsyslogd`, `/usr/share/doc/rsyslog/`.
