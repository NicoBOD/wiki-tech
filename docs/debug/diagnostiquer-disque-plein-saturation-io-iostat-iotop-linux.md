---
title: Diagnostiquer un disque plein ou une saturation I/O sur Linux avec iostat et iotop
date: 2026-07-04
author: Nicolas BODAINE
tags:
  - linux
  - debug
  - disque
  - iostat
  - iotop
  - performances
  - sysstat
difficulty: intermédiaire
os: Linux
status: publié
---

# Diagnostiquer un disque plein ou une saturation I/O sur Linux avec iostat et iotop

!!! abstract "Résumé"
    Un serveur Linux qui ralentit sans reason apparente, des applications qui se bloquent ou des temps de réponse qui explosent : la cause est souvent un disque saturé. Apprenez à identifier un disque plein et à quantifier une saturation d'entrées/sorties (I/O) avec `iostat` et `iotop`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Ubuntu / Debian / RHEL / Rocky |
| Dernière mise à jour | 2026-07-04 |

## Contexte

Une baisse de performances d'un serveur Linux se manifeste souvent par des symptômes trompeurs : pages web lentes, base de données qui mouline, commandes qui mettent plusieurs secondes à répondre alors que le CPU et la RAM semblent au repos. Dans beaucoup de cas, le vrai coupable est le **disque** — soit parce qu'il est plein, soit parce que les opérations de lecture/écriture saturent la bande passante du périphérique de stockage.

Linux possède deux outils complémentaires pour diagnostiquer ces situations :

- **`iostat`** : affiche des statistiques agrégées par périphérique de bloc (débit, temps d'attente, taux d'utilisation).
- **`iotop`** : affiche, comme `htop` mais pour les disques, quels processus consomment le plus d'I/O en temps réel.

Ce tutoriel explique comment les installer, les utiliser et interpréter leurs sorties pour identifier la cause d'une saturation disque.

## Prérequis

- Un accès terminal (local ou via SSH) à une machine Linux.
- Les droits d'administration (`sudo`) pour installer les paquets.
- Idéalement une machine de test (VM, conteneur ou poste de lab) sur laquelle vous pouvez générer une charge I/O sans risques.

!!! tip "Lab reproductible"
    Ce tutoriel est entièrement reproductible dans une VM Ubuntu 24.04 ou Rocky Linux 9. Les commandes de génération de charge fournies plus bas permettent de simuler une saturation sans matériel spécifique.

## Procédure

### Étape 1 : Détecter un disque plein avec `df` et `du`

Avant de parler de performances, éliminons d'abord l'hypothèse la plus simple : un disque **plein** (100 % d'utilisation de l'espace).

```bash
df -h
```

**Exemple de sortie :**

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda2        49G   38G  8.9G  81% /
tmpfs           3.9G     0  3.9G   0% /dev/shm
/dev/sda1       511M  6.1M  505M   2% /boot/efi
```

Vérifiez la colonne **Use%**. À partir de 90–95 %, le système devient instable :

- Impossible d'écrire dans `/var/log` (les journaux échouent).
- Les bases de données refusent les transactions.
- Le système ne peut plus créer de fichiers temporaires.

!!! warning "Seuils critiques d'occupation"
    La plupart des systèmes de fichiers ext4/xfs réservent ~5 % des blocs pour `root`. Un volume affiché à 95 % est donc en pratique déjà saturé pour les utilisateurs non privilégiés. Intervenez avant d'atteindre 90 %.

Pour identifier **qui** occupe l'espace, utilisez `du` :

```bash
# Taille de chaque répertoire de premier niveau, triée du plus grand au plus petit
sudo du -h --max-depth=1 / 2>/dev/null | sort -rh | head -15
```

```bash
# Zoom sur /var (souvent le coupable : logs, caches, bases de données)
sudo du -h --max-depth=1 /var 2>/dev/null | sort -rh | head -10
```

!!! note "Inodes : un disque peut être « plein » sans que l'espace le soit"
    Chaque fichier consomme un *inode* (structure de métadonnées). Un disque peut avoir 30 % d'espace libre mais 0 inode disponible (typique quand un programme crée des millions de petits fichiers). Vérifiez avec `df -i`.

### Étape 2 : Installer `iostat` (paquet sysstat)

`iostat` fait partie du paquet **sysstat**, qui regroupe plusieurs outils de mesure des performances système.

=== "Ubuntu / Debian"

    ```bash
    sudo apt update
    sudo apt install sysstat
    ```

=== "RHEL / Rocky Linux / AlmaLinux"

    ```bash
    sudo dnf install sysstat
    ```

Activez la collecte de statistiques système (désactivée par défaut sur Debian/Ubuntu) :

```bash
# Sur Ubuntu/Debian : éditer /etc/default/sysstat
sudo sed -i 's/^ENABLED="false"/ENABLED="true"/' /etc/default/sysstat
sudo systemctl restart sysstat
sudo systemctl enable sysstat
```

Vérifiez l'installation :

```bash
iostat -V
```

### Étape 3 : Lire les statistiques globales avec `iostat`

Lancez d'abord une vue d'ensemble (`-x` pour les statistiques étendues, `-h` pour un format lisible par l'humain) :

```bash
iostat -xh
```

**Exemple de sortie :**

```text
Linux 6.8.0-45-generic (srv-lab)   04/07/26   _x86_64_   (4 CPU)

