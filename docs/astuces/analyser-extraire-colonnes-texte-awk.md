---
title: "Analyser et extraire des colonnes de texte sous Linux avec awk"
date: 2026-06-26
author: Nicolas BODAINE
tags:
  - awk
  - linux
  - terminal
  - bash
  - texte
difficulty: intermédiaire
os: Linux
status: publié
---

# Analyser et extraire des colonnes de texte sous Linux avec awk

!!! abstract "Résumé"
    Ce tutoriel montre comment utiliser la commande `awk` sous Linux pour analyser, extraire et manipuler efficacement des données tabulaires ou colonnées directement depuis le terminal.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux |
| Dernière mise à jour | 2026-06-26 |

## Contexte

Dans l'administration système et l'automatisation, il est courant de devoir extraire des informations précises depuis la sortie d'une commande (comme `df`, `ps` ou `ls`) ou depuis des fichiers de log. Bien que `cut` puisse extraire des colonnes, il gère très mal les séparateurs multiples (comme des espaces consécutifs). 

`awk` est un outil de traitement de texte très puissant (c'est en fait un langage de programmation à part entière) qui gère nativement et proprement les espaces multiples et permet de filtrer et de reformater facilement les données.

## Prérequis

- Un terminal Linux (n'importe quelle distribution).
- Le programme `awk` installé (il l'est par défaut sur presque toutes les distributions GNU/Linux).

## Procédure

### Étape 1 : Comprendre le principe de base

Par défaut, `awk` lit le texte ligne par ligne, et considère que les mots sont séparés par un ou plusieurs espaces ou tabulations.
Il affecte chaque mot à une variable spéciale :

- `$1` pour la première colonne
- `$2` pour la deuxième colonne
- `$0` représente la ligne entière

Prenons un exemple avec la commande `ls -l` :

```bash
ls -l /var/log | head -n 5
```

Sortie typique :
```text
total 1234
-rw-r--r-- 1 root root  4321 Jun 26 10:00 auth.log
-rw-r--r-- 1 root root  9876 Jun 26 09:50 syslog
```

### Étape 2 : Extraire des colonnes simples

Pour afficher uniquement les tailles de fichiers (colonne 5) et leurs noms (colonne 9), on redirige (pipe) la sortie vers `awk` et on utilise l'instruction `print` :

```bash
ls -l /var/log | awk '{print $5, $9}'
```

Le résultat affichera la taille et le nom, séparés par un espace.

!!! tip "Ignorer les en-têtes"
    Si la première ligne est un en-tête (comme `total 1234`), on peut dire à `awk` de l'ignorer grâce à `NR` (Number of Record), qui contient le numéro de la ligne courante. Pour lire à partir de la ligne 2 :
    ```bash
    ls -l /var/log | awk 'NR > 1 {print $5, $9}'
    ```

### Étape 3 : Filtrer selon des conditions

`awk` permet aussi de n'afficher des colonnes que si une condition est remplie.
Par exemple, comment trouver les partitions utilisant plus de 80% de leur espace ?

Regardons la sortie de `df -h` :
```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   45G  2.5G  90% /
/dev/sdb1       100G   10G   85G  10% /data
```

La colonne contenant le pourcentage d'utilisation est la 5e (`$5`).

On peut demander à `awk` d'enlever le symbole `%` et de tester si la valeur est supérieure à 80 :

```bash
df -h | awk 'NR > 1 { 
    pourcentage = $5; 
    sub("%", "", pourcentage); 
    if (pourcentage > 80) { 
        print "Alerte espace sur " $1 " (" $5 ")" 
    } 
}'
```

!!! note "Explication"
    - `NR > 1` ignore la ligne d'en-tête de `df`.
    - `sub("%", "", pourcentage)` supprime le caractère `%` pour pouvoir comparer numériquement.
    - `if (pourcentage > 80)` vérifie notre condition.
    - `print` formate notre alerte personnalisée.

### Étape 4 : Changer le séparateur (fichiers CSV ou /etc/passwd)

Parfois, les colonnes ne sont pas séparées par des espaces. Par exemple, le fichier `/etc/passwd` utilise des deux-points (`:`).
Pour dire à `awk` d'utiliser `:` comme séparateur, on utilise l'option `-F`.

Exemple pour extraire les noms d'utilisateurs (colonne 1) et leurs interpréteurs de commandes (shells, colonne 7) :

```bash
awk -F':' '{print $1 " utilise " $7}' /etc/passwd
```

## Aide-mémoire

| Commande `awk` / Variable | Description |
|---------------------------|-------------|
| `awk '{print $1}'` | Affiche la première colonne |
| `awk -F':' '{print $1}'` | Utilise `:` comme séparateur de colonnes |
| `$0`, `$1`, `$2` | Ligne complète, colonne 1, colonne 2 |
| `NR` | Numéro de la ligne en cours de lecture |
| `NF` | Nombre total (Number of Fields) de colonnes sur la ligne courante |
| `awk 'NR==3 {print $0}'` | Affiche uniquement la 3ème ligne |

## Ressources

- [Manuel GNU Awk](https://www.gnu.org/software/gawk/manual/gawk.html) — La documentation officielle (très complète).
- `man awk` depuis le terminal Linux.
