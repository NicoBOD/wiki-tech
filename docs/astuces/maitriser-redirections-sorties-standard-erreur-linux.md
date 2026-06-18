---
title: Maîtriser les redirections des sorties standard et d'erreur sous Linux (> et 2>)
date: 2026-06-18
author: Nicolas BODAINE
tags:
  - linux
  - bash
  - astuces
  - sysadmin
difficulty: débutant
os: Linux
status: publié
---

# Maîtriser les redirections des sorties standard et d'erreur sous Linux (> et 2>)

!!! abstract "Résumé"
    Sous Linux, chaque commande produit une sortie qui s'affiche à l'écran. Comprendre la différence entre la sortie standard (`stdout`) et la sortie d'erreur (`stderr`), et savoir les rediriger, est fondamental pour la création de scripts, le debug et l'automatisation. Ce guide vous apprend à dompter les flux de redirection avec `>` et `2>`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | GNU/Linux (Bash, Zsh) |
| Dernière mise à jour | 2026-06-18 |

## Contexte

Dans les environnements Linux, la ligne de commande fonctionne sur un principe de flux (streams). Par défaut, une commande possède trois flux standard :
1. **L'entrée standard (stdin) - descripteur 0 :** Les données envoyées à la commande (souvent le clavier).
2. **La sortie standard (stdout) - descripteur 1 :** Le résultat normal de la commande.
3. **La sortie d'erreur (stderr) - descripteur 2 :** Les messages d'erreur.

Quand vous lancez une commande, `stdout` et `stderr` s'affichent par défaut dans votre terminal. Cependant, lors de la création d'un script ou de l'analyse d'une longue sortie, il est indispensable de pouvoir les séparer (par exemple, sauvegarder les résultats tout en ignorant les erreurs).

## Rediriger la sortie standard (stdout)

Pour rediriger le résultat d'une commande vers un fichier, on utilise le chevron `>`. Le chiffre `1` (pour `stdout`) est implicite : on peut écrire `1>` ou simplement `>`.

### Écraser ou créer un fichier
L'opérateur `>` écrase le contenu du fichier s'il existe, ou le crée s'il n'existe pas.

```bash
# Écrit le résultat de la commande 'ls -la' dans un fichier 'liste_fichiers.txt'
ls -la > liste_fichiers.txt
```

### Ajouter à un fichier existant (append)
Si vous souhaitez conserver le contenu d'un fichier et ajouter de nouvelles données à la fin, utilisez le double chevron `>>`.

```bash
# Ajoute la date actuelle à la fin du fichier 'historique.log'
date >> historique.log
```

## Rediriger la sortie d'erreur (stderr)

La redirection des erreurs se fait avec le descripteur `2` suivi du chevron `>`. Cela est très pratique pour isoler les messages d'erreur dans un fichier de logs.

```bash
# Recherche de fichiers (certains dossiers donneront une erreur 'Permission denied')
# Les erreurs seront écrites dans 'erreurs.log'
find / -name "passwd" 2> erreurs.log
```
*Note : Seuls les messages d'erreur iront dans le fichier, le reste de la recherche (les succès) continuera de s'afficher à l'écran.*

## Combiner les redirections (stdout et stderr)

### Séparer les résultats et les erreurs
Vous pouvez rediriger les résultats dans un fichier, et les erreurs dans un autre en une seule commande :

```bash
find / -name "passwd" > resultats.txt 2> erreurs.log
```

### Regrouper stdout et stderr dans le même fichier
Parfois, on souhaite garder une trace complète de l'exécution, succès comme erreurs. On utilise alors la syntaxe `2>&1` (qui signifie "redirige le flux 2 vers le même endroit que le flux 1").

```bash
# Redirige d'abord stdout vers log_complet.txt, puis y attache stderr
/opt/scripts/backup.sh > log_complet.txt 2>&1
```

**Astuce Bash moderne :**
Avec Bash 4+, vous pouvez utiliser le raccourci `&>` pour tout rediriger vers un seul fichier :
```bash
/opt/scripts/backup.sh &> log_complet.txt
```

## Le trou noir : `/dev/null`

`/dev/null` est un fichier spécial sous Linux qui détruit toutes les données qu'on lui envoie. C'est l'outil idéal pour "faire taire" une commande.

Ignorer les erreurs gênantes (comme les fameux "Permission non accordée" avec `find`) :
```bash
find / -name "mon_fichier.conf" 2> /dev/null
```

Ignorer toute la sortie (pour qu'une commande tourne de manière totalement silencieuse) :
```bash
apt-get update &> /dev/null
```

## Ce qu'il faut retenir

- `>` ou `1>` : Redirige la sortie standard en écrasant le fichier.
- `>>` : Redirige la sortie standard en ajoutant au fichier.
- `2>` : Redirige uniquement la sortie d'erreur.
- `2>&1` ou `&>` : Combine sortie standard et erreur.
- `/dev/null` : Supprime les sorties indésirables.

La maîtrise de ces opérateurs est une étape clé pour passer du statut de simple utilisateur à celui de futur administrateur système. N'hésitez pas à tester ces commandes en laboratoire ou sur une VM (virtuelle) pour bien visualiser leur comportement !
