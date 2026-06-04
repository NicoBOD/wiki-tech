---
title: Partager un dossier sur le réseau local avec Samba sur Ubuntu Server
date: 2026-06-04
author: Nicolas BODAINE
tags:
  - samba
  - partage
  - reseau
  - windows
  - linux
difficulty: débutant
os: Ubuntu 24.04
status: publié
---

# Partager un dossier sur le réseau local avec Samba sur Ubuntu Server

!!! abstract "Résumé"
    Apprenez à installer et configurer un serveur Samba sur Ubuntu Server pour partager des dossiers sur votre réseau local. Ce tutoriel montre comment créer un partage public accessible à tous, ainsi qu'un partage privé protégé par mot de passe (accessible depuis Windows, macOS ou un autre poste Linux).

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 |
| Dernière mise à jour | 2026-06-04 |

## Contexte

Dans un environnement hétérogène (où se côtoient des machines Windows, Linux et macOS), **Samba** (l'implémentation libre du protocole SMB/CIFS) est la solution standard pour le partage de fichiers. Contrairement à NFS, qui est idéal entre machines Linux, Samba est nativement compris par Windows, ce qui en fait l'outil parfait pour créer un NAS domestique ou un serveur de fichiers d'entreprise.

Ce tutoriel couvre deux cas d'usage :

1. Un dossier partagé en accès libre (lecture/écriture pour tous sans mot de passe).
2. Un dossier partagé sécurisé, nécessitant un utilisateur et un mot de passe.

## Prérequis

- Une machine Ubuntu Server à jour et connectée au réseau local.
- Une adresse IP statique configurée sur le serveur (voir [Configurer une adresse IP statique avec Netplan](../reseaux/configurer-ip-statique-netplan-ubuntu-server.md)).
- Les droits administrateur (`sudo`).

## Procédure

### Étape 1 : Installation de Samba

Mettez à jour vos dépôts et installez le paquet `samba` :

```bash
sudo apt update
sudo apt install samba -y
```

Vérifiez que le service est actif :

```bash
sudo systemctl status smbd
```

### Étape 2 : Préparation des dossiers à partager

Nous allons créer deux dossiers distincts dans `/srv/samba` : un pour le partage public et un pour le partage privé.

```bash
# Créer l'arborescence
sudo mkdir -p /srv/samba/public
sudo mkdir -p /srv/samba/prive

# Le dossier public doit être accessible et modifiable par tous
sudo chmod 777 /srv/samba/public

# Le dossier privé appartiendra à un groupe spécifique (nous le créerons après)
```

### Étape 3 : Création d'un utilisateur Samba (pour le partage privé)

Samba utilise sa propre base de données de mots de passe, indépendante de celle des sessions Linux. Cependant, l'utilisateur Samba doit exister en tant qu'utilisateur système.

Créons un utilisateur système sans droit de connexion locale (`-M -s /usr/sbin/nologin`) appelé `smbuser` :

```bash
sudo useradd -M -s /usr/sbin/nologin smbuser
```

Ajoutez maintenant cet utilisateur à la base de données Samba (il vous sera demandé de définir un mot de passe) :

```bash
sudo smbpasswd -a smbuser
```

Attribuons la propriété du dossier privé à cet utilisateur :

```bash
sudo chown -R smbuser:smbuser /srv/samba/prive
sudo chmod 700 /srv/samba/prive
```

### Étape 4 : Configuration de `smb.conf`

Le fichier de configuration principal est `/etc/samba/smb.conf`. Il est recommandé de faire une sauvegarde de l'original avant de le modifier :

```bash
sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.backup
```

Éditez le fichier pour y ajouter vos partages à la fin du fichier :

```bash
sudo nano /etc/samba/smb.conf
```

Ajoutez-y ceci :

```ini title="/etc/samba/smb.conf"
# [Partage_Public] correspond au nom tel qu'il apparaîtra sur le réseau
[Partage_Public]
    path = /srv/samba/public
    browseable = yes
    read only = no
    guest ok = yes
    force create mode = 0666
    force directory mode = 0777

[Partage_Prive]
    path = /srv/samba/prive
    browseable = yes
    read only = no
    guest ok = no
    valid users = smbuser
    force create mode = 0660
    force directory mode = 0770
```

### Étape 5 : Redémarrage et prise en compte

Testez votre configuration pour détecter les éventuelles erreurs de syntaxe :

```bash
testparm
```

Si le résultat n'affiche pas d'erreur (`Loaded services file OK.`), redémarrez les services Samba :

```bash
sudo systemctl restart smbd nmbd
```

!!! tip "Autoriser Samba dans le pare-feu"
    Si vous utilisez UFW, n'oubliez pas d'autoriser le trafic Samba :
    ```bash
    sudo ufw allow samba
    ```

## Vérification

Pour vérifier que le partage fonctionne, rendez-vous sur une autre machine du réseau (par exemple votre poste de travail Windows).

=== "Depuis Windows"

    1. Ouvrez l'Explorateur de fichiers.
    2. Dans la barre d'adresse, tapez `\\IP_DE_VOTRE_SERVEUR` (ex: `\\192.168.1.50`).
    3. Vous devriez voir `Partage_Public` et `Partage_Prive`.
    4. En double-cliquant sur `Partage_Prive`, Windows vous demandera des identifiants : utilisez `smbuser` et le mot de passe défini lors de l'exécution de `smbpasswd`.

=== "Depuis Linux (en ligne de commande)"

    Installez le client Samba (`smbclient`) sur la machine cliente et testez l'accès :
    ```bash
    # Lister les partages (laissez le mot de passe vide pour le compte "guest")
    smbclient -L //IP_DE_VOTRE_SERVEUR -U guest

    # Se connecter au partage privé
    smbclient //IP_DE_VOTRE_SERVEUR/Partage_Prive -U smbuser
    ```

## Ressources

- [Documentation officielle d'Ubuntu - Samba File Server](https://ubuntu.com/server/docs/samba-file-server)