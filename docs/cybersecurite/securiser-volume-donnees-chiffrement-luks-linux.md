---
title: Sécuriser un volume de données avec le chiffrement LUKS sous Linux
date: 2026-06-15
author: Nicolas BODAINE
tags:
  - linux
  - securite
  - luks
  - chiffrement
  - cryptsetup
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Sécuriser un volume de données avec le chiffrement LUKS sous Linux

!!! abstract "Résumé"
    Le chiffrement des données au repos est une bonne pratique essentielle pour protéger des informations sensibles. LUKS (Linux Unified Key Setup) est le standard de chiffrement de disques et partitions sous Linux. Ce tutoriel montre comment initialiser, ouvrir, formater et monter un volume chiffré.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 (valable pour la majorité des distributions Linux) |
| Dernière mise à jour | 2026-06-15 |

## Contexte

La perte ou le vol d'un support de stockage (disque dur, clé USB, ordinateur portable) peut compromettre l'intégralité des données qui s'y trouvent. LUKS permet de chiffrer l'intégralité d'un périphérique bloc au niveau du noyau Linux (grâce à *dm-crypt*). Sans la clé de déchiffrement, les données restent totalement illisibles.

Dans ce laboratoire, nous allons chiffrer un volume (qui peut être une partition comme `/dev/sdb1` ou un disque entier), puis le formater et l'utiliser comme un espace de stockage classique.

!!! warning "Attention aux données"
    Le processus d'initialisation de LUKS détruit toutes les données précédemment présentes sur la partition ciblée. **Assurez-vous de manipuler le bon disque !**

## Prérequis

- Un accès `root` ou via `sudo`
- Le paquet `cryptsetup` installé (`sudo apt install cryptsetup` sous Debian/Ubuntu)
- Une partition ou un disque disponible et **vide de données importantes** (dans notre exemple : `/dev/sdb1`)

## Procédure

### Étape 1 : Initialiser le volume LUKS

L'initialisation prépare la partition en écrivant l'en-tête LUKS et en définissant la première phrase de passe (passphrase).

```bash
sudo cryptsetup luksFormat /dev/sdb1
```

Il vous sera demandé de taper `YES` (en majuscules) pour confirmer l'écrasement des données, puis de saisir une phrase de passe solide (deux fois).

### Étape 2 : Ouvrir (déverrouiller) le volume chiffré

Une fois initialisé, le volume doit être déverrouillé et mappé virtuellement pour pouvoir être utilisé.

```bash
sudo cryptsetup open /dev/sdb1 volume_secret
```

Le système vous demandera la phrase de passe définie à l'étape précédente. Si elle est correcte, un périphérique déchiffré virtuel apparaîtra sous `/dev/mapper/volume_secret`.

### Étape 3 : Créer un système de fichiers (formater)

Maintenant que le volume est ouvert en clair au niveau logique, nous pouvons le formater, par exemple en `ext4`.

```bash
sudo mkfs.ext4 /dev/mapper/volume_secret
```

### Étape 4 : Monter le volume et l'utiliser

Créez un point de montage et montez le volume logique.

```bash
sudo mkdir -p /mnt/donnees_securisees
sudo mount /dev/mapper/volume_secret /mnt/donnees_securisees
```

Vous pouvez maintenant écrire des fichiers dans `/mnt/donnees_securisees`. Ils seront chiffrés à la volée sur le disque dur physique (`/dev/sdb1`).

### Étape 5 : Démonter et verrouiller (fermer) le volume

Pour sécuriser à nouveau les données (par exemple avant de débrancher un disque dur externe ou d'éteindre la machine), il faut démonter le volume et refermer le conteneur LUKS.

```bash
sudo umount /mnt/donnees_securisees
sudo cryptsetup close volume_secret
```

Le périphérique virtuel `/dev/mapper/volume_secret` disparaît. Les données sur `/dev/sdb1` sont inaccessibles sans refaire l'étape d'ouverture avec la phrase de passe.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `cryptsetup luksFormat /dev/sdX` | Formater la partition au format LUKS (DÉTRUIT LES DONNÉES) |
| `cryptsetup open /dev/sdX nom` | Ouvrir le volume chiffré dans `/dev/mapper/nom` |
| `cryptsetup close nom` | Verrouiller le volume chiffré |
| `cryptsetup luksAddKey /dev/sdX` | Ajouter une phrase de passe supplémentaire au volume |
| `cryptsetup luksDump /dev/sdX` | Afficher les informations de l'en-tête LUKS (clés, algorithmes) |

## Vérification

Pour vérifier qu'un périphérique bloc est bien au format LUKS (même lorsqu'il est fermé) :

```bash
sudo cryptsetup isLuks /dev/sdb1 && echo "C'est un volume LUKS" || echo "Ce n'est pas un volume LUKS"
```

Pour visualiser l'état d'un volume ouvert :

```bash
sudo cryptsetup status volume_secret
```

!!! success "Résultat attendu"
    La commande de statut doit afficher des informations comme `type: LUKS2`, l'algorithme de chiffrement (ex: `aes-xts-plain64`), et le statut (actif).

## Ressources

- [Documentation Ubuntu sur le chiffrement](https://help.ubuntu.com/community/EncryptedFilesystems)
- [Manuel utilisateur de cryptsetup](https://gitlab.com/cryptsetup/cryptsetup/-/wikis/home)
- [Recommandations ANSSI sur la cryptographie](https://www.ssi.gouv.fr/entreprise/reglementation/confiance-numerique/le-chiffrement/)