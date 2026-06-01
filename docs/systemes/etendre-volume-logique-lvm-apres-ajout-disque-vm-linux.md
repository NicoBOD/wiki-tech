---
title: "Étendre un volume logique LVM après ajout d’un disque sur une VM Linux"
date: 2026-06-01
author: Nicolas BODAINE
tags:
  - linux
  - lvm
  - stockage
  - disque
  - vm
  - ext4
  - xfs
difficulty: intermédiaire
os: Ubuntu 24.04 / Debian 13
status: publié
---

# Étendre un volume logique LVM après ajout d’un disque sur une VM Linux

!!! abstract "Résumé"
    Dans ce tutoriel, nous ajoutons un **nouveau disque** à une **VM Linux**, nous l’intégrons à **LVM**, puis nous agrandissons un **volume logique existant** et son **système de fichiers**. Le scénario est pensé pour un TP simple, concret et reproductible sur Ubuntu ou Debian.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 / Debian 13 |
| Dernière mise à jour | 2026-06-01 |

## Contexte

Dans un lab ou en production, il est fréquent de devoir agrandir un espace disque devenu trop petit :

- une partition de données arrive à saturation ;
- une application écrit plus de logs que prévu ;
- une VM reçoit un nouveau disque virtuel dans l’hyperviseur ;
- il faut augmenter la capacité sans recréer entièrement le serveur.

Quand Linux utilise **LVM** (*Logical Volume Manager*), l’opération est souvent plus souple qu’avec des partitions classiques.
On peut :

1. ajouter un nouveau disque ;
2. le déclarer comme **volume physique** LVM ;
3. l’ajouter au **groupe de volumes** existant ;
4. agrandir le **volume logique** visé ;
5. agrandir le **système de fichiers**.

Dans ce TP, nous allons suivre exactement cette chaîne.

## Prérequis

- Une VM Linux déjà installée avec **LVM**
- Un accès `sudo`
- Un **nouveau disque virtuel** ajouté depuis l’hyperviseur, par exemple **10 Go**
- Un volume logique existant à agrandir, par exemple un volume monté sur `/srv/donnees`
- Les outils `lvm2` installés
- Si le système de fichiers est en **XFS**, le paquet `xfsprogs`

Vérifiez les outils présents sur la machine :

```bash
lvs --version
vgs --version
pvs --version
```

Si nécessaire :

```bash
sudo apt update
sudo apt install -y lvm2
```

Si vous travaillez avec un système de fichiers XFS :

```bash
sudo apt install -y xfsprogs
```

!!! danger "Vérifiez toujours le bon disque"
    La commande `pvcreate` prépare un disque pour LVM. Si vous vous trompez de disque, vous pouvez détruire des données existantes. Avant chaque commande, relisez bien le nom du nouveau disque, par exemple `/dev/sdb`.

## Procédure

### Étape 1 : identifier l’existant avant modification

Commencez par afficher la situation actuelle côté disques, LVM et systèmes de fichiers :

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
sudo pvs
sudo vgs
sudo lvs -o lv_name,vg_name,lv_size,lv_path
df -hT
```

L’objectif est d’identifier :

- le **groupe de volumes** à étendre ;
- le **volume logique** à agrandir ;
- le **type de système de fichiers** (`ext4` ou `xfs`) ;
- le **point de montage** concerné.

Dans la suite, nous utiliserons cet exemple de lab :

```bash
NEW_DISK=/dev/sdb
VG_NAME=ubuntu-vg
LV_PATH=/dev/ubuntu-vg/data
MOUNT_POINT=/srv/donnees
```

Adaptez ces valeurs à votre machine.

!!! note "Exemple fréquent sur Ubuntu Server"
    Sur une installation Ubuntu avec LVM par défaut, le volume logique principal peut aussi être quelque chose comme `/dev/ubuntu-vg/ubuntu-lv`, monté sur `/`.
    La méthode reste la même, mais soyez encore plus vigilant si vous agrandissez le système principal.

### Étape 2 : vérifier que le nouveau disque est bien visible

Après avoir ajouté le disque dans l’hyperviseur, vérifiez qu’il apparaît dans le système invité :

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
```

