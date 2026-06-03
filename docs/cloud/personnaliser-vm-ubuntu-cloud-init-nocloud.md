---
title: Personnaliser une VM Ubuntu au premier démarrage avec cloud-init et NoCloud
date: 2026-06-03
author: Nicolas BODAINE
tags:
  - cloud-init
  - ubuntu
  - automatisation
  - deploiement
  - kvm
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Personnaliser une VM Ubuntu au premier démarrage avec cloud-init et NoCloud

!!! abstract "Résumé"
    Apprenez à utiliser `cloud-init` en environnement local ou hors-ligne (Proxmox, KVM, VMware) sans serveur de métadonnées cloud. Grâce à la méthode "NoCloud", vous pouvez injecter un nom d'hôte, des utilisateurs, des clés SSH et préinstaller des paquets dès le premier démarrage en attachant simplement une petite image ISO (le *seed*).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04, Debian |
| Dernière mise à jour | 2026-06-03 |

## Contexte

Lorsque vous déployez une machine virtuelle sur un cloud public (AWS, GCP, Azure), la plateforme injecte automatiquement vos clés SSH et la configuration réseau grâce à `cloud-init`. L'outil récupère ces données via un service de "metadata" accessible sur le réseau (généralement à l'adresse locale `169.254.169.254`).

En environnement de laboratoire (homelab, KVM local, VirtualBox), ce service réseau n'existe pas. Si vous utilisez les images prêtes à l'emploi d'Ubuntu (les "Cloud Images"), vous vous retrouvez bloqué au démarrage : impossible de vous connecter sans mot de passe défini.

La solution est la source de données **NoCloud** de `cloud-init`. Elle permet de fournir la configuration via un fichier ISO monté comme lecteur CD-ROM virtuel sur la VM. 

## Prérequis

- Un système Linux hôte pour préparer l'ISO (avec `cloud-image-utils` installé).
- Une image disque de type "Cloud" (ex: `ubuntu-24.04-server-cloudimg-amd64.img`).

## Procédure

### Étape 1 : Installer les outils nécessaires sur l'hôte

Pour créer facilement l'image ISO contenant nos fichiers de configuration, nous allons utiliser l'utilitaire `cloud-localds`.

```bash
sudo apt update
sudo apt install cloud-image-utils
```

### Étape 2 : Préparer le fichier `meta-data`

Le fichier `meta-data` contient les informations de base de l'instance, principalement son identifiant et son nom d'hôte.

Créez un fichier nommé `meta-data` (sans extension) :

```yaml title="meta-data"
instance-id: server-demo-01
local-hostname: webserver-demo
```

!!! tip "Pourquoi `instance-id` ?"
    `cloud-init` s'exécute entièrement au premier boot. Si, plus tard, vous modifiez le `user-data` et que vous voulez forcer `cloud-init` à se relancer au prochain démarrage, vous devrez changer la valeur de `instance-id`.

### Étape 3 : Préparer le fichier `user-data`

C'est ici que réside toute la puissance de `cloud-init`. Le fichier `user-data` utilise la syntaxe YAML pour définir les actions à effectuer (création d'utilisateurs, gestion de paquets, commandes diverses).

Créez un fichier nommé `user-data` :

```yaml title="user-data"
#cloud-config

# Configuration des utilisateurs
users:
  - name: adminuser
    groups: sudo
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... votre_cle_publique_ici

# Mise à jour de la liste des paquets au démarrage
package_update: true
# Installation automatique de certains paquets
packages:
  - htop
  - curl
  - git

# Commandes à exécuter à la toute fin du processus de boot
runcmd:
  - echo "VM déployée avec succès par cloud-init" > /etc/motd
```

!!! warning "L'en-tête est obligatoire"
    La toute première ligne de votre fichier `user-data` **doit** être `#cloud-config`. Sans cela, `cloud-init` ne saura pas comment interpréter le fichier.

### Étape 4 : Générer l'ISO (le "seed")

Une fois vos deux fichiers prêts dans le même répertoire, générez l'image ISO avec la commande `cloud-localds` :

```bash
cloud-localds seed.iso user-data meta-data
```

Cette commande va créer un fichier `seed.iso` contenant un système de fichiers `cidata` avec vos fichiers YAML à la racine.

### Étape 5 : Démarrer la VM

La dernière étape dépend de votre hyperviseur. Vous devez :
1. Attacher le disque dur principal (l'image Cloud Ubuntu).
2. Attacher le fichier `seed.iso` comme lecteur CD/DVD.

Si vous utilisez `qemu`/`kvm` en ligne de commande, cela ressemble à ceci :

```bash
qemu-system-x86_64 -m 2048 -enable-kvm \
  -drive file=ubuntu-24.04-server-cloudimg-amd64.img,format=qcow2 \
  -cdrom seed.iso
```

Au démarrage, `cloud-init` détectera le lecteur "cidata" (NoCloud), appliquera le nom d'hôte, créera l'utilisateur `adminuser`, ajoutera votre clé SSH, et installera les paquets demandés.

## Vérification

Une fois connecté à votre VM via SSH (`ssh adminuser@ip_de_la_vm`), vous pouvez vérifier que `cloud-init` a terminé son travail correctement.

Vérifier le statut global :
```bash
cloud-init status
```

!!! success "Résultat attendu"
    ```text
    status: done
    ```

Pour diagnostiquer d'éventuelles erreurs si un paquet ne s'est pas installé ou qu'une commande a échoué, consultez le fichier journal complet :
```bash
cat /var/log/cloud-init-output.log
```

## Ressources

- [Documentation officielle cloud-init : NoCloud Datasource](https://cloudinit.readthedocs.io/en/latest/reference/datasources/nocloud.html)
- [Documentation officielle cloud-init : Exemples user-data](https://cloudinit.readthedocs.io/en/latest/reference/examples.html)