Device            r/s     w/s    rkB/s   wkB/s   %util  await  r_await  w_await
sda              12.40   35.80    68.20  420.30   62.1   12.6      8.2     13.8
sdb               0.10    0.05     0.80    0.40    0.2    5.1      4.9      5.5
```

**Colonnes à surveiller en priorité :**

| Colonne | Signification | Seuil d'alerte |
|---------|---------------|----------------|
| `%util` | Pourcentage de temps pendant lequel le disque a traité au moins une requête. | > 80 % durablement = saturation |
| `await` | Temps moyen d'attente (en ms) d'une requête I/O (file d'attente + service). | > 20–30 ms = latence élevée pour un SSD, > 50 ms pour un disque mécanique |
| `r/s` / `w/s` | Requêtes de lecture / écriture par seconde. | Dépend du matériel, mais une explosion soudaine indique une charge anormale |
| `rkB/s` / `wkB/s` | Débit de lecture / écriture en ko/s. | Comparez aux spécifications du disque |

!!! tip "Comprendre `%util`"
    `%util` est l'indicateur le plus simple : un disque à **95 % d'utilisation** sur une période de plusieurs minutes est canoniquement saturé. Attention cependant : avec les SSD NVMe capables de traiter plusieurs requêtes en parallèle, `%util` peut atteindre 100 % sans que le disque soit réellement à genoux. Complétez toujours avec `await`.

### Étape 4 : Suivre les statistiques en continu

Pour observer l'évolution dans le temps, demandez à `iostat` de rafraîchir l'affichage toutes les secondes :

```bash
iostat -xz 1
```

- `-x` : statistiques étendues.
- `-z` : masque les périphériques inactifs (utile pour ignorer les disques sans activité).
- `1` : intervalle de 1 seconde.

Appuyez sur ++ctrl+c++ pour arrêter.

### Étape 5 : Installer et lancer `iotop` pour identifier les processus

`iostat` vous dit *quel disque* est saturé, mais pas *quel processus* en est responsable. C'est le rôle d'**`iotop`**.

=== "Ubuntu / Debian"

    ```bash
    sudo apt install iotop
    ```

=== "RHEL / Rocky Linux / AlmaLinux"

    ```bash
    sudo dnf install iotop
    ```

Lancez-le **en root** (l'accès aux statistiques I/O par processus nécessite les privilèges administrateur) :

```bash
sudo iotop
```

**Comprendre l'interface :**

| Colonne | Description |
|---------|-------------|
| `TID` | Identifiant du thread. |
| `PRIO` | Priorité I/O (la classe `be/4` = best-effort, niveau 4). |
| `USER` | Utilisateur propriétaire du processus. |
| `DISK READ` | Débit de lecture actuel. |
| `DISK WRITE` | Débit d'écriture actuel (y compris le cache sale). |
| `SWAPIN` | Pourcentage de temps passé à lire dans le swap. |
| `IO` | Pourcentage de temps passé à attendre des I/O. **← colonne clé** |
| `COMMAND` | Nom du processus. |

!!! warning "La colonne `IO` est l'indicateur principal"
    Une valeur élevée dans la colonne `IO>` signifie que le processus passe son temps à *attendre* le disque. C'est le symptôme direct d'un processus bloqué par la lenteur du stockage.

**Raccourcis utiles dans `iotop` :**

- ++o+/** ++or ++o++ : n'afficher que les processus qui génèrent effectivement des I/O (très pratique pour isoler le coupable).
- ++a++ : bascule en mode « accumulateur » (cumul des I/O au lieu d'un instantané).
- ++q++ : quitter.

### Étape 6 : Simuler une saturation I/O pour s'exercer (lab)

Pour reproduire une saturation sur une VM de test, **n'exécutez jamais ces commandes en production**.

```bash
# 1. Charge en écriture : écrit un gros fichier avec dd
dd if=/dev/zero of=/tmp/charge-test bs=1M count=4096 oflag=direct
```

```bash
# 2. Charge en lecture aléatoire avec fio (si installé)
sudo apt install fio  # Ubuntu/Debian
fio --name=test-lab --filename=/tmp/fio-test --rw=randread --bs=4k --size=1G --runtime=60 --time_based --ioengine=libaio --iodepth=32
```

Pendant que la charge tourne, ouvrez un second terminal et lancez en parallèle :

```bash
sudo iotop -o
```

```bash
iostat -xz 1
```

Vous devriez voir `dd` ou `fio` dominer la colonne `DISK WRITE`/`DISK READ` dans `iotop`, et le `%util` du disque concerné grimper vers 100 % dans `iostat`.

### Étape 7 : Identifier la cause et agir

Une fois le coupable identifié, les actions dépendent du contexte :

| Cause fréquente | Action corrective |
|-----------------|-------------------|
| Base de données qui fait trop de `fsync` | Régler `wal_buffers` / `synchronous_commit` (PostgreSQL), ou déplacer les données sur un disque plus rapide (SSD/NVMe). |
| Log applicatif verbeux | Réduire le niveau de log, activer la rotation (`logrotate`), ou déplacer `/var/log` sur un disque dédié. |
| Swap massif (le système pagine sur disque faute de RAM) | Ajouter de la RAM ou identifier le processus qui consomme la mémoire avec `htop`. Voir le tutoriel [Diagnostiquer la consommation CPU et mémoire avec htop et free](diagnostiquer-consommation-cpu-memoire-htop-free.md). |
| Disque mécanique (HDD) incapable de suivre une charge aléatoire | Migrer vers un SSD ou répartir les I/O sur plusieurs disques (RAID, LVM). |
| Tâche de sauvegarde ou d'indexation planifiée | Décaler sa planification avec `cron` hors des heures de pointe. Voir [Planifier des tâches récurrentes avec cron](../automatisation/planifier-taches-recurrentes-linux-cron-crontab.md). |

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `df -h` | Vérifie l'espace libre sur tous les systèmes de fichiers. |
| `df -i` | Vérifie la disponibilité des inodes. |
| `du -h --max-depth=1 <dir> \| sort -rh \| head` | Trouve les répertoires les plus volumineux. |
| `iostat -xh` | Statistiques I/O étendues, format lisible, un seul instantané. |
| `iostat -xz 1` | Statistiques I/O étendues rafraîchies chaque seconde. |
| `sudo iotop` | Vue temps réel des processus consommateurs d'I/O. |
| `sudo iotop -o` | N'affiche que les processus actifs en I/O. |
| `iostat -V` | Vérifie la version installée de sysstat. |

## Glossaire

I/O
:   Entrées/sorties. Désigne les opérations de lecture et d'écriture d'un programme vers un périphérique de stockage (disque, SSD).

`%util`
:   Pourcentage de temps pendant lequel un périphérique de bloc a eu au moins une requête en cours d'exécution. C'est l'indicateur de saturation le plus immédiat.

`await`
:   Temps moyen (en millisecondes) mis par une requête I/O entre son émission et sa complétion. Inclut l'attente dans la file du noyau et le temps de service du disque.

IOPS
:   *Input/Output Operations Per Second*. Mesure le nombre d'opérations I/O élémentaires par seconde. Les SSDaltenativement cités en kIOPS (milliers) dépassent largement les disques mécaniques.

`iotop`
:   Outil interactif, équivalent de `htop` pour les I/O, qui affiche en temps réel les débits de lecture/écriture par processus.

## Vérification

Pour confirmer qu'une saturation I/O a été résolue, relancez les deux outils de surveillance :

```bash
iostat -xz 5
```

```bash
sudo iotop -o
```

!!! success "Résultat attendu"
    Après suppression de la cause, `%util` doit redescendre sous les 30–50 %, `await` sous 10 ms pour un SSD / 20 ms pour un HDD, et aucune entrée ne doit apparaître durablement dans `iotop -o`.

## Ressources

- [Documentation officielle sysstat (iostat)](https://sysstat.github.io/) — Manuel de référence de l'écosystème sysstat.
- [Man page iostat(1) — linux man-pages](https://man7.org/linux/man-pages/man1/iostat.1.html) — Description complète des colonnes et options.
- [Man page iotop(8) — linux man-pages](https://man7.org/linux/man-pages/man8/iotop.8.html) — Référence de l'outil iotop.
- [Red Hat Performance Tuning Guide — I/O monitoring](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/) — Guide officiel d'analyse de performance.
- [Ubuntu Server Guide — Monitoring](https://ubuntu.com/server/docs) — Documentation serveur Ubuntu, sections monitoring et performance.