Vous devez voir un disque supplémentaire, par exemple :

```text
sdb      10G disk
```

S’il n’apparaît pas immédiatement, forcez un rescannage SCSI puis recommencez :

```bash
for host in /sys/class/scsi_host/host*; do
  echo "- - -" | sudo tee "$host/scan"
done

lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
```

!!! success "Résultat attendu"
    Le nouveau disque est visible, sans système de fichiers ni point de montage, par exemple `/dev/sdb`.

### Étape 3 : préparer le nouveau disque comme volume physique LVM

Dans ce tutoriel, nous utilisons le **disque complet** directement dans LVM.
C’est la méthode la plus simple pour un TP débutant.

```bash
sudo pvcreate "$NEW_DISK"
sudo pvs
```

Exemple de résultat attendu :

```text
PV         VG        Fmt  Attr PSize   PFree
/dev/sda3  ubuntu-vg lvm2 a--  <39.00g    0
/dev/sdb             lvm2 ---  <10.00g <10.00g
```

!!! tip "Pourquoi ne pas créer de partition ici ?"
    C’est possible, mais pour un premier lab LVM ce n’est pas indispensable. Utiliser le disque entier évite d’ajouter une couche de complexité inutile.

### Étape 4 : ajouter le nouveau disque au groupe de volumes existant

Affichez d’abord les groupes de volumes :

```bash
sudo vgs
```

Ajoutez ensuite le nouveau disque au groupe existant :

```bash
sudo vgextend "$VG_NAME" "$NEW_DISK"
sudo vgs
```

Pour voir plus clairement l’espace libre disponible après l’extension :

```bash
sudo vgs -o vg_name,vg_size,vg_free
```

!!! success "Résultat attendu"
    Le groupe de volumes ciblé contient maintenant l’espace du nouveau disque, et la colonne `VFree` ou `vg_free` a augmenté.

### Étape 5 : confirmer le volume logique et le type de système de fichiers

Avant d’agrandir quoi que ce soit, vérifiez une dernière fois votre cible :

```bash
sudo lvs -o lv_name,vg_name,lv_size,lv_path
findmnt "$LV_PATH"
df -hT "$MOUNT_POINT"
```

Vous devez confirmer les éléments suivants :

- le bon **chemin du volume logique** ;
- le bon **point de montage** ;
- le bon **type de système de fichiers**.

C’est important car la commande de redimensionnement final n’est pas la même pour **ext4** et **xfs**.

### Étape 6 : agrandir le volume logique

Deux approches sont très courantes :

- ajouter une taille précise, par exemple `+5G` ;
- consommer tout l’espace libre du groupe de volumes.

#### Option A : ajouter une taille précise

```bash
sudo lvextend -L +5G "$LV_PATH"
```

#### Option B : utiliser tout l’espace libre du groupe de volumes

```bash
sudo lvextend -l +100%FREE "$LV_PATH"
```

Dans ce TP, nous retenons l’option **B**, simple et parlante pour un lab.

Vérifiez ensuite la nouvelle taille du volume logique :

```bash
sudo lvs -o lv_name,vg_name,lv_size,lv_path
```

!!! note "Pourquoi le système de fichiers n’a pas encore grandi ?"
    `lvextend` agrandit le **conteneur LVM**, mais pas automatiquement le système de fichiers qu’il contient. Il faut faire une deuxième étape.

### Étape 7 : agrandir le système de fichiers

Le choix dépend du système de fichiers utilisé.

#### Cas 1 : le volume est en `ext4`

```bash
sudo resize2fs "$LV_PATH"
```

#### Cas 2 : le volume est en `xfs`

Avec XFS, la commande s’exécute sur le **point de montage** :

```bash
sudo xfs_growfs "$MOUNT_POINT"
```

