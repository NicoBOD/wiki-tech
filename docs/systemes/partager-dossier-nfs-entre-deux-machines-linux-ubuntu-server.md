---
title: Partager un dossier entre deux machines Linux avec NFS sur Ubuntu Server
date: 2026-06-01
author: Nicolas BODAINE
tags:
  - linux
  - nfs
  - ubuntu
  - partage
  - fichiers
  - stockage
difficulty: débutant
os: Ubuntu Server 24.04 / Debian 13
status: publié
---

# Partager un dossier entre deux machines Linux avec NFS sur Ubuntu Server

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour mettre en place un **partage NFS** simple entre **deux machines Linux**. Nous allons préparer un serveur NFS, exporter un dossier de lab, monter ce dossier depuis une machine cliente, tester la lecture/écriture, puis rendre le montage persistant.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu Server 24.04 / Debian 13 |
| Dernière mise à jour | 2026-06-01 |

## Contexte

Dans un lab, un partage **NFS** (*Network File System*) est pratique pour :

- centraliser des fichiers sur une VM serveur ;
- déposer des scripts, sauvegardes ou documents de TP ;
- partager un même dossier entre plusieurs machines Linux ;
- comprendre la différence entre un **stockage local** et un **stockage monté par le réseau**.

Pour un premier exercice, NFS est intéressant car il permet de travailler plusieurs notions utiles :

- installation d'un service côté serveur ;
- configuration d'un partage via `/etc/exports` ;
- montage manuel puis persistant côté client ;
- vérification avec des commandes simples comme `exportfs`, `showmount` et `findmnt`.

Dans ce tutoriel, nous utilisons un scénario volontairement simple :

- une VM **serveur NFS** avec l'adresse `192.168.56.21` ;
- une VM **cliente** avec l'adresse `192.168.56.22` ;
- un dossier partagé : `/srv/nfs/partage-lab` ;
- un point de montage côté client : `/mnt/partage-lab`.

Adaptez ces valeurs à votre propre lab.

## Prérequis

- Deux machines Linux sur le même réseau de test
- Un accès `sudo` sur les deux machines
- Une connectivité IP fonctionnelle entre les deux machines
- Un utilisateur de lab cohérent sur les deux machines, par exemple `formation`

Vérifiez d'abord la connectivité et l'identité de l'utilisateur sur chaque machine :

### Côté serveur

```bash
hostname
ip -br addr
id
```

### Côté client

```bash
hostname
ip -br addr
id
ping -c 2 192.168.56.21
```

!!! note "À propos des droits sur NFS"
    NFS manipule surtout des **UID** et **GID** Linux.
    Pour un premier TP, le plus simple est d'utiliser un même utilisateur de lab sur les deux machines, souvent créé en premier lors de l'installation.
    Cela évite beaucoup de confusion sur les permissions.

## Procédure

### Étape 1 : installer le serveur NFS

Sur la machine serveur, installez le paquet serveur :

```bash
sudo apt update
sudo apt install -y nfs-kernel-server
```

Activez ensuite le service et vérifiez son état :

```bash
sudo systemctl enable --now nfs-kernel-server
sudo systemctl status nfs-kernel-server --no-pager
```

!!! success "Résultat attendu"
    Le service `nfs-kernel-server` doit être actif sans erreur bloquante.

### Étape 2 : créer le dossier qui sera partagé

Sur le serveur, créez un dossier dédié au TP :

```bash
sudo mkdir -p /srv/nfs/partage-lab
sudo chown "$USER":"$USER" /srv/nfs/partage-lab
sudo chmod 2775 /srv/nfs/partage-lab
```

Ajoutez un premier fichier de test :

```bash
printf 'Fichier créé sur le serveur NFS\n' | sudo tee /srv/nfs/partage-lab/serveur.txt > /dev/null
ls -ld /srv/nfs/partage-lab
ls -l /srv/nfs/partage-lab
```

Pourquoi `2775` ?

- `775` laisse le propriétaire et le groupe écrire dans le dossier ;
- le bit `2` active le **setgid** sur le dossier, ce qui aide à garder le même groupe sur les nouveaux fichiers créés dedans.

### Étape 3 : déclarer l'export NFS dans `/etc/exports`

Sur le serveur, ouvrez le fichier de configuration des exports :

```bash
sudo nano /etc/exports
```

Ajoutez la ligne suivante à la fin du fichier :

```exports
/srv/nfs/partage-lab 192.168.56.22(rw,sync,no_subtree_check)
```

Explication rapide :

- `/srv/nfs/partage-lab` : dossier exporté ;
- `192.168.56.22` : machine cliente autorisée ;
- `rw` : le client peut lire et écrire ;
- `sync` : le serveur écrit les données de façon synchrone ;
- `no_subtree_check` : évite des contrôles inutiles sur l'arborescence exportée.

!!! warning "N'utilisez pas `*` sans réfléchir"
    Dans un vrai environnement, évitez d'autoriser tout le réseau sans nécessité.
    Pour un TP propre, ciblez une IP précise ou un sous-réseau connu.

### Étape 4 : appliquer et vérifier la configuration du serveur

Rechargez la table des exports :

```bash
sudo exportfs -rav
```

Affichez ensuite les exports actifs :

```bash
sudo exportfs -v
```

Vous pouvez aussi contrôler localement le contenu exporté :

```bash
sudo showmount -e localhost
```

Exemple de résultat attendu :

```text
Export list for localhost:
/srv/nfs/partage-lab 192.168.56.22
```

