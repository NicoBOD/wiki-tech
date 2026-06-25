---
title: Capturer et diagnostiquer le trafic réseau en ligne de commande avec tcpdump
date: 2026-06-25
author: Nicolas BODAINE
tags:
  - tcpdump
  - reseau
  - linux
  - debug
difficulty: intermédiaire
os: Linux
status: publié
---

# Capturer et diagnostiquer le trafic réseau en ligne de commande avec tcpdump

!!! abstract "Résumé"
    Apprenez à utiliser l'outil en ligne de commande `tcpdump` pour capturer, filtrer et analyser le trafic réseau directement depuis un terminal Linux. Une compétence indispensable pour diagnostiquer des problèmes de connectivité sans interface graphique.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux |
| Dernière mise à jour | 2026-06-25 |

## Contexte

Lorsque vous administrez des serveurs Linux dépourvus d'interface graphique (GUI), il est souvent impossible de lancer des outils comme Wireshark pour analyser le trafic réseau. C'est là que `tcpdump` entre en jeu. 

Cet outil en ligne de commande permet d'écouter les interfaces réseau, de capturer les paquets en transit et de les afficher ou les sauvegarder pour une analyse ultérieure. Que ce soit pour vérifier qu'un serveur reçoit bien des requêtes web, qu'une règle de pare-feu ne bloque pas un flux, ou pour isoler une application bavarde, `tcpdump` est la référence.

## Prérequis

- Un système GNU/Linux avec un accès au terminal.
- Des privilèges d'administration (`sudo` ou `root`), car la capture de paquets nécessite un accès bas niveau aux interfaces réseau.
- L'outil `tcpdump` installé (généralement présent par défaut ou installable via `apt`, `dnf`, `pacman`...).

## Installation

Si `tcpdump` n'est pas déjà présent sur votre système :

=== "Debian / Ubuntu"

    ```bash
    sudo apt update
    sudo apt install tcpdump
    ```

=== "RHEL / Rocky / Alma"

    ```bash
    sudo dnf install tcpdump
    ```

## Procédure

### 1. Identifier l'interface réseau à écouter

Avant de lancer la capture, il faut savoir sur quelle interface réseau écouter (ex: `eth0`, `ens33`, `wlan0`).

```bash
# Lister toutes les interfaces réseau disponibles pour la capture
sudo tcpdump -D
```

Vous pouvez aussi utiliser la commande classique pour voir vos interfaces et leurs adresses IP :
```bash
ip a
```

### 2. Capture basique sur une interface

Pour commencer à écouter tout le trafic passant par l'interface `eth0` :

```bash
sudo tcpdump -i eth0
```
*(Utilisez ++ctrl+c++ pour arrêter la capture)*

!!! warning "Mode promiscuité"
    Par défaut, `tcpdump` passe l'interface en *mode promiscuité*, ce qui signifie qu'elle capture tous les paquets passant par le réseau, même ceux qui ne lui sont pas destinés.

### 3. Filtrer par adresse IP

Dans la majorité des cas, vous ne voulez capturer que le trafic concernant une machine spécifique.

```bash
# Capturer les échanges depuis et vers l'IP 192.168.1.10
sudo tcpdump -i eth0 host 192.168.1.10

# Capturer uniquement les paquets DONT la source est 192.168.1.10
sudo tcpdump -i eth0 src 192.168.1.10

# Capturer uniquement les paquets DONT la destination est 192.168.1.10
sudo tcpdump -i eth0 dst 192.168.1.10
```

### 4. Filtrer par port ou protocole

Si vous dépannez un serveur web ou un serveur DNS, vous voudrez isoler ce trafic.

```bash
# Capturer uniquement le trafic sur le port 80 (HTTP)
sudo tcpdump -i eth0 port 80

# Capturer uniquement le trafic ICMP (les ping par exemple)
sudo tcpdump -i eth0 icmp
```

### 5. Combiner des filtres (Expressions booléennes)

Vous pouvez utiliser `and` (`&&`), `or` (`||`) et `not` (`!`) pour affiner votre filtre. Pensez à utiliser des guillemets pour éviter que le terminal n'interprète certains caractères spéciaux.

```bash
# Trafic sur le port 80 OU 443 vers/depuis l'IP cible
sudo tcpdump -i eth0 "host 192.168.1.50 and (port 80 or port 443)"

# Tout le trafic SAUF le SSH (utile pour ne pas noyer la capture avec votre propre connexion distante)
sudo tcpdump -i eth0 "not port 22"
```

### 6. Rendre la sortie lisible et détaillée

Par défaut, `tcpdump` essaie de résoudre les noms d'hôtes (DNS) et les noms de ports. Cela peut ralentir l'affichage et encombrer l'écran.

```bash
# L'option -n désactive la résolution DNS (affiche les IP)
# L'option -nn désactive la résolution des ports (affiche les numéros)
sudo tcpdump -i eth0 -nn
```

Pour voir le contenu détaillé des paquets :

```bash
# -v, -vv, ou -vvv pour augmenter le niveau de verbosité (détails des en-têtes)
sudo tcpdump -i eth0 -vv

# -X affiche à la fois l'en-tête et le contenu (payload) du paquet en hexadécimal et en ASCII
sudo tcpdump -i eth0 -X port 80
```

### 7. Sauvegarder la capture dans un fichier (.pcap)

Si le trafic est trop dense pour une lecture en temps réel ou si vous souhaitez l'analyser confortablement plus tard avec Wireshark sur une machine graphique :

```bash
# L'option -w redirige la capture vers un fichier
sudo tcpdump -i eth0 -w /tmp/capture_reseau.pcap
```
*(Aucune sortie ne s'affichera à l'écran pendant l'enregistrement)*

Pour lire ce fichier depuis la ligne de commande avec `tcpdump` :
```bash
sudo tcpdump -r /tmp/capture_reseau.pcap -nn
```

## Aide-mémoire des options clés

| Option | Description |
|--------|-------------|
| `-i <interface>` | Spécifie l'interface réseau à écouter (ex: `eth0`, `any`). |
| `-n` / `-nn` | Désactive la résolution de nom (IP / Ports), accélérant la sortie. |
| `-v` / `-vv` / `-vvv` | Augmente le niveau de détails (verbosité) des en-têtes. |
| `-c <nombre>` | S'arrête après avoir capturé *n* paquets. |
| `-w <fichier.pcap>` | Écrit la capture dans un fichier au format pcap. |
| `-r <fichier.pcap>` | Lit une capture depuis un fichier pcap. |
| `-X` | Affiche le contenu des paquets en Hexadécimal et ASCII. |

## Ressources

- [Manuel officiel tcpdump (man page)](https://www.tcpdump.org/manpages/tcpdump.1.html) — Documentation exhaustive.
- [Red Hat : Comment utiliser tcpdump](https://access.redhat.com/solutions/114223) — Guide de diagnostic par l'éditeur RHEL.
