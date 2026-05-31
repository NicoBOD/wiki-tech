---
title: "Sauvegarder et restaurer un dossier avec `rsync` sur Linux en local ou via SSH"
date: 2026-05-31
author: Nicolas BODAINE
tags:
  - linux
  - rsync
  - sauvegarde
  - restauration
  - ssh
  - fichiers
difficulty: débutant
os: Ubuntu 24.04 / Debian 13
status: publié
---

# Sauvegarder et restaurer un dossier avec `rsync` sur Linux en local ou via SSH

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour apprendre à utiliser **`rsync`** dans un petit lab Linux. Nous allons créer un dossier source, faire une première sauvegarde locale, rejouer une synchronisation incrémentale, restaurer les fichiers dans un autre emplacement, puis envoyer la même sauvegarde vers une autre machine en **SSH**.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu 24.04 / Debian 13 |
| Dernière mise à jour | 2026-05-31 |

## Contexte

`rsync` est un outil très utilisé pour :

- copier un dossier vers un autre emplacement ;
- faire une sauvegarde simple sur le même poste ;
- envoyer des fichiers vers une autre machine en SSH ;
- rejouer ensuite la synchronisation sans tout recopier inutilement ;
- restaurer rapidement des données depuis une copie saine.

Pour un débutant, c'est un excellent outil de TP car il permet de travailler plusieurs notions en même temps :

- arborescence de fichiers ;
- permissions Linux ;
- chemins absolus et relatifs ;
- tests sans risque avec `--dry-run` ;
- synchronisation distante avec SSH.

Dans ce tutoriel, nous utilisons un scénario volontairement simple et reproductible dans une VM ou sur deux machines de lab.

## Prérequis

- Une machine Linux de test
- `rsync` installé
- `openssh-client` installé si vous voulez faire la partie via SSH
- Une deuxième machine Linux joignable en SSH pour la partie distante, par exemple `192.168.56.30`
- Un compte utilisateur valide sur la machine distante, par exemple `formation`

Vérifiez d'abord que les outils sont disponibles :

```bash
rsync --version
ssh -V
```

Si `rsync` n'est pas encore installé :

```bash
sudo apt update
sudo apt install -y rsync openssh-client
```

!!! note "Aucun agent à installer côté distant"
    Pour la synchronisation via SSH, `rsync` s'appuie simplement sur la connexion SSH. Il n'y a pas de service spécial à déployer pour ce TP.

## Procédure

### Étape 1 : préparer un petit lab de fichiers

Créez un dossier de travail dédié au TP :

```bash
mkdir -p ~/lab-rsync/source/docs
mkdir -p ~/lab-rsync/destination-local
mkdir -p ~/lab-rsync/restore
```

Ajoutez quelques fichiers de test :

```bash
printf 'Bonjour depuis le lab rsync\n' > ~/lab-rsync/source/readme.txt
printf 'Version 1\n' > ~/lab-rsync/source/docs/inventaire.txt
printf '192.168.56.21 srv-lab-01\n192.168.56.22 srv-lab-02\n' > ~/lab-rsync/source/docs/hotes.txt
```

Affichez ensuite le contenu du dossier source :

```bash
find ~/lab-rsync/source -maxdepth 2 -type f | sort
```

Exemple de résultat attendu :

```text
/home/formation/lab-rsync/source/docs/hotes.txt
/home/formation/lab-rsync/source/docs/inventaire.txt
/home/formation/lab-rsync/source/readme.txt
```

!!! success "Résultat attendu"
    Le dossier `source` contient déjà quelques fichiers qui serviront de base à la sauvegarde et à la restauration.

### Étape 2 : comprendre le rôle du slash final

Avec `rsync`, le **slash final** à la fin du dossier source change le résultat.

#### Cas 1 : avec slash final

```bash
rsync -av ~/lab-rsync/source/ ~/lab-rsync/destination-local/
```

Ici, `rsync` copie **le contenu** de `source` dans `destination-local`.

#### Cas 2 : sans slash final

```bash
rsync -av ~/lab-rsync/source ~/lab-rsync/destination-local/
```

Ici, `rsync` copie **le dossier `source` lui-même** dans `destination-local`.

!!! warning "Point très important"
    Dans les sauvegardes, une grande partie des erreurs vient d'un mauvais chemin source. Avant de lancer une vraie synchronisation, prenez toujours 10 secondes pour relire la commande et vérifier la présence ou non du slash final.

Pour la suite du TP, nous allons utiliser ce modèle :

