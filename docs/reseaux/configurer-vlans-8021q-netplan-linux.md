---
title: Configurer des VLANs (802.1q) sur un serveur Linux avec Netplan
date: 2026-06-20
author: Nicolas BODAINE
tags:
  - reseaux
  - vlan
  - netplan
  - linux
  - 802.1q
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Configurer des VLANs (802.1q) sur un serveur Linux avec Netplan

!!! abstract "Résumé"
    Ce tutoriel explique comment configurer une interface réseau Linux pour qu'elle puisse communiquer sur plusieurs VLANs (norme 802.1q) en utilisant **Netplan**. Cette configuration est indispensable lorsque votre serveur est connecté à un port de switch configuré en mode "Trunk" (ou *tagged*).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 (ou toute distribution utilisant Netplan) |
| Dernière mise à jour | 2026-06-20 |

## Contexte

En entreprise ou en laboratoire, un serveur physique ou une machine virtuelle doit souvent accéder à plusieurs réseaux isolés (VLANs). Au lieu d'ajouter une carte réseau physique pour chaque réseau, on utilise le standard **802.1q**. Cela permet de faire transiter plusieurs VLANs sur un seul câble, via un port de switch configuré en **Trunk**.

Côté serveur Linux, il faut "découper" cette interface physique en plusieurs **interfaces virtuelles**, chacune associée à un ID de VLAN (le *VLAN tag*). Sous les distributions modernes basées sur Debian/Ubuntu, cela se fait très simplement avec **Netplan**.

## Prérequis

- Un serveur Linux (Ubuntu 22.04 / 24.04) fonctionnant avec **Netplan**.
- Des privilèges d'administration (`sudo` ou `root`).
- Le nom de votre interface physique connectée au switch (ex: `eth0`, `enp3s0`).
- Un port de commutateur (switch) configuré en **Trunk** (laissant passer les VLANs souhaités).
- Les IDs de VLAN et les adresses IP prévues. Dans ce tutoriel, nous utiliserons :
    - **VLAN 10** (Management) : `10.0.10.5/24`
    - **VLAN 20** (Production) : `10.0.20.5/24`

## Procédure

### Étape 1 : Identifier l'interface réseau physique

Avant de configurer les VLANs, vous devez connaître le nom de l'interface qui reçoit le lien Trunk.

```bash
ip link show
```

!!! success "Résultat attendu"
    Vous devriez voir une interface active (avec l'état `UP`), par exemple `enp3s0`. C'est cette interface qui servira de base (interface "parente") pour nos VLANs.

### Étape 2 : Éditer la configuration Netplan

Les fichiers de configuration de Netplan se trouvent dans le répertoire `/etc/netplan/` et portent l'extension `.yaml`.

Ouvrez le fichier de configuration existant ou créez-en un nouveau (par exemple `50-cloud-init.yaml` ou `01-netcfg.yaml`) :

```bash
sudo nano /etc/netplan/01-netcfg.yaml
```

Voici comment structurer votre fichier YAML pour déclarer les deux VLANs sur l'interface `enp3s0` :

```yaml title="/etc/netplan/01-netcfg.yaml" linenums="1"
network:
  version: 2
  ethernets:
    enp3s0:
      # L'interface physique ne prend pas d'IP directement
      # s'il n'y a pas de VLAN natif (untagged) à exploiter.
      dhcp4: false
      dhcp6: false

  vlans:
    vlan10:
      id: 10
      link: enp3s0
      addresses:
        - 10.0.10.5/24
      # On peut définir une route par défaut sur un VLAN spécifique
      routes:
        - to: default
          via: 10.0.10.254
      nameservers:
        addresses:
          - 1.1.1.1
          - 8.8.8.8

    vlan20:
      id: 20
      link: enp3s0
      addresses:
        - 10.0.20.5/24
```

!!! warning "Attention à l'indentation"
    Le format YAML est extrêmement strict sur l'indentation. Utilisez des **espaces** (2 espaces par niveau), et jamais de tabulations.

### Étape 3 : Tester et appliquer la configuration

Netplan permet de tester la configuration avant de l'appliquer définitivement, ce qui évite de perdre la main sur le serveur en cas d'erreur de syntaxe ou de routage.

```bash
sudo netplan try
```

Si le test est concluant, validez en appuyant sur `Entrée`. Si la commande ne retourne pas d'erreur, mais que vous voulez appliquer directement (en connaissance de cause) :

```bash
sudo netplan apply
```

## Vérification

Une fois la configuration appliquée, vérifions que les interfaces virtuelles ont bien été créées et qu'elles possèdent les bonnes adresses IP.

```bash
ip -brief address show
```

!!! success "Résultat attendu"
    ```text
    lo               UNKNOWN        127.0.0.1/8 ::1/128 
    enp3s0           UP             
    vlan10@enp3s0    UP             10.0.10.5/24 fe80::...
    vlan20@enp3s0    UP             10.0.20.5/24 fe80::...
    ```
    On observe la création des interfaces `vlan10` et `vlan20` attachées à l'interface parente `@enp3s0`.

Vérifiez ensuite la connectivité vers les passerelles respectives des VLANs :

```bash
ping -c 3 10.0.10.254
ping -c 3 10.0.20.254
```

## Ressources

- [Documentation officielle Ubuntu sur Netplan](https://ubuntu.com/server/docs/network-configuration) — Le manuel officiel pour la configuration réseau sous Ubuntu.
- [Standard IEEE 802.1Q](https://fr.wikipedia.org/wiki/IEEE_802.1Q) — Pour approfondir la théorie sur le fonctionnement du protocole d'encapsulation des VLANs.
