---
title: Naviguer plus vite dans ses dossiers Linux avec pushd et popd
date: 2026-06-08
author: Nicolas BODAINE
tags:
  - linux
  - terminal
  - bash
  - productivité
  - astuce
difficulty: débutant
os: Linux / macOS
status: publié
---

# Naviguer plus vite dans ses dossiers Linux avec pushd et popd

!!! abstract "Résumé"
    Oubliez les longs `cd /chemin/absolu/tres/long` à répétition ! Découvrez les commandes `pushd`, `popd` et `dirs` qui permettent de mémoriser vos chemins de répertoires sous forme de pile (stack) pour revenir instantanément en arrière ou jongler entre plusieurs dossiers.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux / macOS (Bash/Zsh) |
| Dernière mise à jour | 2026-06-08 |

## Contexte

Lorsque l'on administre un serveur ou que l'on développe en local, il est fréquent de devoir naviguer entre différents répertoires éloignés. 

Par exemple, vous modifiez une configuration dans `/etc/nginx/sites-available/`, puis vous devez aller dans `/var/log/nginx/` pour lire les logs, et enfin retourner dans `/etc/nginx/sites-available/` pour corriger l'erreur.

La méthode classique consiste à utiliser `cd` (Change Directory) avec des chemins absolus ou un `cd -` (qui ne retient que le dernier dossier). Mais que faire si vous jonglez entre 3 ou 4 dossiers ? C'est là que `pushd` et `popd` entrent en jeu.

## Le concept de pile (Stack)

Imaginez une pile d'assiettes. Vous pouvez ajouter une assiette sur le dessus (push) ou retirer l'assiette du dessus (pop).

Dans Bash/Zsh, vos répertoires peuvent fonctionner exactement de la même manière :

- **`pushd`** (Push Directory) : Sauvegarde le répertoire actuel sur la pile et vous déplace dans le nouveau répertoire.
- **`popd`** (Pop Directory) : Vous ramène au dernier répertoire sauvegardé en haut de la pile (en le retirant de la liste).
- **`dirs`** (Directories) : Affiche la liste des répertoires actuellement dans la pile.

## Procédure

### Étape 1 : Sauvegarder un dossier et se déplacer avec `pushd`

Pour vous déplacer tout en mémorisant d'où vous venez, remplacez `cd` par `pushd` :

```bash
# Je suis dans mon dossier personnel
utilisateur@machine:~$ pushd /var/log/
/var/log ~

# Je suis maintenant dans /var/log, et la commande m'affiche la pile actuelle :
utilisateur@machine:/var/log$ pushd /etc/nginx/
/etc/nginx /var/log ~
```

La console affiche la pile de gauche à droite : le dossier actuel est à gauche (`/etc/nginx`), suivi du précédent (`/var/log`), puis du répertoire personnel (`~`).

### Étape 2 : Consulter la pile avec `dirs`

À tout moment, vous pouvez voir quels dossiers sont mémorisés grâce à `dirs`. L'option `-v` est très pratique car elle liste les répertoires verticalement avec leur index.

```bash
utilisateur@machine:/etc/nginx$ dirs -v
 0  /etc/nginx
 1  /var/log
 2  ~
```

### Étape 3 : Revenir en arrière avec `popd`

Une fois votre travail terminé dans `/etc/nginx`, vous voulez revenir au dossier précédent (`/var/log`). Utilisez simplement `popd` (sans argument) :

```bash
utilisateur@machine:/etc/nginx$ popd
/var/log ~

utilisateur@machine:/var/log$ pwd
/var/log
```

La commande `popd` vous a ramené dans `/var/log` et a retiré `/etc/nginx` de la pile.

### Étape 4 : Naviguer vers un dossier spécifique de la pile

Si votre pile contient plusieurs dossiers, vous n'êtes pas obligé de faire `popd` plusieurs fois. Vous pouvez vous déplacer directement vers un dossier précis en utilisant `pushd +N` ou `pushd -N`.

Admettons la pile suivante :
```bash
utilisateur@machine:/var/www/html$ dirs -v
 0  /var/www/html
 1  /etc/apache2
 2  /var/log/apache2
 3  ~
```

Pour aller directement dans `/var/log/apache2` (index 2), tapez :

```bash
utilisateur@machine:/var/www/html$ pushd +2
/var/log/apache2 ~ /var/www/html /etc/apache2
```

!!! note "Rotation de la pile"
    L'utilisation de `pushd +N` ne fait pas que vous déplacer, elle effectue une **rotation** de la pile. Le répertoire ciblé devient le numéro 0, et les autres tournent en boucle.

## Aide-mémoire

| Commande | Description |
|----------|-------------|
| `pushd /chemin` | Va dans `/chemin` et sauvegarde le dossier précédent. |
| `popd` | Revient au dernier dossier sauvegardé (et le retire de la pile). |
| `dirs -v` | Affiche la pile des répertoires numérotés verticalement. |
| `dirs -c` | Vide la pile (efface l'historique mémorisé). |
| `pushd +N` | Fait une rotation de la pile pour mettre l'élément N en haut et s'y déplace. |

## Ressources

- [GNU Bash Reference Manual - Directory Stack Builtins](https://www.gnu.org/software/bash/manual/html_node/Directory-Stack-Builtins.html) — Documentation officielle du shell GNU Bash.
