---
title: Mesurer la bande passante réelle entre deux machines avec iperf3
date: 2026-06-09
author: Nicolas BODAINE
tags:
  - reseau
  - iperf3
  - bande-passante
  - diagnostic
  - tcp
  - udp
difficulty: débutant
os: Linux | Windows | macOS
status: publié
---

# Mesurer la bande passante réelle entre deux machines avec iperf3

!!! abstract "Résumé"
    Apprenez à utiliser `iperf3`, l'outil standard de l'industrie pour mesurer de manière fiable la bande passante maximale atteignable entre deux machines sur un réseau IP, que ce soit en TCP ou en UDP.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | GNU/Linux, Windows, macOS |
| Dernière mise à jour | 2026-06-09 |

## Contexte

Lorsque vous rencontrez des lenteurs sur un réseau, les outils classiques comme `ping` ou `traceroute` permettent de vérifier la latence et le chemin emprunté, mais ne vous informent pas sur le **débit réel** (throughput). Pour vérifier si une liaison Gigabit est capable d'atteindre sa vitesse théorique, ou pour tester la qualité d'un lien Wi-Fi ou VPN, `iperf3` est l'outil de référence. Il génère du trafic entre un client et un serveur pour mesurer la bande passante de façon empirique.

## Prérequis

- Deux machines (physiques ou virtuelles) capables de communiquer entre elles sur le réseau.
- Les droits d'installation de paquets sur les deux machines.
- Autoriser le port par défaut de `iperf3` (TCP/UDP **5201**) dans le pare-feu si nécessaire.

## Procédure

### Étape 1 : Installation

L'outil doit être installé à la fois sur la machine qui fera office de **serveur** (qui recevra le trafic) et sur celle qui sera le **client** (qui enverra le trafic).

=== "Linux (Debian/Ubuntu)"

    ```bash
    sudo apt update
    sudo apt install -y iperf3
    ```

=== "Linux (RHEL/Rocky/Alma)"

    ```bash
    sudo dnf install -y epel-release
    sudo dnf install -y iperf3
    ```

=== "Windows"

    Vous pouvez télécharger l'exécutable depuis le [site officiel d'iperf](https://iperf.fr/iperf-download.php) ou l'installer via Winget :
    ```powershell
    winget install iperf3
    ```

### Étape 2 : Lancer la machine en mode Serveur

Sur la première machine (par exemple, d'adresse IP `192.168.1.50`), démarrez `iperf3` en mode écoute (serveur).

```bash
iperf3 -s
```

Le terminal affichera qu'il écoute sur le port 5201. Laissez ce terminal ouvert.

### Étape 3 : Lancer la machine en mode Client (Test TCP par défaut)

Sur la deuxième machine (le client), lancez le test en vous connectant à l'adresse IP du serveur. Par défaut, `iperf3` effectue un test TCP de 10 secondes.

```bash
iperf3 -c 192.168.1.50
```

Vous verrez les paquets s'envoyer et un rapport final s'afficher.

### Étape 4 : Options avancées utiles

Pour affiner vos tests, voici quelques options très pratiques à utiliser **côté client** :

**Test inversé (Téléchargement)**
Par défaut, le client envoie des données au serveur (upload). Pour tester la vitesse depuis le serveur vers le client (download), ajoutez `-R` (Reverse) :
```bash
iperf3 -c 192.168.1.50 -R
```

**Test UDP (idéal pour Wi-Fi / VPN)**
Le protocole TCP adapte sa vitesse en fonction des pertes. Pour mesurer la capacité brute ou voir le taux de paquets perdus, utilisez UDP avec `-u` et spécifiez une bande passante cible avec `-b` (par exemple 100M ou 1G) :
```bash
iperf3 -c 192.168.1.50 -u -b 1G
```

**Flux parallèles**
Si vous testez un réseau très rapide (ex: 10 Gbps) ou très distant, un seul flux TCP peut ne pas suffire à saturer le lien. Utilisez `-P` pour ouvrir plusieurs flux simultanés (ex: 4 flux) :
```bash
iperf3 -c 192.168.1.50 -P 4
```

## Vérification

Une fois le test terminé, `iperf3` affiche un résumé similaire à celui-ci (côté client) :

```text hl_lines="4"
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-10.00  sec  1.10 GBytes   942 Mbits/sec    0             sender
[  5]   0.00-10.00  sec  1.10 GBytes   940 Mbits/sec                  receiver
```

!!! success "Interprétation"
    - **Transfer** : La quantité de données échangées (ici 1.10 Go).
    - **Bitrate** : Le débit moyen mesuré (ici 942 Mbits/sec, ce qui est excellent pour un réseau Gigabit théorique de 1000 Mbps).
    - **Retr** (Retransmits) : Le nombre de paquets TCP renvoyés. Un chiffre élevé (plus de quelques dizaines) indique des instabilités, des collisions ou une saturation sur le réseau.

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `iperf3 -s` | Lance iperf3 en mode serveur (écoute). |
| `iperf3 -c <IP>` | Test standard (Client vers Serveur). |
| `iperf3 -c <IP> -R` | Test inversé (Serveur vers Client). |
| `iperf3 -c <IP> -u -b 1G` | Test UDP avec un débit cible de 1 Gbps. |
| `iperf3 -c <IP> -p 8080` | Utilise un port spécifique au lieu du 5201 par défaut. |

## Ressources

- [Site officiel iperf](https://iperf.fr/) — Téléchargements et documentation.
- [ESnet iperf3 documentation](https://software.es.net/iperf/) — Documentation complète maintenue par le Département de l'Énergie américain.