```bash
~/lab-rsync/source/
```

Cela signifie que nous voulons copier le **contenu** du dossier source.

### Étape 3 : tester la sauvegarde locale avec `--dry-run`

Avant de copier réellement les fichiers, faites une simulation :

```bash
rsync -av --dry-run ~/lab-rsync/source/ ~/lab-rsync/destination-local/
```

### Que signifient ces options ?

- `-a` : mode archive, utile pour conserver la structure, les dates et les permissions ;
- `-v` : mode verbeux, pour voir ce qui se passe ;
- `--dry-run` : simulation, rien n'est vraiment copié.

Exemple de sortie possible :

```text
sending incremental file list
./
readme.txt
docs/
docs/hotes.txt
docs/inventaire.txt

sent ...
received ...
```

!!! success "Résultat attendu"
    Vous devez voir la liste des fichiers qui seraient copiés, sans erreur et sans copie réelle.

### Étape 4 : lancer la première sauvegarde locale

Quand la simulation vous semble correcte, relancez la commande sans `--dry-run` :

```bash
rsync -av ~/lab-rsync/source/ ~/lab-rsync/destination-local/
```

Vérifiez ensuite le contenu de la destination :

```bash
find ~/lab-rsync/destination-local -maxdepth 2 -type f | sort
```

Vous pouvez aussi comparer les deux arborescences :

```bash
diff -r ~/lab-rsync/source ~/lab-rsync/destination-local && echo "copies identiques"
```

!!! success "Résultat attendu"
    La destination locale contient les mêmes fichiers que la source.

### Étape 5 : rejouer une synchronisation incrémentale

L'intérêt de `rsync` apparaît vraiment quand la source change.

Modifiez un fichier existant et ajoutez-en un nouveau :

```bash
printf 'Version 2\n' >> ~/lab-rsync/source/docs/inventaire.txt
printf 'Compte-rendu du TP\n' > ~/lab-rsync/source/docs/compte-rendu.txt
```

Relancez une simulation :

```bash
rsync -av --dry-run ~/lab-rsync/source/ ~/lab-rsync/destination-local/
```

Puis appliquez les changements :

```bash
rsync -av ~/lab-rsync/source/ ~/lab-rsync/destination-local/
```

!!! note "Pourquoi on parle de synchronisation incrémentale ?"
    `rsync` ne recopie pas inutilement tous les fichiers à chaque passage. Il détecte ce qui a changé et ne traite que les différences utiles.

### Étape 6 : restaurer les données dans un autre dossier

Dans un vrai contexte, la restauration consiste souvent à recopier une sauvegarde vers un nouvel emplacement.

Copiez ici le contenu sauvegardé vers un dossier `restore` :

```bash
rsync -av ~/lab-rsync/destination-local/ ~/lab-rsync/restore/
```

Vérifiez le résultat :

```bash
find ~/lab-rsync/restore -maxdepth 2 -type f | sort
diff -r ~/lab-rsync/destination-local ~/lab-rsync/restore && echo "restauration correcte"
```

!!! success "Résultat attendu"
    Le dossier `restore` doit contenir les mêmes fichiers que la sauvegarde locale.

### Étape 7 : préparer la sauvegarde vers une machine distante en SSH

Pour la partie distante, remplacez les valeurs ci-dessous par votre contexte de lab :

```bash
REMOTE_USER=formation
REMOTE_HOST=192.168.56.30
```

Testez d'abord l'accès SSH :

```bash
ssh ${REMOTE_USER}@${REMOTE_HOST} "hostname"
```

Si la connexion fonctionne, créez un dossier cible sur la machine distante :

```bash
ssh ${REMOTE_USER}@${REMOTE_HOST} 'mkdir -p ~/backup-rsync/source'
```

!!! tip "Premier test conseillé"
    Faites toujours une connexion SSH manuelle avant votre premier `rsync` distant. Cela permet de valider le réseau, l'utilisateur, la clé éventuelle et l'empreinte SSH.

### Étape 8 : simuler puis exécuter la sauvegarde via SSH

Commencez par une simulation :

```bash
rsync -av --dry-run -e ssh ~/lab-rsync/source/ ${REMOTE_USER}@${REMOTE_HOST}:~/backup-rsync/source/
```

Puis lancez la vraie synchronisation :

```bash
rsync -av -e ssh ~/lab-rsync/source/ ${REMOTE_USER}@${REMOTE_HOST}:~/backup-rsync/source/
```

