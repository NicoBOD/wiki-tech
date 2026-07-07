---
title: Créer et gérer un fichier d'échange (Swap) sous Linux
date: 2026-06-30
author: Nicolas BODAINE
tags:
  - swap
  - memoire
  - systeme
  - performances
difficulty: intermédiaire
os: Ubuntu 24.04 | Debian 12
status: publié
---

# Créer et gérer un fichier d'échange (Swap) sous Linux

!!! abstract "Résumé"
    Lorsque la mémoire vive (RAM) d'un serveur vient à saturer, Linux utilise l'espace d'échange (Swap) pour stocker temporairement les données inactives. Ce tutoriel explique comment créer, activer et optimiser un fichier de Swap sur un serveur ne disposant pas de partition dédiée.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu 24.04 / Debian 12 |
| Dernière mise à jour | 2026-06-30 |

## Contexte

Sur de nombreux serveurs Cloud (VPS), le système est livré sans partition de Swap pour économiser de l'espace disque. Cependant, si vos applications (bases de données, serveurs web) consomment toute la RAM disponible, le système invoquera le processus `OOM Killer` (Out Of Memory) pour tuer de manière brutale certains processus et libérer de la mémoire. 

La création d'un fichier de Swap permet d'éviter ces arrêts inopinés en offrant un "filet de sécurité" de mémoire virtuelle sur le disque dur.

## Prérequis

- Un accès `root` ou via `sudo` à votre machine Linux.
- Suffisamment d'espace disque disponible (vérifiable avec la commande `df -h`).

## Procédure

### Étape 1 : Vérifier l'état actuel du Swap

Avant de commencer, vérifions si le système possède déjà un espace de Swap actif.

```bash
sudo swapon --show
```
Si la commande ne retourne rien, cela signifie qu'aucun Swap n'est configuré. Vous pouvez également confirmer avec `free -h` :

```bash
free -h
```
!!! info "Sortie attendue"
    La ligne `Swap:` devrait afficher `0B` en total.

### Étape 2 : Créer le fichier de Swap

Nous allons créer un fichier de 2 Go nommé `/swapfile`. Il est recommandé d'utiliser `fallocate` car cette commande alloue l'espace instantanément.

```bash
sudo fallocate -l 2G /swapfile
```

!!! tip "Alternative si fallocate échoue"
    Sur certains systèmes de fichiers (comme ZFS), `fallocate` peut ne pas fonctionner. Dans ce cas, utilisez la commande `dd` :
    ```bash
    sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
    ```

### Étape 3 : Sécuriser et formater le fichier

Le fichier de Swap ne doit être lisible que par l'utilisateur `root` pour des raisons de sécurité, car il peut contenir des informations sensibles (mots de passe en clair, clés de session).

Ajustez les permissions :
```bash
sudo chmod 600 /swapfile
```

Ensuite, indiquez au système d'initialiser ce fichier comme un espace d'échange :
```bash
sudo mkswap /swapfile
```

### Étape 4 : Activer le Swap

Maintenant que le fichier est prêt, activons-le :

```bash
sudo swapon /swapfile
```

Vérifiez que le Swap est bien actif :
```bash
sudo swapon --show
```
!!! success "Résultat attendu"
    ```text
    NAME      TYPE  SIZE USED PRIO
    /swapfile file    2G   0B   -2
    ```

### Étape 5 : Rendre le Swap permanent

Par défaut, ce fichier de Swap sera désactivé au prochain redémarrage. Pour qu'il soit monté automatiquement, nous devons l'ajouter au fichier `/etc/fstab`.

Sauvegardez d'abord le fichier original :
```bash
sudo cp /etc/fstab /etc/fstab.bak
```

Ajoutez l'entrée pour le Swap à la fin du fichier :
```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Étape 6 : Optimiser l'utilisation du Swap (Swappiness)

Le paramètre `swappiness` définit la propension du système à utiliser le Swap plutôt que la RAM. La valeur va de 0 à 100 :
- `100` : le système utilisera le Swap de manière très agressive.
- `0` ou `10` : le système privilégiera la RAM jusqu'au dernier moment.

Par défaut, la valeur est souvent à `60`. Pour un serveur classique, une valeur de `10` est recommandée pour privilégier la réactivité (la RAM étant beaucoup plus rapide que le disque).

Vérifiez la valeur actuelle :
```bash
cat /proc/sys/vm/swappiness
```

Pour la modifier temporairement à `10` :
```bash
sudo sysctl vm.swappiness=10
```

Pour rendre ce changement permanent, éditez ou créez le fichier `/etc/sysctl.conf` :
```bash
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `swapon --show` | Lister les espaces de Swap actifs. |
| `swapoff -a` | Désactiver temporairement tous les espaces de Swap. |
| `free -m` | Afficher la RAM et le Swap utilisés (en Mo). |

## Ressources

- [Documentation Ubuntu sur le Swap](https://help.ubuntu.com/community/SwapFaq) — Les meilleures pratiques pour la gestion de l'espace d'échange.
- [Man page de mkswap](https://man7.org/linux/man-pages/man8/mkswap.8.html) — Référence technique de la commande `mkswap`.
