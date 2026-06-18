---
title: Cartographier et analyser les ports d'un réseau avec Nmap
date: 2026-06-18
author: Nicolas BODAINE
tags:
  - nmap
  - reseau
  - scan
  - cybersecurite
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Cartographier et analyser les ports d'un réseau avec Nmap

!!! abstract "Résumé"
    Apprenez à utiliser Nmap, l'outil incontournable d'exploration réseau et d'audit de sécurité, pour identifier les hôtes actifs, les ports ouverts et les services en cours d'exécution sur votre réseau local.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 (ou toute distribution Linux) |
| Dernière mise à jour | 2026-06-18 |

## Contexte

Dans le cadre de l'administration réseau ou de l'audit de sécurité (pentest), la première étape consiste souvent à comprendre la topologie du réseau cible et à identifier les points d'entrée potentiels. **Nmap** (Network Mapper) est le scanner de ports de référence. Il permet de découvrir les machines connectées, les ports ouverts, les services qui tournent derrière ces ports, et parfois même le système d'exploitation utilisé.

!!! warning "Avertissement Légal"
    Nmap est un outil puissant. Ne scannez **jamais** un réseau ou un serveur qui ne vous appartient pas ou pour lequel vous n'avez pas d'autorisation explicite et écrite. Restez dans un environnement de test local (lab) ou sur vos propres machines.

## Prérequis

- Un système Linux (Ubuntu/Debian, CentOS/RHEL, etc.).
- Les droits d'administrateur (`sudo`) pour certains types de scan (notamment le scan SYN).

## Procédure

### Étape 1 : Installation de Nmap

Nmap est présent dans les dépôts officiels de la grande majorité des distributions Linux.

=== "Ubuntu / Debian"

    ```bash
    sudo apt update
    sudo apt install -y nmap
    ```

=== "CentOS / RHEL / Fedora"

    ```bash
    sudo dnf install -y nmap
    ```

Vérifiez que l'installation a réussi :

```bash
nmap --version
```

### Étape 2 : Découverte des hôtes (Ping Scan)

Avant de scanner les ports d'une machine, on vérifie souvent quelles machines sont actives sur le réseau. L'option `-sn` (anciennement `-sP`) indique à Nmap de ne faire qu'une découverte d'hôtes sans scanner les ports.

Pour scanner votre réseau local (par exemple `192.168.1.0/24`) :

```bash
nmap -sn 192.168.1.0/24
```

!!! success "Résultat attendu"
    Nmap listera toutes les adresses IP ayant répondu, ainsi que leur adresse MAC si vous êtes sur le même sous-réseau.

### Étape 3 : Scanner les ports d'une machine spécifique

Une fois l'IP cible identifiée (ex: `192.168.1.50`), on peut lancer un scan de ports classique.

**Scan TCP Connect (`-sT`)** : Le scan de base sans privilèges root. Il complète la poignée de main TCP (3-way handshake).

```bash
nmap -sT 192.168.1.50
```

**Scan SYN (`-sS`)** : Le scan par défaut si vous êtes root. Plus discret et plus rapide, il envoie un paquet SYN et analyse la réponse sans terminer la connexion. C'est le plus couramment utilisé.

```bash
sudo nmap -sS 192.168.1.50
```

### Étape 4 : Détection de version et d'OS

Connaître un port ouvert c'est bien, savoir quel service et quelle version tournent derrière, c'est mieux.

**Détection de version (`-sV`)** :

```bash
sudo nmap -sV 192.168.1.50
```

**Détection du système d'exploitation (`-O`)** :

```bash
sudo nmap -O 192.168.1.50
```

**Le scan complet ("Agressif" : `-A`)** : Regroupe la détection d'OS, de version, l'utilisation des scripts Nmap par défaut (`-sC`) et le traceroute. Très verbeux et "bruyant" sur le réseau.

```bash
sudo nmap -A 192.168.1.50
```

### Étape 5 : Accélérer et optimiser le scan

Vous pouvez spécifier les ports exacts avec `-p` et contrôler la vitesse avec `-T` (de 0 à 5).

Pour scanner rapidement (`-T4`) tous les 65535 ports (`-p-`) d'une machine :

```bash
sudo nmap -p- -T4 192.168.1.50
```

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `nmap <IP>` | Scan basique des 1000 ports les plus courants. |
| `nmap -sn <CIDR>` | "Ping scan", découvre les hôtes actifs sur un sous-réseau sans scanner les ports. |
| `nmap -p 22,80,443 <IP>` | Scan uniquement les ports 22, 80 et 443. |
| `nmap -p- <IP>` | Scan l'intégralité des 65535 ports. |
| `sudo nmap -sS <IP>` | "Stealth SYN scan", rapide et nécessite les droits root. |
| `nmap -sV <IP>` | Détecte les versions des services en écoute. |
| `sudo nmap -O <IP>` | Tente d'identifier le système d'exploitation (OS). |

## Ressources

- [Documentation officielle Nmap](https://nmap.org/book/man.html) — Guide de référence.
- [SecNumacadémie (ANSSI)](https://secnumacademie.gouv.fr/) — Sensibilisation et cours de sécurité incluant les bases de la cartographie.
- [OWASP Testing Guide](https://owasp.org/) — Guides de bonnes pratiques pour les tests d'intrusion.