Vérifiez ensuite la présence des fichiers sur la machine distante :

```bash
ssh ${REMOTE_USER}@${REMOTE_HOST} 'find ~/backup-rsync/source -maxdepth 2 -type f | sort'
```

!!! success "Résultat attendu"
    Les fichiers du dossier `source` doivent être visibles sur la machine distante dans `~/backup-rsync/source`.

### Étape 9 : comprendre et tester `--delete` sans risque

L'option `--delete` sert à supprimer dans la destination ce qui n'existe plus dans la source.

C'est très utile pour garder une copie fidèle, mais c'est aussi **l'option la plus risquée** si vous vous trompez de chemin.

Créez un mini labo séparé pour la tester sans danger :

```bash
mkdir -p ~/lab-rsync/delete-demo/source
mkdir -p ~/lab-rsync/delete-demo/destination
printf 'fichier utile\n' > ~/lab-rsync/delete-demo/source/fichier-a.txt
printf 'ancien fichier\n' > ~/lab-rsync/delete-demo/destination/obsolete.txt
```

Simulez d'abord la commande :

```bash
rsync -av --dry-run --delete ~/lab-rsync/delete-demo/source/ ~/lab-rsync/delete-demo/destination/
```

Si la sortie est cohérente, appliquez-la :

```bash
rsync -av --delete ~/lab-rsync/delete-demo/source/ ~/lab-rsync/delete-demo/destination/
```

Vérifiez le contenu final :

```bash
find ~/lab-rsync/delete-demo/destination -maxdepth 2 -type f | sort
```

!!! warning "À retenir"
    N'utilisez jamais `--delete` sur un chemin de production sans test préalable avec `--dry-run`. Une erreur de chemin peut supprimer beaucoup plus que prévu.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `rsync -av source/ destination/` | Synchroniser le contenu d'un dossier en local |
| `rsync -av --dry-run source/ destination/` | Simuler une synchronisation sans rien copier |
| `rsync -av -e ssh source/ user@host:destination/` | Synchroniser vers une machine distante via SSH |
| `rsync -av --delete source/ destination/` | Aligner la destination avec la source en supprimant les fichiers absents de la source |
| `diff -r dossier1 dossier2` | Comparer deux arborescences |
| `find dossier -type f | sort` | Lister les fichiers d'un dossier pour vérifier rapidement le résultat |

## Vérification

À la fin du TP, vous devez pouvoir valider les points suivants :

- [x] le dossier `destination-local` contient les mêmes fichiers que `source` ;
- [x] une deuxième synchronisation ne recopie que les changements utiles ;
- [x] le dossier `restore` contient une copie exploitable de la sauvegarde ;
- [x] la synchronisation distante via SSH fonctionne ;
- [x] vous savez quand utiliser `--dry-run` et pourquoi `--delete` demande de la prudence.

Commandes de contrôle utiles :

```bash
diff -r ~/lab-rsync/source ~/lab-rsync/destination-local && echo "sauvegarde locale OK"
diff -r ~/lab-rsync/destination-local ~/lab-rsync/restore && echo "restauration OK"
ssh ${REMOTE_USER}@${REMOTE_HOST} 'find ~/backup-rsync/source -maxdepth 2 -type f | sort'
```

!!! success "Résultat attendu"
    Vous avez une méthode simple, reproductible et vérifiable pour sauvegarder et restaurer un dossier avec `rsync`, aussi bien en local qu'à travers SSH.

## Glossaire

`rsync`
:   Outil de synchronisation de fichiers et de dossiers, utilisable en local ou via le réseau.

`--dry-run`
:   Mode simulation qui montre ce que la commande ferait sans appliquer les changements.

`SSH`
:   Protocole permettant de se connecter de façon sécurisée à une autre machine.

`Synchronisation incrémentale`
:   Méthode qui ne traite que les différences utiles entre la source et la destination.

## Ressources

- [rsync — documentation officielle / manpage](https://download.samba.org/pub/rsync/rsync.1) — Référence officielle de l'outil et de ses options
- [Debian Manpages — `rsync(1)`](https://manpages.debian.org/bookworm/rsync/rsync.1.en.html) — Version HTML pratique de la manpage `rsync`
- [Debian Manpages — `ssh(1)`](https://manpages.debian.org/bookworm/openssh-client/ssh.1.en.html) — Référence pour l'utilisation de SSH côté client
- [OpenSSH Manual Pages](https://www.openssh.com/manual.html) — Documentation officielle OpenSSH
