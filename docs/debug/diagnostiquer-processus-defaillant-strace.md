---
title: Diagnostiquer un processus défaillant avec strace
date: 2026-06-17
author: Nicolas BODAINE
tags:
  - linux
  - debug
  - strace
  - processus
difficulty: intermédiaire
os: Ubuntu 24.04
status: publié
---

# Diagnostiquer un processus défaillant avec strace

!!! abstract "Résumé"
    Apprenez à utiliser `strace` pour espionner les appels système (syscalls) d'un processus sous Linux. C'est l'outil de référence lorsqu'une application crashe, boucle ou gèle silencieusement sans laisser de traces dans les logs.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux (Debian, Ubuntu) |
| Dernière mise à jour | 2026-06-17 |

## Contexte

Il arrive souvent qu'une application échoue mystérieusement au démarrage, bloque en cours d'exécution, ou renvoie une erreur inexpliquée ("Fichier introuvable", "Permission refusée") sans qu'aucun message explicite ne soit consigné dans les logs. Dans ces situations "boîte noire", la seule façon de comprendre ce qui bloque est de regarder sous le capot : observer comment le programme interagit avec le système d'exploitation.

`strace` (System Call Trace) intercepte et enregistre les **appels système** effectués par un processus, c'est-à-dire toutes les requêtes que le programme envoie au noyau Linux (ouvrir un fichier, lire un répertoire, allouer de la mémoire, écouter sur un port réseau, etc.).

## Prérequis

- Un système Linux.
- Les droits d'administration (`sudo` ou `root`) pour observer les processus système.
- L'outil `strace` installé sur la machine.

## Procédure

### Étape 1 : Installer strace

Sur une distribution basée sur Debian/Ubuntu :

```bash
sudo apt update
sudo apt install strace -y
```

### Étape 2 : Lancer et analyser une commande

Pour analyser un programme dès son démarrage, il suffit de le précéder de la commande `strace`. Par exemple, essayons de lire un fichier qui n'existe pas :

```bash
strace cat fichier_inexistant.txt
```

La sortie peut être très verbeuse, car le système doit charger de nombreuses bibliothèques partagées avant même d'exécuter l'action. Observez particulièrement les dernières lignes :

```text
...
openat(AT_FDCWD, "fichier_inexistant.txt", O_RDONLY) = -1 ENOENT (No such file or directory)
write(2, "cat: fichier_inexistant.txt: No "..., 52cat: fichier_inexistant.txt: No such file or directory
) = 52
close(1)                                = 0
close(2)                                = 0
exit_group(1)                           = ?
+++ exited with 1 +++
```
L'erreur est visible sur l'appel `openat` : le fichier demandé n'existe pas (`ENOENT`).

### Étape 3 : S'attacher à un processus en cours

Si un service est gelé ou consomme anormalement du CPU, vous pouvez vous "attacher" au processus via son PID.

1. Identifiez le PID avec `ps`, `top` ou `htop` :
   ```bash
   pidof nginx
   ```
2. Attachez `strace` au PID avec l'option `-p` :
   ```bash
   sudo strace -p <PID>
   ```
!!! tip "Processus enfants"
    Beaucoup de services (comme Nginx ou Apache) créent des processus enfants (workers). Ajoutez l'option `-f` pour suivre automatiquement tous les processus enfants créés : `sudo strace -f -p <PID>`.

### Étape 4 : Filtrer la sortie de strace

La sortie de `strace` est souvent énorme. L'option `-e` permet de filtrer l'affichage pour ne conserver que ce qui vous intéresse.

**Filtrer par type de fichier (ouverture/lecture) :**
```bash
strace -e openat,read <commande>
```

**Filtrer les opérations réseau :**
```bash
strace -e trace=network <commande>
```

**Obtenir un résumé statistique des appels système au lieu du détail complet :**
L'option `-c` affiche un tableau de profilage récapitulatif à la fin de l'exécution, très utile pour identifier les goulets d'étranglement :
```bash
strace -c ls -la
```

## Problème courant

!!! failure "Message d'erreur"
    ```text
    strace: attach: ptrace(PTRACE_SEIZE, 1234): Operation not permitted
    ```

Cela se produit lorsque vous essayez de vous attacher à un processus dont vous n'êtes pas propriétaire, ou si les politiques de sécurité (comme YAMA) interdisent le traçage.

### Solution
1. Utilisez `sudo` devant votre commande `strace`.
2. Si vous tracez souvent en local pour le développement et que vous comprenez les risques, vous pouvez temporairement autoriser le ptrace pour tout utilisateur (sur un environnement de test uniquement) :
   ```bash
   echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
   ```

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `strace <cmd>` | Exécute et trace une commande. |
| `strace -p <pid>` | S'attache à un processus en cours de fonctionnement. |
| `strace -f` | Suit les processus enfants (forks). |
| `strace -e <syscall>` | Ne trace qu'un ou plusieurs appels système spécifiques (ex: `openat`). |
| `strace -c` | Affiche un résumé détaillé avec le temps passé dans chaque appel système. |
| `strace -o log.txt` | Enregistre la sortie dans un fichier plutôt que de l'afficher à l'écran. |

## Ressources

- [Manuel de strace (man 1 strace)](https://man7.org/linux/man-pages/man1/strace.1.html) — Documentation officielle du projet.
- [Red Hat : Troubleshooting with strace](https://access.redhat.com/articles/2483) — Guide pratique d'utilisation orienté administrateur système.