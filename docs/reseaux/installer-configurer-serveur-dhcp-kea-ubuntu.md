---
title: Mettre en place un serveur DHCP local avec Kea sur Ubuntu
date: 2026-06-15
author: Nicolas BODAINE
tags:
  - dhcp
  - kea
  - reseaux
  - infrastructure
  - linux
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Mettre en place un serveur DHCP local avec Kea sur Ubuntu

!!! abstract "Résumé"
    Apprenez à installer et configurer **Kea**, le serveur DHCP moderne développé par l'ISC (Internet Systems Consortium), pour distribuer automatiquement des adresses IP, des passerelles et des serveurs DNS aux machines de votre réseau local sur Ubuntu.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 / 22.04 |
| Dernière mise à jour | 2026-06-15 |

## Contexte

Pendant longtemps, `isc-dhcp-server` a été le standard de l'industrie pour les serveurs DHCP sous Linux. Cependant, l'ISC a annoncé la fin de vie (*End of Life*) de ce vénérable logiciel. Son remplaçant officiel est **Kea**, un serveur DHCP de nouvelle génération, plus modulaire, plus performant et qui utilise une configuration au format JSON.

Dans ce tutoriel, nous allons configurer Kea pour distribuer des adresses IP sur un sous-réseau local (par exemple, `192.168.10.0/24`).

## Prérequis

- Un serveur Ubuntu (22.04 ou 24.04) avec une adresse IP **statique** (ex: `192.168.10.1`).
- Avoir les privilèges `sudo` ou `root` sur ce serveur.
- Au moins une machine cliente sur le même réseau pour tester l'attribution d'IP.

!!! warning "Attention aux conflits"
    Assurez-vous qu'il n'y a **pas d'autre serveur DHCP** actif sur ce réseau (comme une box internet ou un routeur) pour éviter les conflits d'adresses.

## Procédure

### Étape 1 : Installation de Kea

Sur Ubuntu, les paquets de Kea sont disponibles dans les dépôts officiels. Pour un serveur DHCP IPv4, nous n'avons besoin que du paquet principal.

```bash
sudo apt update
sudo apt install kea-dhcp4-server
```

Vous pouvez vérifier que le service est installé, mais il ne démarrera probablement pas correctement tant que la configuration n'est pas adaptée à votre interface.

### Étape 2 : Configuration du serveur DHCPv4

Le fichier de configuration principal pour le DHCP en IPv4 est `/etc/kea/kea-dhcp4.conf`. Il est au format JSON. Par défaut, il contient de très nombreux commentaires et exemples.

Nous allons sauvegarder l'original et créer un fichier de configuration épuré.

```bash
sudo mv /etc/kea/kea-dhcp4.conf /etc/kea/kea-dhcp4.conf.backup
sudo nano /etc/kea/kea-dhcp4.conf
```

Ajoutez la configuration suivante. Adaptez les adresses selon votre réseau (ici, on utilise le réseau `192.168.10.0/24`, l'interface `eth1`, et la passerelle `192.168.10.1`) :

```json title="/etc/kea/kea-dhcp4.conf"
{
  "Dhcp4": {
    "interfaces-config": {
      "interfaces": [ "eth1" ],
      "dhcp-socket-type": "raw"
    },
    
    "lease-database": {
      "type": "memfile",
      "lfc-interval": 3600
    },

    "valid-lifetime": 4000,
    "renew-timer": 1000,
    "rebind-timer": 2000,

    "subnet4": [
      {
        "id": 1,
        "subnet": "192.168.10.0/24",
        "pools": [
          {
            "pool": "192.168.10.100 - 192.168.10.200"
          }
        ],
        "option-data": [
          {
            "name": "routers",
            "data": "192.168.10.1"
          },
          {
            "name": "domain-name-servers",
            "data": "1.1.1.1, 8.8.8.8"
          }
        ]
      }
    ]
  }
}
```

!!! note "Explications de la configuration"
    - **`interfaces`** : L'interface réseau sur laquelle Kea va écouter (ex: `eth1`, `ens33`). Modifiez selon le nom de votre interface (visible avec la commande `ip a`).
    - **`lease-database`** : Kea stocke les baux (leases) dans un fichier en mémoire par défaut, ce qui est très performant.
    - **`valid-lifetime`** : La durée de validité du bail DHCP en secondes.
    - **`subnet4`** : La déclaration de votre sous-réseau. Le `pool` définit la plage d'IP distribuables (ici de `.100` à `.200`).
    - **`option-data`** : Les options distribuées aux clients, comme la passerelle par défaut (`routers`) et les serveurs DNS (`domain-name-servers`).

### Étape 3 : Validation et redémarrage du service

Kea propose une commande pour vérifier que votre syntaxe JSON est valide avant de relancer le service. C'est essentiel pour éviter les erreurs de frappe (comme une virgule manquante) !

```bash
sudo kea-dhcp4 -t /etc/kea/kea-dhcp4.conf
```

Si aucune erreur n'est signalée, vous pouvez redémarrer le service et vérifier son statut :

```bash
sudo systemctl restart kea-dhcp4-server
sudo systemctl status kea-dhcp4-server
```

!!! success "Statut attendu"
    Vous devriez voir `Active: active (running)` en vert, confirmant que le serveur écoute les requêtes.

### Étape 4 : Définir une IP fixe (réservation)

Pour assigner toujours la même adresse IP à une machine spécifique (par exemple une imprimante, un NAS ou un hyperviseur), on utilise son adresse MAC.

Ajoutez un bloc `reservations` dans votre définition de sous-réseau :

```json hl_lines="17-23"
    "subnet4": [
      {
        "id": 1,
        "subnet": "192.168.10.0/24",
        "pools": [
          {
            "pool": "192.168.10.100 - 192.168.10.200"
          }
        ],
        "option-data": [
          {
            "name": "routers",
            "data": "192.168.10.1"
          }
        ],
        "reservations": [
          {
            "hw-address": "00:11:22:33:44:55",
            "ip-address": "192.168.10.50",
            "hostname": "imprimante-reseau"
          }
        ]
      }
    ]
```

N'oubliez pas de redémarrer le service après modification :
```bash
sudo systemctl restart kea-dhcp4-server
```

## Vérification

Sur une machine cliente connectée au même réseau, renouvelez votre bail DHCP.

=== "Linux"

    ```bash
    sudo dhclient -r
    sudo dhclient -v
    ```

=== "Windows"

    ```powershell
    ipconfig /release
    ipconfig /renew
    ```

Pour voir les baux actuellement attribués par Kea, consultez le fichier d'état local :

```bash
cat /var/lib/kea/kea-leases4.csv
```

## Ressources

- [Documentation officielle Kea DHCP](https://kea.readthedocs.io/) — Le guide de référence complet par l'ISC.
- [Dépôt GitHub du projet Kea](https://github.com/isc-projects/kea) — Pour suivre le développement et les sources.
