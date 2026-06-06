---
title: Rechercher des fichiers sous Linux avec la commande find
date: 2026-06-06
author: Nicolas BODAINE
tags:
  - linux
  - systeme
  - terminal
  - cli
difficulty: débutant
os: Linux
status: publié
---

# Rechercher des fichiers sous Linux avec la commande find

!!! abstract "Résumé"
    La commande `find` est l'un des outils les plus puissants et indispensables sous Linux. Elle permet de rechercher des fichiers et des dossiers dans l'arborescence selon de multiples critères (nom, taille, date de modification, permissions, etc.) et même d'exécuter des actions sur les résultats trouvés.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Ubuntu / Debian / RHEL / Any Linux |
| Dernière mise à jour | 2026-06-06 |

## Contexte

Dans la gestion quotidienne d'un serveur ou d'un poste de travail Linux, vous serez souvent confronté à la perte de fichiers, à la recherche de journaux volumineux ou au besoin de nettoyer des données anciennes. Contrairement à une interface graphique où l'on utilise une barre de recherche, le terminal propose `find`, un outil extrêmement précis qui parcourt récursivement vos répertoires.

Ce tutoriel s'adresse aux débutants et présente les utilisations les plus courantes et pratiques de `find` pour des opérations de base et de maintenance.

## Prérequis

- Un accès à un terminal Linux (machine virtuelle, WSL, serveur distant).
- Des droits utilisateurs standard (certains dossiers nécessiteront les droits `root` ou `sudo` pour être fouillés).

## Procédure

La syntaxe de base de `find` est toujours la même :
```bash
find [chemin_de_départ] [options_de_recherche] [action]
```
Par défaut, si vous ne spécifiez pas d'action, `find` affichera simplement les chemins des fichiers trouvés à l'écran.

### 1. Rechercher par nom de fichier

C'est l'utilisation la plus fréquente. On utilise l'option `-name` (sensible à la casse) ou `-iname` (insensible à la casse).

Rechercher un fichier dont on connaît le nom exact dans le dossier `/etc` :
```bash
find /etc -name "passwd"
```

Rechercher tous les fichiers se terminant par `.log` dans `/var/log` :
```bash
find /var/log -name "*.log"
```

!!! tip "Attention aux guillemets"
    Il est recommandé d'entourer vos motifs de recherche (comme `*.log`) par des guillemets. Cela évite que le terminal (le shell) n'interprète l'astérisque avant que la commande `find` ne s'exécute.

### 2. Rechercher par type

Vous pouvez limiter la recherche aux fichiers standards, aux dossiers, ou aux liens symboliques avec l'option `-type`.

- `f` : fichier (file)
- `d` : dossier (directory)
- `l` : lien symbolique (link)

Lister uniquement les **dossiers** nommés `backup` dans le répertoire courant (`.`) :
```bash
find . -type d -name "backup"
```

### 3. Rechercher par taille

Idéal pour identifier ce qui consomme de l'espace disque. L'option `-size` permet de spécifier une taille avec un préfixe `+` (plus grand que) ou `-` (plus petit que).
Les unités courantes sont `k` (kilo-octets), `M` (méga-octets), et `G` (giga-octets).

Trouver tous les fichiers de plus de 100 Mo dans `/var` :
```bash
find /var -type f -size +100M
```

Trouver les fichiers dont la taille est exactement de 0 octet (fichiers vides) :
```bash
find . -type f -size 0
```
*(Vous pouvez aussi utiliser le raccourci `find . -type f -empty`)*

### 4. Rechercher par date de modification

L'option `-mtime` (modification time) permet de chercher des fichiers selon leur âge en **jours**.

Trouver les fichiers modifiés il y a **moins de 7 jours** dans votre dossier personnel :
```bash
find /home/$USER -type f -mtime -7
```

Trouver les fichiers modifiés il y a **plus de 30 jours** :
```bash
find /home/$USER -type f -mtime +30
```

### 5. Exécuter une commande sur les résultats trouvés

C'est là que `find` devient redoutable pour l'automatisation. L'option `-exec` permet de lancer une commande sur chaque fichier trouvé.
La syntaxe requiert `{} ` (qui représente le fichier trouvé) et de terminer la commande par `\;`.

Trouver et supprimer (`rm`) tous les fichiers `.bak` dans le dossier courant :
```bash
find . -type f -name "*.bak" -exec rm {} \;
```

Changer les permissions (`chmod 644`) de tous les fichiers d'un répertoire `/var/www/html` :
```bash
find /var/www/html -type f -exec chmod 644 {} \;
```

!!! warning "Prudence avec `rm`"
    Avant d'utiliser `-exec rm {} \;`, lancez toujours la commande `find` sans l'option `-exec` pour vérifier la liste des fichiers qui seront impactés !

## Aide-mémoire

| Commande `find` | Ce qu'elle fait |
|-----------------|-----------------|
| `find . -name "fichier.txt"` | Cherche "fichier.txt" dans le dossier courant |
| `find / -type f -name "*.conf"` | Cherche tous les fichiers `.conf` sur tout le système |
| `find /var/log -mtime +15` | Trouve les fichiers de plus de 15 jours dans /var/log |
| `find . -size +50M` | Trouve les fichiers de plus de 50 Mo |
| `find . -type d -empty` | Trouve tous les dossiers vides |

## Ressources

- [Manuel Ubuntu - find(1)](https://manpages.ubuntu.com/manpages/jammy/en/man1/find.1.html) — Documentation officielle des manpages.
- [GNU Findutils](https://www.gnu.org/software/findutils/) — Le projet officiel derrière la commande `find`.