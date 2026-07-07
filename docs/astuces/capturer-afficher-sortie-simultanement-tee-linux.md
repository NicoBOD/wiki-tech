---
title: Capturer et afficher simultanément une sortie avec la commande tee sous Linux
date: 2026-07-04
author: Nicolas BODAINE
tags:
  - linux
  - terminal
  - bash
  - tee
  - astuces
difficulty: débutant
os: Linux
status: publié
---

# Capturer et afficher simultanément une sortie avec la commande tee sous Linux

!!! abstract "Résumé"
    La commande `tee` permet de lire l'entrée standard (stdin) et d'écrire le résultat **à la fois** sur la sortie standard (stdout, c'est-à-dire l'écran) et dans un fichier. C'est l'outil idéal pour consigner une commande longue dans un log tout en continuant à suivre son déroulement en direct, ou pour écrire dans un fichier protégé en écriture avec `sudo`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | GNU/Linux (Bash, Zsh) — macOS, Unix |
| Dernière mise à jour | 2026-07-04 |

## Contexte

Sous Linux, l'opérateur de redirection `>` (vu dans le tutoriel sur [les redirections des sorties standard et d'erreur](maitriser-redirections-sorties-standard-erreur-linux.md)) permet d'envoyer la sortie d'une commande dans un fichier. Le problème : le résultat **n'apparaît plus à l'écran**. Impossible donc de suivre en direct une commande longue comme une compilation, une mise à jour système ou un script de sauvegarde, tout en gardant une trace exacte de ce qui s'est affiché.

La commande `tee` résout ce problème en agissant comme un **té** (la lettre T) : le flux d'entrée arrive par le bas, puis se divise en deux sorties distinctes — l'écran d'un côté, un fichier de l'autre.

```text
            ┌──► stdout (écran)
stdin ──► tee ┤
            └──► fichier(s)
```

## Prérequis

