---
title: Déboguer une application Python avec pdb en ligne de commande
date: 2026-06-18
author: Nicolas BODAINE
tags:
  - python
  - debug
  - pdb
  - cli
difficulty: intermédiaire
os: Linux | Windows | macOS
status: publié
---

# Déboguer une application Python avec pdb en ligne de commande

!!! abstract "Résumé"
    Apprenez à utiliser `pdb` (Python Debugger), l'outil natif de Python, pour inspecter le comportement d'un script en cours d'exécution. Mettre le code en pause, examiner les variables pas à pas et trouver l'origine d'un bug sans avoir à truffer votre code de `print()`.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Intermédiaire |
| OS / Environnement | Linux, Windows, macOS |
| Dernière mise à jour | 2026-06-18 |

## Contexte

Lorsque votre script Python a un comportement inattendu ou produit une erreur, la technique classique (mais laborieuse) consiste à ajouter de multiples `print()` pour afficher l'état des variables. 

L'outil **`pdb`** (Python Debugger) offre une approche beaucoup plus puissante. Intégré nativement à la bibliothèque standard Python, il permet de suspendre l'exécution d'un programme, d'exécuter le code ligne par ligne et d'inspecter l'état de la mémoire à n'importe quel moment. Étant disponible partout, il est inestimable, surtout sur des serveurs distants sans interface graphique (CLI) où un IDE classique n'est pas accessible.

## Prérequis

- Un système avec **Python 3.x** installé.
- Un terminal (bash, zsh, powershell...).
- Un script Python contenant un bug ou un comportement à inspecter.

## Préparer l'environnement de test

Pour comprendre l'utilisation de `pdb`, nous allons créer un petit script qui contient un bug logique (une division par zéro potentielle cachée).

Créez un fichier `calcul.py` avec le code suivant :

```python title="calcul.py" linenums="1"
def calculer_moyenne(valeurs):
    total = sum(valeurs)
    compte = len(valeurs)
    
    # Bug potentiel si la liste est vide
    moyenne = total / compte 
    return moyenne

def main():
    listes = [
        [10, 20, 30],
        [5, 15],
        [],           # Cette liste vide va provoquer une erreur !
        [100, 200]
    ]

    for index, data in enumerate(listes):
        resultat = calculer_moyenne(data)
        print(f"Moyenne de la liste {index} : {resultat}")

if __name__ == "__main__":
    main()
```

Si vous exécutez ce script via `python3 calcul.py`, vous obtiendrez l'erreur suivante :

!!! failure "ZeroDivisionError"
    ```text
    Moyenne de la liste 0 : 20.0
    Moyenne de la liste 1 : 10.0
    Traceback (most recent call last):
      File "calcul.py", line 22, in <module>
        main()
      File "calcul.py", line 18, in main
        resultat = calculer_moyenne(data)
      File "calcul.py", line 6, in calculer_moyenne
        moyenne = total / compte
    ZeroDivisionError: division by zero
    ```

Nous voyons où le script a échoué, mais avec un programme plus complexe, il serait utile de l'inspecter juste avant qu'il ne plante.

## Procédure : Lancer et utiliser le débogueur

Il existe deux principales manières de démarrer `pdb`. 

### Méthode 1 : Lancer le script via pdb (Sans modifier le code)

C'est la méthode la plus rapide pour auditer un script de l'extérieur. Dans votre terminal, lancez le script en l'appelant avec le module `pdb` :

```bash
python3 -m pdb calcul.py
```

Le script démarre en pause, à la toute première ligne. Le prompt `(Pdb)` apparaît, indiquant que le débogueur attend vos instructions.

```text
> /chemin/vers/calcul.py(1)<module>()
-> def calculer_moyenne(valeurs):
(Pdb) 
```

### Méthode 2 : Ajouter un point d'arrêt dans le code (Breakpoint)

Depuis Python 3.7, vous pouvez utiliser la fonction native `breakpoint()` pour indiquer exactement où l'exécution doit se suspendre. 

Modifiez le fichier `calcul.py` pour ajouter `breakpoint()` juste avant l'appel à la fonction :

```python hl_lines="17"
# ... [code précédent] ...
    for index, data in enumerate(listes):
        breakpoint()  # <-- Le script se mettra en pause ici
        resultat = calculer_moyenne(data)
        print(f"Moyenne de la liste {index} : {resultat}")
# ... [suite du code] ...
```

Lancez maintenant le script normalement :

```bash
python3 calcul.py
```

Le script s'exécute jusqu'au moment où il rencontre `breakpoint()`, puis vous rend la main :

```text
> /chemin/vers/calcul.py(18)main()
-> resultat = calculer_moyenne(data)
(Pdb)
```

## Naviguer dans le code

Une fois le prompt `(Pdb)` affiché, vous pouvez utiliser les commandes suivantes pour contrôler l'exécution.

### Afficher le contexte (`l` ou `ll`)

Pour savoir où vous vous trouvez exactement, tapez `l` (list) pour voir 11 lignes autour de votre position actuelle, ou `ll` (longlist) pour afficher la fonction complète.

```text
(Pdb) ll
 10     def main():
 11         listes = [
 12             [10, 20, 30],
 13             [5, 15],
 14             [],           # Cette liste vide va provoquer une erreur !
 15             [100, 200]
 16         ]
 17  
 18         for index, data in enumerate(listes):
 19             breakpoint()
 20  ->         resultat = calculer_moyenne(data)
 21             print(f"Moyenne de la liste {index} : {resultat}")
```
*(La flèche `->` indique la ligne qui **va être** exécutée).*

