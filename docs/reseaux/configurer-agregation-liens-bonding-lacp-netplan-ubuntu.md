---
title: Configurer une agrégation de liens (Bonding/LACP) avec Netplan sous Ubuntu
date: 2026-06-26
author: Nicolas BODAINE
tags:
  - netplan
  - bonding
  - lacp
  - ubuntu
  - reseau
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Configurer une agrégation de liens (Bonding/LACP) avec Netplan sous Ubuntu

!!! abstract "Résumé"
    L'agrégation de liens (ou bonding / teaming) permet de regrouper plusieurs interfaces réseau physiques en une seule interface logique. Cela offre de la redondance (si un câble ou un port switch lâche) et/ou une augmentation de la bande passante globale. Ce tutoriel explique comment configurer un bonding LACP (802.3ad) via Netplan sur Ubuntu Server.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 22.04 / 24.04 |
| Dernière mise à jour | 2026-06-26 |

## Contexte

Dans un environnement de production (ex: un serveur de virtualisation ou de stockage), s'appuyer sur une seule carte réseau est un point individuel de défaillance (SPOF). En configurant un *bonding* en mode LACP, vous demandez au serveur et au switch de discuter ensemble pour fusionner dynamiquement plusieurs liens.

## Prérequis

- Un serveur Ubuntu avec au moins deux interfaces réseau physiques disponibles (ex: `eth0` et `eth1` ou `enp3s0` et `enp4s0`).
- Un switch (commutateur) en face configuré pour supporter LACP (Link Aggregation Control Protocol - 802.3ad) sur les ports connectés au serveur.
- Les privilèges `root` ou l'accès à `sudo`.

## Procédure

### Étape 1 : Identifier les interfaces réseau

Avant de modifier la configuration, listez vos interfaces réseau pour identifier celles que vous allez agréger.

```bash
ip link show
```

Imaginons que nous avons deux interfaces : `enp3s0` et `enp4s0`.

### Étape 2 : Créer la configuration Netplan

Sur les versions récentes d'Ubuntu Server, la configuration réseau est gérée par Netplan, dont les fichiers YAML se trouvent dans `/etc/netplan/`.

Créez ou éditez le fichier de configuration existant (souvent `00-installer-config.yaml` ou `50-cloud-init.yaml`) :

```bash
sudo nano /etc/netplan/01-netcfg.yaml
```

Insérez la configuration suivante. **Attention à l'indentation** (qui est stricte en YAML, n'utilisez pas de tabulations, seulement des espaces) :

```yaml title="/etc/netplan/01-netcfg.yaml"
network:
  version: 2
  ethernets:
    enp3s0:
      dhcp4: false
      dhcp6: false
    enp4s0:
      dhcp4: false
      dhcp6: false
  bonds:
    bond0:
      interfaces:
        - enp3s0
        - enp4s0
      addresses:
        - 192.168.1.50/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 1.1.1.1
          - 8.8.8.8
      parameters:
        mode: 802.3ad
        transmit-hash-policy: layer2+3
        mii-monitor-interval: 100
```

!!! tip "Explication des paramètres"
    - `mode: 802.3ad` : Active le protocole LACP. D'autres modes existent comme `active-backup` si votre switch ne supporte pas LACP.
    - `transmit-hash-policy: layer2+3` : Définit la méthode de répartition de charge, utilisant les adresses MAC et IP.
    - `mii-monitor-interval: 100` : Vérifie l'état du lien toutes les 100 millisecondes.

### Étape 3 : Appliquer la configuration

Avant d'appliquer, il est recommandé de tester la syntaxe du fichier :

```bash
sudo netplan try
```

Si le test est concluant, vous pouvez appliquer la configuration de manière permanente :

```bash
sudo netplan apply
```

## Vérification

Pour vérifier que votre agrégation fonctionne correctement, observez le fichier spécial généré par le noyau Linux :

```bash
cat /proc/net/bonding/bond0
```

!!! success "Résultat attendu"
    Vous devriez voir `Bonding Mode: IEEE 802.3ad Dynamic link aggregation`, et un peu plus bas, l'état de chaque interface (`MII Status: up`). Si les compteurs `Aggregator ID` sont identiques pour toutes les interfaces, cela signifie que le switch a bien négocié l'agrégation LACP !

Vous pouvez aussi vérifier l'adresse IP de votre nouvelle interface `bond0` :

```bash
ip a show bond0
```

## Ressources

- [Documentation Netplan - Bonding](https://netplan.readthedocs.io/en/stable/examples/#how-to-configure-bonding) — Exemples officiels de configuration.
- [Ubuntu Server Guide - Network Configuration](https://ubuntu.com/server/docs/network-configuration) — Documentation Ubuntu sur le réseau.
