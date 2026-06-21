---
title: Diagnostiquer les problèmes matériels et pilotes sous Linux avec dmesg
date: 2026-06-21
author: Nicolas BODAINE
tags:
  - linux
  - debug
  - kernel
  - hardware
difficulty: débutant
os: Linux
status: publié
---

# Diagnostiquer les problèmes matériels et pilotes sous Linux avec dmesg

!!! abstract "Résumé"
    La commande `dmesg` (diagnostic message) est l'outil indispensable pour interroger le tampon des messages du noyau Linux (ring buffer). Elle permet de voir tout ce que le système d'exploitation détecte au niveau matériel et réseau, de la séquence de démarrage jusqu'à l'insertion d'une clé USB, ce qui en fait un outil de premier plan pour diagnostiquer les pannes matérielles ou les pilotes manquants.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Toutes distributions Linux |
| Dernière mise à jour | 2026-06-21 |

## Contexte

Lorsque vous branchez un périphérique (disque dur, clé USB, carte réseau) ou que vous rencontrez un comportement anormal sur votre serveur ou votre poste de travail (déconnexions réseau intempestives, plantages de la carte graphique, erreurs disques), il n'y a souvent aucune notification visible. Le noyau Linux enregistre pourtant minutieusement tous ces événements. L'outil `dmesg` permet de lire ces enregistrements pour identifier la source du problème.

## Prérequis

- Un accès en ligne de commande à un système Linux.
- Les droits `sudo` ou `root` (sur les distributions récentes, la lecture de `dmesg` est restreinte aux administrateurs pour des raisons de sécurité).

## Utilisation de base

### Étape 1 : Lire les messages récents

Par défaut, `dmesg` affiche tout l'historique depuis le démarrage, ce qui représente des centaines de lignes. Pour un diagnostic immédiat (par exemple après avoir branché une clé USB), on limite généralement la sortie aux dernières lignes.

```bash
sudo dmesg | tail -n 20
```

!!! tip "Afficher des dates lisibles par l'humain"
    Par défaut, `dmesg` affiche un horodatage en secondes depuis le démarrage (uptime). Ajoutez l'option `-T` ou `--ctime` pour obtenir des dates classiques.

    ```bash
    sudo dmesg -T | tail -n 20
    ```

### Étape 2 : Suivre les événements en temps réel

Si vous souhaitez diagnostiquer un périphérique USB défectueux ou un câble réseau capricieux, le meilleur moyen est de suivre les logs du noyau en temps réel, puis de provoquer l'action (débrancher et rebrancher le câble/périphérique).

```bash
sudo dmesg -w
```
*(Appuyez sur `Ctrl+C` pour quitter le suivi en direct).*

### Étape 3 : Filtrer par type d'équipement

Pour retrouver une information noyée dans la masse, il est d'usage d'associer `dmesg` à `grep`. Voici quelques mots-clés classiques.

=== "Réseau"

    Rechercher l'état des cartes réseau (link up/down) :
    ```bash
    sudo dmesg | grep -i eth
    sudo dmesg | grep -i enp
    ```

=== "Stockage (Disques / USB)"

    Rechercher les disques SCSI/SATA/USB (sda, sdb...) ou NVMe :
    ```bash
    sudo dmesg | grep -i -E "sd[a-z]|nvme"
    sudo dmesg | grep -i usb
    ```

=== "Mémoire (RAM)"

    Vérifier la détection de la RAM ou d'éventuels dépassements (OOM Killer) :
    ```bash
    sudo dmesg | grep -i memory
    sudo dmesg | grep -i "out of memory"
    ```

## Filtrage avancé intégré

Depuis les versions récentes, la commande `dmesg` possède ses propres options de filtrage, souvent plus propres que l'utilisation de `grep`.

Filtrer par **niveau de criticité** (log level). Très utile pour ne faire ressortir que les erreurs :
```bash
# Affiche uniquement les alertes critiques (emerg, alert, crit, err)
sudo dmesg --level=err,crit

# Affiche les erreurs et avertissements
sudo dmesg --level=err,warn
```

Filtrer par **composant du noyau** (facility). Par exemple pour voir uniquement les logs liés aux pilotes matériels :
```bash
sudo dmesg --facility=kern,daemon
```

## Cas concrets de pannes (Problème / Solution)

### Problème 1 : Périphérique non reconnu
Vous branchez une clé USB ou une carte Wi-Fi, mais elle n'apparaît pas dans vos interfaces.

!!! failure "Message d'erreur typique dans dmesg"
    ```text
    [ 1234.567890] usb 1-1: new high-speed USB device number 5 using xhci_hcd
    [ 1234.678901] usb 1-1: firmware: failed to load rtlwifi/rtl8192eu_nic.bin (-2)
    ```

**Solution :**
Le matériel est physiquement détecté par le port USB, mais le système n'a pas le programme (firmware) pour le piloter. Vous devez installer le paquet contenant les firmwares non libres (ex: `sudo apt install linux-firmware` ou `firmware-realtek` sur Debian).

### Problème 2 : Processus tué silencieusement (OOM)
Votre serveur web ou votre base de données s'arrête sans raison apparente et sans laisser d'erreur dans ses propres logs.

!!! failure "Message d'erreur typique dans dmesg"
    ```text
    [  567.890123] Out of memory: Killed process 1234 (mysqld) total-vm:2105124kB, anon-rss:512000kB, file-rss:0kB
    ```

**Solution :**
Le système a manqué de mémoire vive (RAM) et a fait intervenir le *Out Of Memory Killer* pour sacrifier le processus qui consommait le plus de mémoire afin de sauver le système d'exploitation. Vous devez augmenter la RAM, ajouter du swap, ou limiter la consommation du service.

## Aide-mémoire

| Commande | Action |
|----------|--------|
| `sudo dmesg -T` | Affiche l'historique complet avec des dates lisibles. |
| `sudo dmesg -w` | Suit l'apparition de nouveaux événements en temps réel. |
| `sudo dmesg -c` | Lit les logs puis vide le tampon (pratique avant un test). |
| `sudo dmesg --level=err` | N'affiche que les erreurs critiques détectées par le noyau. |

## Ressources

- [Manuel de la commande dmesg](https://man7.org/linux/man-pages/man1/dmesg.1.html) — Documentation officielle du manuel Linux.
- [Documentation du Kernel Linux](https://www.kernel.org/doc/html/latest/) — Architecture et documentation avancée du noyau.