!!! warning "Erreur classique"
    N’utilisez pas `resize2fs` sur un volume XFS. Inversement, `xfs_growfs` ne fonctionne que sur un système de fichiers XFS déjà monté.

### Étape 8 : vérifier le résultat final

Contrôlez à nouveau l’état global :

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
sudo pvs
sudo vgs -o vg_name,vg_size,vg_free
sudo lvs -o lv_name,vg_name,lv_size,lv_path
df -hT "$MOUNT_POINT"
```

Exemple de logique attendue :

- le groupe de volumes a gagné de la capacité ;
- le volume logique est plus grand ;
- le système de fichiers monté sur le point choisi affiche plus d’espace disponible.

## Vérification

Vous pouvez faire une vérification simple avec cette mini-checklist :

- [x] Le nouveau disque apparaît dans `lsblk`
- [x] Le disque a été initialisé avec `pvcreate`
- [x] Le groupe de volumes a été étendu avec `vgextend`
- [x] Le volume logique a été agrandi avec `lvextend`
- [x] Le système de fichiers a été agrandi avec `resize2fs` ou `xfs_growfs`
- [x] `df -hT` montre bien la nouvelle taille

Commande de contrôle final :

```bash
sudo lvs -o lv_name,vg_name,lv_size,lv_path
df -hT "$MOUNT_POINT"
```

!!! success "Résultat attendu"
    La taille du volume logique et celle du système de fichiers sont cohérentes. Le point de montage dispose bien du nouvel espace.

## Aide-mémoire

| Commande | Rôle |
|----------|------|
| `lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT` | Voir les disques, partitions, types de FS et points de montage |
| `pvs` | Lister les volumes physiques LVM |
| `vgs` | Lister les groupes de volumes |
| `lvs` | Lister les volumes logiques |
| `pvcreate /dev/sdb` | Initialiser un disque pour LVM |
| `vgextend ubuntu-vg /dev/sdb` | Ajouter un disque à un groupe de volumes |
| `lvextend -l +100%FREE /dev/ubuntu-vg/data` | Donner tout l’espace libre au volume logique |
| `resize2fs /dev/ubuntu-vg/data` | Agrandir un système de fichiers ext4 |
| `xfs_growfs /srv/donnees` | Agrandir un système de fichiers XFS |

## Glossaire

`PV` (*Physical Volume*)
:   Disque ou partition préparé(e) pour être utilisé(e) par LVM.

`VG` (*Volume Group*)
:   Groupe logique qui agrège un ou plusieurs volumes physiques.

`LV` (*Logical Volume*)
:   Volume logique créé dans un groupe de volumes, sur lequel on place généralement un système de fichiers.

`ext4`
:   Système de fichiers très courant sous Linux, extensible avec `resize2fs`.

`XFS`
:   Système de fichiers souvent utilisé sur les serveurs, extensible avec `xfs_growfs`.

## Ressources

- [Documentation Red Hat Enterprise Linux — Configuring and managing logical volumes](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_logical_volumes/index) — Vue d’ensemble officielle sur LVM
- [man `pvcreate` (Ubuntu 24.04)](https://manpages.ubuntu.com/manpages/noble/en/man8/pvcreate.8.html) — Initialiser un volume physique LVM
- [man `vgextend` (Ubuntu 24.04)](https://manpages.ubuntu.com/manpages/noble/en/man8/vgextend.8.html) — Ajouter un volume physique à un groupe de volumes
- [man `lvextend` (Ubuntu 24.04)](https://manpages.ubuntu.com/manpages/noble/en/man8/lvextend.8.html) — Agrandir un volume logique
- [man `resize2fs` (Ubuntu 24.04)](https://manpages.ubuntu.com/manpages/noble/en/man8/resize2fs.8.html) — Agrandir un système de fichiers ext4
- [man `xfs_growfs` (Ubuntu 24.04)](https://manpages.ubuntu.com/manpages/noble/en/man8/xfs_growfs.8.html) — Agrandir un système de fichiers XFS