### Inspecter les variables (Taper leur nom ou `p`)

Pour voir le contenu d'une variable à cet instant précis, tapez simplement son nom ou utilisez `p` (print) :

```text
(Pdb) data
[10, 20, 30]
(Pdb) index
0
```

Vous pouvez même exécuter de vraies expressions Python :
```text
(Pdb) len(data)
3
```

### Avancer pas à pas : `n` (next) vs `s` (step)

- **`n` (next)** exécute la ligne actuelle et passe à la suivante dans la fonction courante. Elle n'entre *pas* à l'intérieur des appels de fonction.
- **`s` (step)** exécute la ligne et *plonge* à l'intérieur de toute fonction qui y est appelée.

Puisque nous sommes sur la ligne `resultat = calculer_moyenne(data)`, tapons **`s`** pour entrer dans `calculer_moyenne` :

```text
(Pdb) s
--Call--
> /chemin/vers/calcul.py(1)calculer_moyenne()
-> def calculer_moyenne(valeurs):
```

Tapons ensuite **`n`** plusieurs fois pour avancer à travers cette fonction :

```text
(Pdb) n
> /chemin/vers/calcul.py(2)calculer_moyenne()
-> total = sum(valeurs)
(Pdb) n
> /chemin/vers/calcul.py(3)calculer_moyenne()
-> compte = len(valeurs)
(Pdb) n
> /chemin/vers/calcul.py(6)calculer_moyenne()
-> moyenne = total / compte
```

Nous sommes à présent juste avant la division.

### Continuer l'exécution : `c` (continue)

Pour laisser le programme reprendre son exécution normale jusqu'à la fin ou jusqu'au prochain point d'arrêt, tapez **`c`**.

Puisque nous sommes dans une boucle, le programme va s'exécuter, afficher le résultat de la première liste, et s'arrêter au `breakpoint()` au tour de boucle suivant :

```text
(Pdb) c
Moyenne de la liste 0 : 20.0
> /chemin/vers/calcul.py(18)main()
-> resultat = calculer_moyenne(data)
```

## Aide-mémoire interactif pdb

Voici un résumé des commandes indispensables de `pdb`. 

!!! tip "Raccourci"
    Appuyer sur ++enter++ sans rien taper répète la dernière commande `pdb` saisie. Très pratique pour enchaîner les `n` (next).

| Commande | Description |
|----------|-------------|
| `l` (list) / `ll` (longlist) | Affiche le code source autour de la position actuelle. |
| `n` (next) | Exécute la ligne courante et passe à la suivante. |
| `s` (step) | Exécute la ligne courante et *entre* dans les appels de fonctions. |
| `c` (continue) | Reprend l'exécution jusqu'au prochain arrêt. |
| `r` (return) | Continue l'exécution jusqu'à la fin de la fonction courante (jusqu'au `return`). |
| `unt` (until) | Exécute jusqu'à une ligne supérieure à l'actuelle (utile pour sortir d'une boucle `for` ou `while`). |
| `p variable` | Évalue et affiche la valeur de `variable`. |
| `w` (where) | Affiche la pile d'appels complète (Call Stack) montrant comment vous êtes arrivé là. |
| `q` (quit) | Quitte brusquement le débogueur (arrête le script). |
| `h` (help) | Affiche la liste complète des commandes. |

## Post-mortem : Inspecter un script APRÈS qu'il ait planté

Parfois, un script plante de façon intermittente, et il est difficile de savoir *où* mettre le `breakpoint()`. `pdb` offre un mode d'analyse "post-mortem" inestimable.

Retirez le `breakpoint()` de votre fichier `calcul.py`.

Lancez le script avec l'argument spécial `-c continue` de pdb. Cela va exécuter le programme normalement. S'il ne rencontre pas d'erreur, il se termine. Mais s'il lève une exception non gérée, il s'interrompt et **ouvre le débogueur exactement à l'endroit du crash, avec l'état de la mémoire figé au moment de l'erreur**.

```bash
python3 -m pdb -c continue calcul.py
```

Résultat :
```text
Moyenne de la liste 0 : 20.0
Moyenne de la liste 1 : 10.0
Traceback (most recent call last):
  File "/usr/lib/python3.12/pdb.py", line 1801, in main
    pdb._runscript(mainpyfile)
  [...]
  File "/chemin/vers/calcul.py", line 6, in calculer_moyenne
    moyenne = total / compte
ZeroDivisionError: division by zero
Uncaught exception. Entering post mortem debugging
Running 'cont' or 'step' will restart the program
> /chemin/vers/calcul.py(6)calculer_moyenne()
-> moyenne = total / compte
(Pdb) 
```

Nous pouvons inspecter la situation :

```text
(Pdb) p total
0
(Pdb) p compte
0
(Pdb) p valeurs
[]
```

Le coupable est clairement identifié : on tente de faire une division avec `compte = 0` car la liste `valeurs` est vide. La correction du bug devient évidente !

## Ressources

- [Documentation officielle Python - Pdb](https://docs.python.org/fr/3/library/pdb.html) — Référence complète de toutes les fonctionnalités et commandes.
- [Real Python - Python Debugging With Pdb](https://realpython.com/python-debugging-pdb/) — Guide détaillé en anglais pour aller plus loin.