!!! success "Résultat attendu"
    Le dossier `/srv/nfs/partage-lab` apparaît bien dans la liste des exports du serveur.

### Étape 5 : installer les outils NFS côté client

Sur la machine cliente, installez les outils nécessaires au montage NFS :

```bash
sudo apt update
sudo apt install -y nfs-common
```

Vérifiez que le client voit bien l'export du serveur :

```bash
showmount -e 192.168.56.21
```

Exemple de résultat attendu :

```text
Export list for 192.168.56.21:
/srv/nfs/partage-lab 192.168.56.22
```

Si rien n'apparaît, revérifiez :

- l'adresse IP du serveur ;
- la ligne dans `/etc/exports` ;
- la connectivité réseau ;
- l'application de la configuration avec `exportfs -rav`.

### Étape 6 : monter le partage manuellement sur le client

Créez le point de montage puis montez le partage :

```bash
sudo mkdir -p /mnt/partage-lab
sudo mount -t nfs 192.168.56.21:/srv/nfs/partage-lab /mnt/partage-lab
```

Vérifiez immédiatement le montage :

```bash
mount | grep partagelab || mount | grep partage-lab
findmnt /mnt/partage-lab
ls -l /mnt/partage-lab
```

Exemple de lecture possible avec `findmnt` :

```text
TARGET            SOURCE                                   FSTYPE OPTIONS
/mnt/partage-lab  192.168.56.21:/srv/nfs/partage-lab      nfs4   rw,relatime,...
```

!!! success "Résultat attendu"
    Le point de montage `/mnt/partage-lab` doit être de type `nfs` ou `nfs4`, et le fichier `serveur.txt` doit être visible depuis le client.

### Étape 7 : tester la lecture et l'écriture depuis le client

Depuis le client, créez un nouveau fichier dans le partage :

```bash
echo 'Fichier créé depuis le client NFS' > /mnt/partage-lab/client.txt
ls -l /mnt/partage-lab
cat /mnt/partage-lab/serveur.txt
cat /mnt/partage-lab/client.txt
```

Puis revenez sur le serveur pour vérifier que le fichier est bien visible :

```bash
ls -l /srv/nfs/partage-lab
cat /srv/nfs/partage-lab/client.txt
```

!!! note "Si l'écriture échoue"
    Le problème vient souvent des permissions Linux ou d'un décalage d'UID/GID entre les deux machines.
    Pour un premier lab, vérifiez avec `id` que l'utilisateur de travail a bien les mêmes identifiants sur le serveur et le client.

### Étape 8 : rendre le montage persistant avec `/etc/fstab`

Le montage manuel disparaît après un redémarrage.
Pour le remonter automatiquement, ajoutez une ligne dans `/etc/fstab` côté client.

Sauvegardez d'abord le fichier :

```bash
sudo cp /etc/fstab /etc/fstab.bak
```

Ouvrez ensuite `/etc/fstab` :

```bash
sudo nano /etc/fstab
```

Ajoutez cette ligne :

```fstab
192.168.56.21:/srv/nfs/partage-lab /mnt/partage-lab nfs defaults,_netdev 0 0
```

Explication rapide :

- premier champ : export NFS distant ;
- deuxième champ : point de montage local ;
- `nfs` : type de système de fichiers ;
- `defaults` : options standard ;
- `_netdev` : indique que le montage dépend du réseau.

### Étape 9 : valider l'entrée `/etc/fstab`

Avant de redémarrer, testez la configuration :

```bash
sudo umount /mnt/partage-lab
sudo mount -a
findmnt /mnt/partage-lab
ls -l /mnt/partage-lab
```

Si `mount -a` ne renvoie pas d'erreur et que le partage revient correctement, l'entrée est bonne.

## Vérification

Depuis le client, vous devez pouvoir confirmer les points suivants :

```bash
showmount -e 192.168.56.21
findmnt /mnt/partage-lab
touch /mnt/partage-lab/test-validation.txt
ls -l /mnt/partage-lab
```

!!! success "Résultat attendu"
    Le partage est visible, monté correctement, et la création d'un fichier de test fonctionne depuis la machine cliente.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `sudo apt install -y nfs-kernel-server` | Installer le serveur NFS |
| `sudo apt install -y nfs-common` | Installer les outils NFS côté client |
| `sudo exportfs -rav` | Recharger les exports NFS |
| `sudo exportfs -v` | Afficher les exports actifs et leurs options |
| `showmount -e 192.168.56.21` | Lister les exports proposés par le serveur |
| `sudo mount -t nfs serveur:/export /mnt/point` | Monter un partage NFS manuellement |
| `findmnt /mnt/partage-lab` | Vérifier le montage effectivement utilisé |
| `sudo mount -a` | Tester les montages déclarés dans `/etc/fstab` |

## Ressources

- [Ubuntu Server documentation — Install NFS](https://documentation.ubuntu.com/server/how-to/networking/install-nfs/) — Procédure officielle pour installer et configurer NFS sur Ubuntu
- [man7 — `exports(5)`](https://man7.org/linux/man-pages/man5/exports.5.html) — Référence sur le format et les options de `/etc/exports`
- [man7 — `mount.nfs(8)`](https://man7.org/linux/man-pages/man8/mount.nfs.8.html) — Référence sur le montage NFS côté client
- [man7 — `exportfs(8)`](https://man7.org/linux/man-pages/man8/exportfs.8.html) — Référence sur la publication et le rechargement des exports
