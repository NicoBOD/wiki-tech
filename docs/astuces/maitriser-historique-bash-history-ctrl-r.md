---
title: Maîtriser l'historique Bash avec history et Ctrl+R
date: 2026-06-07
author: Nicolas BODAINE
tags:
  - bash
  - terminal
  - linux
  - productivité
  - astuces
difficulty: débutant
os: Linux
status: publié
---

# Maîtriser l'historique Bash avec history et Ctrl+R

!!! abstract "Résumé"
    Sous Linux, la ligne de commande garde en mémoire les commandes que vous avez tapées. Savoir rechercher et réutiliser rapidement ces commandes avec `history` et le raccourci `Ctrl+R` permet de gagner un temps précieux et d'éviter les erreurs de frappe.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Débutant |
| OS / Environnement | Linux (Bash) |
| Dernière mise à jour | 2026-06-07 |

## Contexte

Lorsque l'on administre un système ou que l'on travaille régulièrement dans un terminal, on tape souvent des commandes longues ou complexes (par exemple des commandes `docker`, des connexions `ssh` avec des clés spécifiques, ou des filtres `grep` compliqués).
Plutôt que de retaper ou de copier-coller ces commandes, Bash offre un système d'historique intégré très puissant.

## L'historique de base : la commande `history`

La commande `history` affiche la liste numérotée de vos dernières commandes.

### Afficher l'historique récent

```bash
history | tail -n 10
```

### Relancer une commande spécifique

Chaque commande possède un numéro. Pour relancer la commande numéro `42` de votre historique, utilisez un point d'exclamation suivi du numéro :

```bash
!42
```

### Relancer la toute dernière commande

Le raccourci `!!` relance exactement la dernière commande tapée. C'est extrêmement utile lorsque vous avez oublié le `sudo` :

```bash
apt install nginx
# Erreur : Permission denied
sudo !!
```
*(Cela exécutera `sudo apt install nginx`)*

## La recherche interactive (Reverse-i-search)

C'est la méthode la plus rapide et la plus utilisée par les administrateurs système.

### Étape 1 : Lancer la recherche

Dans votre terminal, appuyez simultanément sur :
++ctrl+r++

Votre invite de commande se transforme en :
`(reverse-i-search)\`': `

### Étape 2 : Taper les mots clés

Commencez à taper un fragment de la commande que vous cherchez (par exemple `ssh`). Bash va afficher la commande la plus récente contenant ce fragment.

### Étape 3 : Naviguer dans les résultats

Si la commande proposée n'est pas la bonne, appuyez à nouveau sur ++ctrl+r++ pour remonter plus loin dans l'historique, jusqu'à trouver la bonne commande.

### Étape 4 : Exécuter ou modifier

- **Exécuter** : Appuyez sur ++enter++ pour la lancer immédiatement.
- **Modifier** : Appuyez sur la flèche de droite ++arrow-right++ pour quitter la recherche, modifier la commande, puis l'exécuter.

## Aide-mémoire

| Commande / Raccourci | Description |
|-------------------|-------------|
| `history` | Affiche l'historique complet des commandes |
| `history -c` | Efface l'historique de la session courante |
| `!numero` | Exécute la commande correspondant à ce numéro |
| `!!` | Répète la dernière commande tapée |
| `!mot` | Exécute la dernière commande commençant par "mot" |
| ++ctrl+r++ | Recherche interactive inversée dans l'historique |
| ++ctrl+c++ | Annule la recherche en cours |

## Vérification

1. Tapez une commande arbitraire : `echo "Test historique"`
2. Tapez une autre commande : `ls -l`
3. Faites ++ctrl+r++ et tapez `Test`. Bash doit vous proposer `echo "Test historique"`.
4. Appuyez sur ++enter++.

!!! success "Résultat attendu"
    La commande `echo "Test historique"` s'exécute et affiche "Test historique" dans le terminal.

## Ressources

- [Manuel de GNU Bash (History)](https://www.gnu.org/software/bash/manual/bash.html#Bash-History-Facilities) — Documentation officielle.