- Une machine Linux (VM, WSL, distribution de test) avec un shell Bash.
- Avoir exécuté au moins une fois des redirections simples (`>`, `2>`) — voir la section « Contexte ».
- Des droits suffisants pour écrire dans le répertoire de travail (utilisateur courant, pas besoin de root sauf pour l'usage avancé avec `sudo`).

## Procédure

### Étape 1 : Comportement de base — afficher ET sauvegarder

La syntaxe minimale est la suivante :

```bash
commande | tee fichier.log
```

`tee` intercale dans le tuyau (pipe). Il récupère la sortie de `commande`, l'affiche dans le terminal **et** l'écrit dans `fichier.log`. Si le fichier n'existe pas, il est créé ; s'il existe, **il est écrasé**.

```bash
# Lister le contenu du répertoire à l'écran et dans une trace
ls -la /etc | tee /tmp/ls-etc.log
```

Vérifiez le contenu du fichier créé :

```bash
cat /tmp/ls-etc.log
```

### Étape 2 : Ajouter à la fin d'un fichier (mode append)

Comme pour la redirection `>>`, l'option `-a` (append) ajoute les données à la fin du fichier sans l'écraser. C'est indispensable pour tenir un journal cumulatif :

```bash
# Ajoute la date et l'heure de chaque exécution à un journal
date "+%F %T — exécution du script de sauvegarde" | tee -a /tmp/sauvegarde.log

# On relance plus tard : la ligne précédente est conservée
date "+%F %T — seconde exécution" | tee -a /tmp/sauvegarde.log
```

### Étape 3 : Capturer stderr en plus de stdout

Par défaut, `tee` ne traite que la sortie standard (`stdout`). Les messages d'erreur (`stderr`) passent au travers sans être enregistrés. Pour tout capturer, redirigez d'abord `stderr` vers `stdout` avec `2>&1` :

```bash
# find génère souvent des "Permission denied" sur stderr
# Cette commande affiche ET enregistre succès ET erreurs
find /var/log -name "*.log" 2>&1 | tee /tmp/find-log-all.txt
```

!!! tip "Raccourci Bash moderne"
    Avec Bash 4+ et la plupart des shells récents, `|&` est un équivalent concis de `2>&1 |` :

    ```bash
    find /var/log -name "*.log" |& tee /tmp/find-log-all.txt
    ```

### Étape 4 : Écrire dans plusieurs fichiers en une seule commande

`tee` accepte plusieurs noms de fichiers en arguments et écrit dans **tous** simultanément :

```bash
# Tracer une commande d'installation dans deux journaux distincts
echo "Début de l'installation" | tee install.log journal.log
```

Utile pour garder une copie locale d'un log tout en alimentant un emplacement réseau (point de montage secondaire, NAS, etc.).

### Étape 5 : Écrire dans un fichier root avec sudo

Un cas très fréquent en administration système : on veut écrire **depuis son utilisateur courant** dans un fichier que seul `root` peut modifier (par exemple `/etc/hosts` ou un fichier de log système). La redirection `>` classique ne fonctionne pas car la redirection est exécutée par le shell de l'utilisateur, pas par `sudo` :

```bash
# ❌ NE FONCTIONNE PAS : le shell ouvre le fichier AVANT le sudo
echo "127.0.0.1 monsite.local" | sudo > /etc/hosts
```

Avec `tee`, le programme `sudo` s'exécute **en premier**, et c'est `tee` (devenu root) qui ouvre et écrit le fichier :

```bash
# ✅ Correct : tee écrit avec les droits root
echo "127.0.0.1 monsite.local" | sudo tee -a /etc/hosts
```

!!! warning "Pas d'option -a = écrasement"
    Sans `-a`, `tee` écrase le fichier cible. Pour `/etc/hosts`, on veut généralement **ajouter** une ligne, donc `-a` est indispensable. Pensez à vérifier avec `cat /etc/hosts` après chaque opération.

### Étape 6 : Ne rien afficher à l'écran (mode silencieux pour les scripts)

Parfois, on veut simplement écrire dans un fichier comme le ferait `>`, mais en profitant du contournement de droits offert par `tee`. On redirige alors la sortie de `tee` vers `/dev/null` pour la faire disparaître de l'écran :

```bash
# Écrit dans le log système root sans rien afficher
echo "Ligne de maintenance" | sudo tee /var/log/maintenance.log > /dev/null
```

### Étape 7 : Combiner tee avec un pipeline long

`tee` s'intercale dans n'importe quel pipeline. On peut ainsi tracer une étape intermédiaire tout en continuant à traiter les données :

```bash
# 1. Lister les fichiers .conf → 2. (tee) garder une copie → 3. Filtrer avec grep
ls /etc/*.conf 2>/dev/null | tee /tmp/conf-brut.txt | grep "^/etc/net"
```

Le fichier `/tmp/conf-brut.txt` contient **la liste complète avant filtrage**, tandis que l'écran n'affiche que le résultat filtré. Très pratique pour déboguer un pipeline qui ne produit pas le résultat attendu.

## Vérification

Tapez successivement les commandes ci-dessous dans votre terminal de test :

```bash
# 1. Création et écriture
echo "première ligne" | tee /tmp/test-tee.log
cat /tmp/test-tee.log

# 2. Ajout
echo "deuxième ligne" | tee -a /tmp/test-tee.log
cat /tmp/test-tee.log

# 3. Capture de stderr
ls /repertoire_inexistant 2>&1 | tee /tmp/test-erreurs.log
cat /tmp/test-erreurs.log
```

!!! success "Résultat attendu"
    - Le fichier `/tmp/test-tee.log` contient exactement deux lignes (`première ligne` puis `deuxième ligne`), preuve que `-a` ajoute sans écraser.
    - Le fichier `/tmp/test-erreurs.log` contient le message d'erreur `ls: cannot access '/repertoire_inexistant'`, preuve que `2>&1` a bien capturé stderr dans le tuyau.
    - Chaque ligne est **apparue à l'écran** en même temps qu'elle était écrite dans le fichier.

## Aide-mémoire

| Commande / Action | Description |
|-------------------|-------------|
| `commande \| tee f.log` | Affiche la sortie à l'écran **et** l'écrit dans `f.log` (écrase). |
| `commande \| tee -a f.log` | Idem, mais **ajoute** à la fin du fichier. |
| `commande 2>&1 \| tee f.log` | Capture stdout **et** stderr dans le fichier. |
| `commande \| tee a.log b.log` | Écrit dans **plusieurs fichiers** en parallèle. |
| `echo ... \| sudo tee /etc/fichier` | Écrit dans un fichier root depuis son utilisateur (contourne le sudo). |
| `commande \| tee f.log > /dev/null` | Écrit dans le fichier sans rien afficher à l'écran. |
| `kill -l \| tee signals.txt` | Sauvegarde une référence rapide du man dans un fichier texte. |

## Ce qu'il faut retenir

- `tee` = **afficher ET sauvegarder** simultanément, là où `>` ne fait que sauvegarder.
- L'option `-a` évite l'écrasement accidentel d'un journal existant.
- `2>&1` (ou `|&`) est nécessaire pour capturer aussi les messages d'erreur.
- `sudo tee` est **la** méthode propre pour écrire dans un fichier root depuis un utilisateur non privilégié.
- `tee` s'intercale dans n'importe quel pipeline : parfait pour tracer une étape intermédiaire pendant le debug.

## Ressources

- [Man page tee(1) — Linux man-pages](https://man7.org/linux/man-pages/man1/tee.1.html) — Page de manuel officielle et complète.
- [Documentation GNU Coreutils — tee invocation](https://www.gnu.org/software/coreutils/manual/html_node/tee-invocation.html) — Référence de la version GNU de `tee` (implémentation par défaut sur la plupart des Linux).
- [POSIX.1-2017 — tee utility](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/tee.html) — Spécification POSIX minimale respectée par tous les Unix.
- [Man page tee(1) — die.net](https://linux.die.net/man/1/tee) — Miroir de la page de manuel en ligne.
